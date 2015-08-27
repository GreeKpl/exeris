__author__ = 'aleksander chrabąszcz'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = None


class Errors:
    NO_INPUT_MATERIALS = "error_no_input_materials"
    ENTITY_NOT_IN_INVENTORY = "error_entity_not_in_inventory"
    ENTITY_TOO_FAR_AWAY = "error_entity_too_far_away"
    ACTIVITY_TARGET_TOO_FAR_AWAY = "error_activity_target_too_far_away"
    TOO_FAR_FROM_ACTIVITY = "error_too_far_from_activity"
    NO_MACHINE_FOR_ACTIVITY = "error_no_machine_for_activity"
    NO_TOOL_FOR_ACTIVITY = "error_no_tool_for_activity"
    OWN_INVENTORY_CAPACITY_EXCEEDED = "error_own_inventory_capacity_exceeded"
    INVALID_AMOUNT = "error_invalid_amount"


class Types:
    SEA = "sea"
    DOOR = "door"
    OUTSIDE = "outside"


class Events:
    SAY_ALOUD = "event_say_aloud"
    ADD_TO_ACTIVITY = "event_add_to_activity"
    DROP_ITEM = "event_drop_item"
    TAKE_ITEM = "event_take_item"
    GIVE_ITEM = "event_give_item"


def create_app(database=db, config_object_module="config.DevelopmentConfig"):
    global app
    app = Flask(__name__, static_folder="../../static", template_folder="../templates")
    app.config.from_object(config_object_module)
    database.init_app(app)
    return app


class GameException(Exception):
    """
    General game exception which can be shown to the user
    """
    def __init__(self, error_tag, **kwargs):
        self.error_tag = error_tag
        self.error_kwargs = kwargs


class ItemException(GameException):
    pass


class CharacterException(GameException):
    pass


class PlayerException(GameException):
    pass


class InvalidAmountException(ItemException):
    def __init__(self, *, amount):
        super().__init__(Errors.INVALID_AMOUNT, amount=amount)


class OwnInventoryExceededException(GameException):
    def __init__(self):
        super().__init__(Errors.OWN_INVENTORY_CAPACITY_EXCEEDED)


class EntityTooFarAwayException(GameException):
    def __init__(self, *, entity):
        super().__init__(Errors.ENTITY_TOO_FAR_AWAY, **entity.pyslatize())


class EntityNotInInventoryException(GameException):
    def __init__(self, *, entity):
        super().__init__(Errors.ENTITY_NOT_IN_INVENTORY, **entity.pyslatize())


class OnlySpecificTypeForGroupException(GameException):
    def __init__(self, *, type_name, group_name):
        params = dict(item_name=type_name, group_name=group_name)  # TODO? PYSLATIZE GROUP?
        super().__init__(Errors.ENTITY_NOT_IN_INVENTORY, **params)


class ItemNotApplicableForActivityException(GameException):
    def __init__(self, *, item, activity):
        params = dict(item.pyslatize(), **activity.pyslatize())
        super().__init__(Errors.ENTITY_NOT_IN_INVENTORY, **params)


class InvalidInitialLocationException(GameException):
    def __init__(self, *, entity):
        super().__init__(Errors.ENTITY_TOO_FAR_AWAY, **entity.pyslatize())


class ActivityException(GameException):
    pass


class NoInputMaterialException(ActivityException):
    def __init__(self, *, item_type):
        super().__init__(Errors.NO_INPUT_MATERIALS, item_name=item_type.name)


class NoToolForActivityException(ActivityException):
    def __init__(self, *, tool_name):
        super().__init__(Errors.NO_TOOL_FOR_ACTIVITY, tool_name=tool_name)


class NoMachineForActivityException(ActivityException):
    def __init__(self, *, machine_name):
        super().__init__(Errors.NO_MACHINE_FOR_ACTIVITY, machine_name=machine_name)


class TooFarFromActivityException(ActivityException):
    def __init__(self, *, activity):
        super().__init__(Errors.TOO_FAR_FROM_ACTIVITY, name_tag=activity.name_tag, name_params=activity.name_params)


class ActivityTargetTooFarAwayException(ActivityException):
    def __init__(self, *, entity):
        super().__init__(Errors.ACTIVITY_TARGET_TOO_FAR_AWAY, **entity.pyslatize())


class TooFewParticipantsException(ActivityException):
    def __init__(self, *, min_number):
        super().__init__(Errors.ACTIVITY_TARGET_TOO_FAR_AWAY, min_number=min_number)


class TooManyParticipantsException(ActivityException):
    def __init__(self, *, max_number):
        super().__init__(Errors.ACTIVITY_TARGET_TOO_FAR_AWAY, max_number=max_number)
