import traceback
from shapely.geometry import Point
from exeris.core.deferred import convert
from exeris.core import deferred
from exeris.core import main
from exeris.core.main import db, Events
from exeris.core import models
from exeris.core import general
from exeris.core.general import SameLocationRange, EventCreator, VisibilityBasedRange
from exeris.core.properties import P

__author__ = 'alek'


class AbstractAction:  # top level, we don't assume anything

    def perform(self):
        self.perform_action()

    def perform_action(self):
        pass


class Action(AbstractAction):  # top level character action, where we only know that it's done by a character

    def __init__(self, executor):
        self.executor = executor


# rich collection of pre-configured actions
class ActionOnSelf(Action):
    def __init__(self, executor, rng=None):
        super().__init__(executor)
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange()


class ActionOnItem(Action):
    def __init__(self, executor, item, rng=None):
        super().__init__(executor)
        self.item = item
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange()


class ActionOnLocation(Action):
    def __init__(self, executor, location, rng=None):
        super().__init__(executor)
        self.location = location
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange()


class ActionOnActivity(Action):
    def __init__(self, executor, activity, rng=None):
        super().__init__(executor)
        self.activity = activity
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange()


class ActionOnItemAndActivity(Action):
    def __init__(self, executor, item, activity, rng=None):
        super().__init__(executor)
        self.item = item
        self.activity = activity
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange()


class ActionOnItemAndCharacter(Action):
    def __init__(self, executor, item, character, rng=None):
        super().__init__(executor)
        self.item = item
        self.character = character
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange()


####################
# ACTIVITY ACTIONS #
####################

class ActivityAction(AbstractAction):
    pass


def form_on_setup(**kwargs):  # adds a field "_form_input" to a class so it can be later used
    def f(clazz):
        clazz._form_inputs = kwargs
        return clazz
    return f


class CreateItemAction(ActivityAction):

    @convert(item_type=models.ItemType)
    def __init__(self, *, item_type, properties, used_materials, amount=1, visible_material=None, **injected_args):
        self.item_type = item_type
        self.activity = injected_args["activity"]
        self.initiator = injected_args["initiator"]
        self.amount = amount
        self.used_materials = used_materials
        self.kwargs = injected_args
        self.properties = properties
        self.visible_material = visible_material if visible_material else {}

    def perform_action(self):

        result_loc = self.activity.being_in.being_in
        if self.item_type.portable and self.initiator.being_in == result_loc:  # if being in the same location then go to inventory
            result_loc = self.initiator

        new_item_weight = self.amount * self.item_type.unit_weight
        new_item = models.Item(self.item_type, result_loc, weight=new_item_weight)

        db.session.add(new_item)

        for property_name in self.properties:
            db.session.add(models.EntityProperty(new_item, property_name, self.properties[property_name]))

        if self.used_materials == "all": # all the materials used for an activity were set to build this item
            for material_type in models.Item.query.filter(models.Item.is_used_for(self.activity)).all():
                material_type.used_for = new_item
        else:  # otherwise it's a dict and we need to look into it
            for material_type_name in self.used_materials:
                self.extract_used_material(material_type_name, new_item)

        if self.visible_material:
            visible_material_property = {}
            for place_to_show in self.visible_material:
                group_name = self.visible_material[place_to_show]
                req_input = self.activity.requirements["input"]
                for req_material_name, req_material in req_input.items():  # forall requirements
                    real_used_type_name = req_material["used_type"]
                    if group_name == req_material_name:  # this group is going to be shown by our visible material
                        visible_material_property[place_to_show] = real_used_type_name
            db.session.add(models.EntityProperty(new_item, P.VISIBLE_MATERIAL, visible_material_property))

    def extract_used_material(self, material_type_name, new_item):
        for req_material_name, requirement_params in self.activity.requirements.get("input",
                {}).items():  # forall requirements
            req_used_type_name = requirement_params["used_type"]
            if req_material_name == material_type_name:  # req is fulfilled by material
                real_material_type = models.ItemType.by_name(req_used_type_name)
                required_material_type = models.EntityType.by_name(req_material_name)

                amount = requirement_params["needed"] / required_material_type.efficiency(real_material_type)

                item = models.Item.query.filter_by(type=real_material_type).one()
                move_between_entities(item, item.used_for, new_item, amount, to_be_used_for=True)


class RemoveItemAction(ActivityAction):

    @convert(item=models.Item)
    def __init__(self, item, gracefully=True):
        self.item = item
        self.gracefully = gracefully

    def perform_action(self):
        self.item.remove(self.gracefully)


@form_on_setup(item_name=deferred.NameInput)
class AddNameToItemAction(ActivityAction):

    @convert(item=models.Item)
    def __init__(self, *, item, item_name):
        pass

##############################
#      SCHEDULER ACTIONS     #
##############################


class ProcessAction(AbstractAction):
    pass


class TravelProcess(ProcessAction):

    def __init__(self):
        pass

    def perform_action(self):
        mobile_locs = models.RootLocation.query.filter_by(is_mobile=True).all()
        for loc in mobile_locs:
            pos = loc.position
            point = Point(pos.x + 1, pos.y + 1)
            loc.position = point


