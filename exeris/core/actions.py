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
    def __init__(self, *, item_type, properties, used_materials, visible_material=None, **injected_args):
        self.item_type = item_type
        self.activity = injected_args["activity"]
        self.initiator = injected_args["initiator"]
        self.used_materials = used_materials
        self.kwargs = injected_args
        self.properties = properties
        self.visible_material = visible_material if visible_material else {}

    def perform_action(self):

        result_loc = self.activity.being_in.being_in
        if self.item_type.portable and self.initiator.being_in == result_loc:  # if being in the same location then go to inventory
            result_loc = self.initiator
        new_item = models.Item(self.item_type, result_loc, self.item_type.unit_weight)

        db.session.add(new_item)

        for property_name in self.properties:
            db.session.add(models.EntityProperty(new_item, property_name, self.properties[property_name]))

        # all the materials used for an activity were set to build this item

        if self.used_materials == "all":
            for material_type_id in models.Item.query.filter(models.Item.is_used_for(self.activity)).all():
                material_type_id.used_for = new_item
        else:  # otherwise it's a dict  # TODO NEEDS URGENT REFACTORING
            for material_type_id in self.used_materials:
                if "input" in self.activity.requirements:
                    req_input = self.activity.requirements["input"]
                    for req_material_id in req_input:  # forall requirements
                        req_used_type_id = req_input[req_material_id]["used_type"]
                        if req_material_id == material_type_id:  # req is fulfilled by material
                            real_material_type = models.ItemType.by_id(req_used_type_id)
                            required_material_type = models.EntityType.by_id(req_material_id)

                            amount = required_material_type.multiplier(real_material_type) *\
                                     req_input[req_material_id]["needed"]
                            item = models.Item.query.filter_by(type=real_material_type).one()
                            move_between_entities(item, item.used_for, new_item, amount, to_be_used_for=True)

        if self.visible_material:
            visible_material_property = {}
            for place_to_show in self.visible_material:
                group_id = self.visible_material[place_to_show]
                req_input = self.activity.requirements["input"]
                for req_material_id in req_input:  # forall requirements
                    real_used_type_id = req_input[req_material_id]["used_type"]
                    if group_id == req_material_id:  # this group is going to be shown by our visible material
                        visible_material_property[place_to_show] = real_used_type_id
            db.session.add(models.EntityProperty(new_item, P.VISIBLE_MATERIAL, visible_material_property))  # TODO


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
            x = StackableItemTransferMixin()
            x.weight = amount * item.type.unit_weight
            x.item = item
            x.move_stackable_resource(source, destination, to_be_used_for)
        elif to_be_used_for:
            item.used_for = destination
        else:
            item.being_in = destination
    else:
        raise Exception


class StackableItemTransferMixin():

    def move_stackable_resource(self, source, goal, to_be_used_for=False):
        # remove from the source
        if self.item.weight == self.weight:
            self.item.remove()
        else:
            self.item.weight -= self.weight

        # add to the goal
        if to_be_used_for:
            existing_pile = models.Item.query.filter_by(type=self.item.type).\
                filter(models.Item.is_used_for(goal)).filter_by(visible_parts=self.item.visible_parts).first()
        else:
            existing_pile = models.Item.query.filter_by(type=self.item.type).\
                filter(models.Item.is_in(goal)).filter_by(visible_parts=self.item.visible_parts).first()

        if existing_pile:
            existing_pile.weight += self.weight
        else:
            new_pile = models.Item(self.item.type, goal, self.weight, role_being_in=not to_be_used_for)
            new_pile.visible_parts = self.item.visible_parts
            db.session.add(new_pile)


class DropItemAction(ActionOnItem, StackableItemTransferMixin):

    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        if self.item.type.stackable:
            self.weight = amount * self.item.type.unit_weight
        else:
            self.weight = self.item.weight

    def perform_action(self):
        if self.item.being_in != self.executor:
            raise Exception

        if self.weight > self.item.weight:
            raise Exception

        if self.item.type.stackable:
            self.move_stackable_resource(self.item.being_in, self.executor.being_in)
            EventCreator.base("event_drop_part_of_item", self.rng, {"item_name": self.item.type.name}, self.executor)
        else:
            self.item.being_in = self.executor.being_in
            EventCreator.base("event_drop_item", self.rng, {"item_name": self.item.type.name}, self.executor)


class TakeItemAction(ActionOnItem, StackableItemTransferMixin):
    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        if self.item.type.stackable:
            self.weight = amount * self.item.type.unit_weight
        else:
            self.weight = self.item.weight

    def perform_action(self):
        if self.item.being_in != self.executor.being_in:
            raise Exception

        if self.weight > self.item.weight:
            raise Exception

        if self.item.type.stackable:
            self.move_stackable_resource(self.item.being_in, self.executor.being_in)
            EventCreator.base("event_take_part_of_item", self.rng, {"item_name": self.item.type.name}, self.executor)
        else:
            self.item.being_in = self.executor.being_in
            EventCreator.base("event_take_item", self.rng, {"item_name": self.item.type.name}, self.executor)



