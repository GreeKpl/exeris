from exeris.core.deferred import convert
from exeris.core import deferred
from exeris.core.main import db
from exeris.core import models

from exeris.core.general import SameLocationRange, EventCreator

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


@form_on_setup(item_name=deferred.NameInput)
class CreateItemAction(ActivityAction):

    @convert(item_type=models.ItemType)
    def __init__(self, *, item_type, properties, **injected_args):
        self.item_type = item_type
        self.activity = injected_args["activity"]
        self.properties = properties

    def perform_action(self):
        item = models.Item(self.item_type, self.activity.being_in.being_in, self.item_type.unit_weight)

        db.session.add(item)

        for property_name in self.properties:
            db.session.add(models.EntityProperty(item, property_name, self.properties[property_name]))


class RemoveItemAction(ActivityAction):

    @convert(item=models.Item)
    def __init__(self, item, gracefully=True):
        self.item = item
        self.gracefully = gracefully

    def perform_action(self):
        self.item.remove(self.gracefully)


##############################
# CHARACTER-SPECIFIC ACTIONS #
##############################

class StackableItemTransferMixin():
    def move_stackable_resource(self, source, goal):
        # remove from the source
        if self.item.weight == self.weight:
            db.session.delete(self.item)
        else:
            self.item.weight -= self.weight

        # add to the goal
        existing_pile = models.Item.query.filter_by(type=self.item.type).\
            filter(models.Item.is_in(goal)).filter_by(visible_parts=self.item.visible_parts).first()

        if existing_pile:
            existing_pile.weight += self.weight
        else:
            new_pile = models.Item(self.item.type, goal, self.weight)
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



