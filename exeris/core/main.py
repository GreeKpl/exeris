import hashlib
import logging
import sys
from Crypto.Cipher import AES

from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = None

logger = logging.getLogger(__name__)


class Errors:
    TOO_LOW_SKILL = "error_too_low_skill"
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
    LAND_TERRAIN = "group_land_terrain"
    WATER_TERRAIN = "group_water_terrain"
    ANY_TERRAIN = "group_any_terrain"
    ACTIVITY = "activity"
    ITEM = "item"  # generic item
    SEA = "sea"
    DOOR = "door"
    INVISIBLE_PASSAGE = "invisible_passage"
    OUTSIDE = "outside"
    ALIVE_CHARACTER = "alive_character"
    DEAD_CHARACTER = "dead_character"


class Events:
    OPEN_ENTITY = "event_open_entity"
    CLOSE_ENTITY = "event_close_entity"
    MOVE = "event_move"
    EAT = "event_eat"
    SAY_ALOUD = "event_say_aloud"
    SPEAK_TO_SOMEBODY = "event_speak_to_somebody"
    WHISPER = "event_whisper"
    ADD_TO_ACTIVITY = "event_add_to_activity"
    DROP_ITEM = "event_drop_item"
    TAKE_ITEM = "event_take_item"
    GIVE_ITEM = "event_give_item"
    DEATH_OF_STARVATION = "event_death_of_starvation"
    DEATH_OF_DAMAGE = "event_death_of_damage"


class Hooks:
    ITEM_DROPPED = "item_dropped"
    LOCATION_ENTERED = "location_entered"
    SPOKEN_ALOUD = "spoken_aloud"
    WHISPERED = "whispered"
    EATEN = "eaten"
    NEW_EVENT = "new_event"
    NEW_CHARACTER_NOTIFICATION = "new_character_notification"
    NEW_PLAYER_NOTIFICATION = "new_player_notification"
    EXCEEDED_HUNGER_LEVEL = "exceeded_hunger_level"
    ENTITY_CONTENTS_COUNT_DECREASED = "entity_contents_count_decreased"


class Intents:
    TRAVEL = "travel"
    COMBAT_TICK = "combat_tick"
    COMBAT = "combat"


def create_app(database=db, config_object_module="exeris.config.DevelopmentConfig"):
    global app

    app = Flask("exeris")
    app.config.from_object(config_object_module)

    if app.config["DEBUG"]:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    else:
        pass  # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    database.init_app(app)
    return app


def _cipher():
    h = hashlib.sha256()
    h.update(app.config['SECRET_KEY'].encode())

    if hasattr(g, "character"):
        h.update(g.character.id.to_bytes(8, 'big'))
    else:
        h.update(b'NO CHAR ID')
    return AES.new(h.digest(), AES.MODE_ECB)


_encode_token = b'f' * 8


def encode(uid):
    pt = uid.to_bytes(8, 'big') + _encode_token
    return str(int.from_bytes(_cipher().encrypt(pt), 'big'))


def decode(encoded_id):
    pt = _cipher().decrypt(int(encoded_id).to_bytes(16, 'big'))
    if pt[8:] != _encode_token:
        raise ValueError('Could not decode ID')
    return int.from_bytes(pt[:8], 'big')


_hooks = {}


def add_hook(name, func):
    if name not in _hooks:
        _hooks[name] = []
    _hooks[name].append(func)


def call_hook(name, **kwargs):
    logger.info("Hook %s for arguments: %s", name, str(kwargs))
    for func in _hooks.get(name, []):
        logger.debug("Calling hook function: %s", func.__name__)
        func(**kwargs)


def hook(name):
    def inner_hook(f):
        add_hook(name, f)  # register hook

    return inner_hook


class GameException(Exception):
    """
    General game exception which can be shown to the user
    """

    def __init__(self, error_tag, **kwargs):
        self.error_tag = error_tag
        self.error_kwargs = kwargs

    def __str__(self):
        return "{}: {} ({})".format(str(self.__class__), self.error_tag, str(self.error_kwargs))


class ItemException(GameException):
    pass


class CharacterException(GameException):
    pass


class PlayerException(GameException):
    pass


class TurningIntoIntentExceptionMixin(Exception):
    """
    This class guarantees that exception class has turn_into_intent method, which creates instance of Intent
        of correct type for a correct (possibly exception-specific) action
    """

    def turn_into_intent(self, entity, action, priority=1):
        raise NotImplementedError("should be implemented in subclass")


class InvalidAmountException(ItemException):
    def __init__(self, *, amount):
        super().__init__(Errors.INVALID_AMOUNT, amount=amount)


class OwnInventoryExceededException(GameException):
    def __init__(self):
        super().__init__(Errors.OWN_INVENTORY_CAPACITY_EXCEEDED)


class EntityTooFarAwayException(GameException, TurningIntoIntentExceptionMixin):
    def __init__(self, *, entity):
        super().__init__(Errors.ENTITY_TOO_FAR_AWAY, **entity.pyslatize())
        self.entity = entity

    def turn_into_intent(self, executor, action, priority=1):
        from exeris.core import models, actions, deferred
        travel_action = actions.TravelToEntityAndPerformActionProcess(executor, self.entity, action)
        return models.Intent(action.executor, Intents.TRAVEL, priority, deferred.serialize(travel_action))


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


class TooLowSkillException(ActivityException):
    def __init__(self, *, skill_name, required_level):
        super().__init__(Errors.TOO_LOW_SKILL, skill_name=skill_name, required_level=required_level)


class TooFewParticipantsException(ActivityException):
    def __init__(self, *, min_number):
        super().__init__(Errors.ACTIVITY_TARGET_TOO_FAR_AWAY, min_number=min_number)


class TooManyParticipantsException(ActivityException):
    def __init__(self, *, max_number):
        super().__init__(Errors.ACTIVITY_TARGET_TOO_FAR_AWAY, max_number=max_number)
