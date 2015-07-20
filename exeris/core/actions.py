from exeris.core.deferred import convert
from exeris.core import deferred
from exeris.core.main import db
from exeris.core import models

from exeris.core.general import SameLocationRange, EventCreator
from exeris.core.properties import P

__author__ = 'alek'


class AbstractAction:  # top level, we don't assume anything

    def perform(self):
        self.perform_action()


class Action(AbstractAction):  # top level character action, where we only know that it's done by a character

    def __init__(self, executor):
        self.executor = executor


# rich collection of pre-configured actions
class ActionOnSelf(Action):
    def __init__(self, executor):
        super().__init__(executor)


class ActionOnItem(Action):

    def __init__(self, executor, item, rng=None):
        super().__init__(executor)
        self.item = item
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange(executor.being_in)


class ActionOnLocation(Action):
    def __init__(self, executor, location, rng=None):
        super().__init__(executor)
        self.location = location
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange(executor.being_in)


class ActionOnActivity(Action):
    def __init__(self, executor, activity, rng=None):
        super().__init__(executor)
        self.activity = activity
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange(executor.being_in)


class ActionOnItemAndActivity(Action):
    def __init__(self, executor, item, activity, rng=None):
        super().__init__(executor)
        self.item = item
        self.activity = activity
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange(executor.being_in)


class ActionOnItemAndCharacter(Action):
    def __init__(self, executor, item, character, rng=None):
        super().__init__(executor)
        self.item = item
        self.character = character
        self.rng = rng
        if not rng:
            self.rng = SameLocationRange(executor.being_in)


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
        raise Exception


def move_stackable_resource(item, source, goal, weight, to_be_used_for=False):
    # remove from the source
    if item.weight == weight:
        item.remove()
    else:
        item.weight -= weight

    # add to the goal
    if to_be_used_for:
        existing_pile = models.Item.query.filter_by(type=item.type).\
            filter(models.Item.is_used_for(goal)).filter_by(visible_parts=item.visible_parts).first()
    else:
        existing_pile = models.Item.query.filter_by(type=item.type).\
            filter(models.Item.is_in(goal)).filter_by(visible_parts=item.visible_parts).first()

    if existing_pile:
        existing_pile.weight += weight
    else:
        new_pile = models.Item(item.type, goal, weight=weight, role_being_in=not to_be_used_for)
        new_pile.visible_parts = item.visible_parts
        db.session.add(new_pile)


class DropItemAction(ActionOnItem):

    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        self.amount = amount

    def perform_action(self):
        if self.item.being_in != self.executor:
            raise Exception

        if self.amount > self.item.amount:
            raise Exception

        move_between_entities(self.item, self.executor, self.executor.being_in, self.amount)

        if self.item.type.stackable:
            EventCreator.base("event_drop_part_of_item", self.rng, {"item_id": self.item.id, "item_name": self.item.type.name}, self.executor)
        else:
            EventCreator.base("event_drop_item", self.rng, {"item_id": self.item.id, "item_name": self.item.type.name}, self.executor)


class TakeItemAction(ActionOnItem):
    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        self.amount = amount

    def perform_action(self):
        if self.item.being_in != self.executor.being_in:
            raise Exception

        if self.amount > self.item.amount:
            raise Exception

        move_between_entities(self.item, self.executor.being_in, self.executor, self.amount)

        if self.item.type.stackable:
            EventCreator.base("event_take_part_of_item", self.rng, {"item_id": self.item.id, "item_name": self.item.type_name}, self.executor)
        else:
            EventCreator.base("event_take_item", self.rng, {"item_id": self.item.id, "item_name": self.item.type_name}, self.executor)


class GiveItemAction(ActionOnItemAndCharacter):
    def __init__(self, executor, item, receiver, amount=1):
        super().__init__(executor, item, receiver)
        self.amount = amount

    def perform_action(self):
        if self.item.being_in != self.executor.being_in:
            raise Exception

        if self.amount > self.item.amount:
            raise Exception

        if not self.character:  # has not enough space in inventory
            raise Exception

        move_between_entities(self.item, self.executor, self.character, self.amount)

        if self.item.type.stackable:
            EventCreator.base("event_give_part_of_item", self.rng, {"item_id": self.item.id, "item_name": self.item.type_name}, self.executor)
        else:
            EventCreator.base("event_give_item", self.rng, {"item_id": self.item.id, "item_name": self.item.type_name}, self.executor)


class AddItemToActivity(ActionOnItemAndActivity):

    def __init__(self, executor, item, activity, amount):
        super().__init__(executor, item, activity)
        self.amount = amount

    def perform_action(self):

        if self.amount > self.item.amount:
            raise Exception

        req = self.activity.requirements
        if "input" in req:
            for required_group_name, required_group_params in req["input"].items():
                required_group = models.EntityType.by_name(required_group_name)
                if "used_type" in required_group_params:
                        if required_group_params["used_type"] != self.item.type_name:  # must be exactly the same type
                            raise Exception("must be exactly type " + str(required_group_params["used_type"]))
                if not required_group.contains(self.item.type):
                    raise Exception
                type_efficiency_ratio = required_group.efficiency(self.item.type)
                max_to_be_added = required_group_params["left"] / type_efficiency_ratio
                amount_to_add = min(self.amount, max_to_be_added)
                move_between_entities(self.item, self.executor, self.activity, amount_to_add, to_be_used_for=True)

                material_left_reduction = amount_to_add * type_efficiency_ratio

                required_group_params["left"] -= material_left_reduction
                required_group_params["used_type"] = self.item.type_name

        # self.activity.requirements = req

        db.session.flush()