class ActivitiesProgressProcess(ProcessAction):

    def __init__(self):
        pass

    def perform_action(self):
        activities = models.Activity.query.all()
        for activity in activities:
            activity_progress = ActivityProgressProcess(activity)
            activity_progress.perform()


class ActivityProgressProcess(ProcessAction):

    def __init__(self, activity):
        self.activity = activity
        self.entity_worked_on = self.activity.being_in
        self.affect_quality_sum = 0.0
        self.affect_quality_ticks = 0
        self.progress_ratio = 1.0

    def perform_action(self):
        print("progress of ", self.activity)
        workers = models.Character.query.filter_by(activity=self.activity).all()

        try:
            req = self.activity.requirements

            if "max_people" in req:
                pass

            if "min_people" in req:
                pass

            if "mandatory_machines" in req:
                self.check_mandatory_machines(req["mandatory_machines"])

            if "optional_machines" in req:
                pass

            if "target" in req:
                pass

            if "target_with_properties" in req:
                pass

            for worker in workers:
                print("worker ", worker)
                self.check_proximity(self.activity, worker)

                if "input" in req:
                    self.check_input_requirements(req["input"])

                if "mandatory_tools" in req:
                    self.check_mandatory_tools(worker, req["mandatory_tools"])

                if "optional_tools" in req:
                    self.check_optional_tools(worker, req["optional_tools"])

                if "skill" in req:
                    pass

                self.activity.ticks_left -= 1

            self.activity.quality_sum += self.affect_quality_sum  # todo it does add quality of chars which have only part of mandatory tools
            self.activity.quality_ticks += self.affect_quality_ticks


        except Exception as e:
            print(traceback.format_exc())

        if self.activity.ticks_left <= 0:
            self.finish_activity(self.activity)

    def check_proximity(self, activity, worker):
        rng = general.SameLocationRange()

        if not worker.has_access(activity, rng=rng):
            raise main.TooFarFromActivityException(activity=activity)

    def check_input_requirements(self, materials):
        for name, material in materials.items():
            if material["left"] > 0:
                raise main.NoInputMaterialException(item_type=models.EntityType.by_name(name))

    def check_mandatory_tools(self, worker, tools):
        for tool_type_name in tools:
            group = models.EntityType.by_name(tool_type_name)
            type_eff_pairs = group.get_descending_types()
            allowed_types = [pair[0] for pair in type_eff_pairs]
            type_efficiency = {pair[0]: pair[1] for pair in type_eff_pairs}

            tools = general.ItemQueryHelper.all_of_types_in(allowed_types, worker).all()
            if not tools:
                raise main.NoToolForActivityException(tool_name=group.name)  # TODO name or object

            sorted_by_quality = sorted(tools, key=lambda item: type_efficiency[item.type] * item.quality, reverse=True)

            self.affect_quality_sum += type_efficiency[sorted_by_quality[0].type] * sorted_by_quality[0].quality
            self.affect_quality_ticks += 1

    def check_optional_tools(self, worker, tools_progress_bonus):
        for tool_type_name in tools_progress_bonus:
            print(tool_type_name)
            group = models.EntityType.by_name(tool_type_name)
            type_eff_pairs = group.get_descending_types()
            allowed_types = [pair[0] for pair in type_eff_pairs]
            type_efficiency = {pair[0]: pair[1] for pair in type_eff_pairs}

            tools = general.ItemQueryHelper.all_of_types_in(allowed_types, worker).all()
            if not tools:
                continue

            sorted_by_quality = sorted(tools, key=lambda item: type_efficiency[item.type] * item.quality, reverse=True)
            self.affect_quality_sum += type_efficiency[sorted_by_quality[0].type] * sorted_by_quality[0].quality
            self.affect_quality_ticks += 1

            # TODO should quality affect also progress? or maybe only progress, so worse optional tool won't harm the result quality?
            self.progress_ratio += tools_progress_bonus[tool_type_name]


    def check_mandatory_machines(self, machines):
        for machine_name in machines:
            group = models.EntityType.by_name(machine_name)
            type_eff_pairs = group.get_descending_types()
            allowed_types = [pair[0] for pair in type_eff_pairs]

            if not general.ItemQueryHelper.all_of_types_in(allowed_types, self.entity_worked_on.being_in).count():
                raise main.NoMachineForActivityException(machine_name=group.name)  # TODO name or object

    def finish_activity(self, activity):
        print("finishing activity")
        for serialized_action in activity.result_actions:
            action = deferred.call(serialized_action, activity=activity, initiator=activity.initiator)
            action.perform()


#

##############################
# CHARACTER-SPECIFIC ACTIONS #
##############################

def move_between_entities(item, source, destination, amount, to_be_used_for=False):

    if item.parent_entity == source:
        if item.type.stackable:
            weight = amount * item.type.unit_weight
            move_stackable_resource(item, source, destination, weight, to_be_used_for)
        elif to_be_used_for:
            item.used_for = destination
        else:
            item.being_in = destination
    else:
        raise main.InvalidInitialLocationException(entity=item)


