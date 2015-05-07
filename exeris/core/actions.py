from exeris.core.main import SameLocationRange

__author__ = 'alek'


class AbstractAction:  # top level, we don't assume anything
    pass


class Action:  # top level action, where we only know that it's done by a character

    def __init__(self, executor):
        self.executor = executor

    def perform(self):
        self.perform_action()


# rich collection of pre-configured actions
class ActionOnSelf(Action):
    def __init__(self, executor):
        super().__init__(executor)


class ActionOnItem(Action):

    def __init__(self, executor, item, rng=SameLocationRange):
        super().__init__(executor)
        self.item = item
        self.rng = rng


class ActionOnLocation(Action):
    def __init__(self, executor, location, rng=SameLocationRange):
        super().__init__(executor)
        self.location = location
        self.rng = rng


class ActionOnActivity(Action):
    def __init__(self, executor, activity, rng=SameLocationRange):
        super().__init__(executor)
        self.activity = activity
        self.rng = rng


class ActionOnItemAndActivity(Action):
    def __init__(self, executor, item, activity, rng=SameLocationRange):
        super().__init__(executor)
        self.item = item
        self.activity = activity
        self.rng = rng


class ActionOnItemAndCharacter(Action):
    def __init__(self, executor, item, character, rng=SameLocationRange):
        super().__init__(executor)
        self.item = item
        self.character = character
        self.rng = rng


class CreateItemAction(AbstractAction):
    pass