def move_stackable_resource(item, source, goal, weight, to_be_used_for=False):
    # remove from the source
    if item.weight == weight:
        item.remove()
    else:
        item.weight -= weight

    # add to the goal
    if to_be_used_for:
        existing_pile = models.Item.query.filter_by(type=item.type)\
            .filter(models.Item.is_used_for(goal)).filter_by(visible_parts=item.visible_parts).first()
    else:
        existing_pile = models.Item.query.filter_by(type=item.type).\
            filter(models.Item.is_in(goal)).filter_by(visible_parts=item.visible_parts).first()

    if existing_pile:
        existing_pile.weight += weight
    else:
        new_pile = models.Item(item.type, goal, weight=weight, role_being_in=not to_be_used_for)
        new_pile.visible_parts = item.visible_parts
        db.session.add(new_pile)


def overwrite_item_amount(item, amount):
    if item.type.stackable:
        return dict(item_amount=amount)
    return {}


class DropItemAction(ActionOnItem):

    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        self.amount = amount

    def perform_action(self):
        if self.item.being_in != self.executor:
            raise main.EntityNotInInventoryException(entity=self.item)

        if self.amount > self.item.amount:
            raise main.InvalidAmountException(amount=self.amount)

        move_between_entities(self.item, self.executor, self.executor.being_in, self.amount)

        event_args = self.item.pyslatize(**overwrite_item_amount(self.item, self.amount))

        EventCreator.base(Events.DROP_ITEM, self.rng, event_args, self.executor)


class TakeItemAction(ActionOnItem):
    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        self.amount = amount

    def perform_action(self):
        if self.item.being_in != self.executor.being_in:
            raise main.EntityTooFarAwayException(entity=self.item)

        if self.amount > self.item.amount:
            raise Exception

        move_between_entities(self.item, self.executor.being_in, self.executor, self.amount)

        event_args = self.item.pyslatize(**overwrite_item_amount(self.item, self.amount))
        EventCreator.base(Events.TAKE_ITEM, self.rng, event_args, self.executor)


class GiveItemAction(ActionOnItemAndCharacter):
    def __init__(self, executor, item, receiver, amount=1):
        super().__init__(executor, item, receiver)
        self.amount = amount

    def perform_action(self):
        if self.item.being_in != self.executor.being_in:
            raise main.EntityNotInInventoryException(entity=self.item)

        if self.amount > self.item.amount:
            raise main.InvalidAmountException(amount=self.amount)

        if not self.character:  # has not enough space in inventory
            raise main.OwnInventoryExceededException()

        move_between_entities(self.item, self.executor, self.character, self.amount)

        event_args = self.item.pyslatize(**overwrite_item_amount(self.item, self.amount))
        EventCreator.base(Events.GIVE_ITEM, self.rng, event_args,
                          self.executor, self.character)


class AddItemToActivityAction(ActionOnItemAndActivity):

    def __init__(self, executor, item, activity, amount):
        super().__init__(executor, item, activity)
        self.amount = amount

    def perform_action(self):

        if self.item.being_in != self.executor:
            raise main.EntityNotInInventoryException(entity=self.item)

        if self.amount > self.item.amount:
            raise main.InvalidAmountException(amount=self.amount)

        req = self.activity.requirements

        for required_group_name, required_group_params in sorted(req.get("input", {}).items()):
            required_group = models.EntityType.by_name(required_group_name)
            if "used_type" in required_group_params:
                    if required_group_params["used_type"] != self.item.type_name:  # must be exactly the same type
                        raise main.OnlySpecificTypeForGroupException(
                            type_name=required_group_params["used_type"], group_name=required_group_name)
            if required_group_params["left"] == 0:  # this requirement is fulfilled
                continue
            if not required_group.contains(self.item.type):  # requirement cannot be fulfilled by this type
                continue
            type_efficiency_ratio = required_group.efficiency(self.item.type)
            max_to_be_added = required_group_params["left"] / type_efficiency_ratio
            amount_to_add = min(self.amount, max_to_be_added)
            move_between_entities(self.item, self.executor, self.activity, amount_to_add, to_be_used_for=True)

            material_left_reduction = amount_to_add * type_efficiency_ratio

            required_group_params["left"] -= material_left_reduction
            required_group_params["used_type"] = self.item.type_name

            overwrites = {}
            if self.item.type.stackable:
                overwrites["item_amount"] = amount_to_add

            item_info = self.item.pyslatize(**overwrite_item_amount(self.item, amount_to_add))
            event_args = {"groups": {
                "item": item_info,
                "activity": self.activity.pyslatize()
            }}
            EventCreator.base(Events.ADD_TO_ACTIVITY, self.rng, event_args, doer=self.executor)
            return

        raise main.ItemNotApplicableForActivityException(item=self.item, activity=self.activity)


class SayAloudAction(ActionOnSelf):

    def __init__(self, executor, message):
        super().__init__(executor, rng=VisibilityBasedRange(20))
        self.message = message

    def perform_action(self):

        EventCreator.base(Events.SAY_ALOUD, self.rng, {"message": self.message}, doer=self.executor)