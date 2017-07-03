# property
from enum import Enum


class P(Enum):
    BOARDABLE = "Boardable"
    IN_BOARDING = "InBoarding"
    ANY = "Any"  # special property which exists for every entity
    ANIMAL = "Animal"
    DOMESTICATED = "Domesticated"
    TAMABLE = "Tamable"
    CLOSEABLE = "Closeable"
    READABLE = "Readable"
    HAS_DEPENDENT = "HasDependent"
    EDIBLE = "Edible"
    EDIBLE_BY_ANIMAL = "EdibleByAnimal"
    ENTERABLE = "Enterable"
    SKILLS = "Skills"
    DYNAMIC_NAMEABLE = "DynamicNameable"
    VISIBLE_MATERIAL = "VisibleMaterial"
    INVISIBLE_PASSAGE = "InvisiblePassage"
    DEATH_INFO = "DeathInfo"
    DEGRADABLE = "Degradable"
    MOBILE = "Mobile"
    LINE_OF_SIGHT = "LineOfSight"
    AFFECT_LINE_OF_SIGHT = "AffectLineOfSight"
    PREFERRED_EQUIPMENT = "PreferredEquipment"
    EQUIPPABLE = "Equippable"
    WEAPONIZABLE = "Weaponizable"
    CONTROLLING_MOVEMENT = "ControllingMovement"
    BURYABLE = "Buryable"
    STATES = "States"
    BIRD_NEST = "BirdNest"
    STORAGE = "Storage"
    LOCKABLE = "Lockable"
    KEY_TO_LOCK = "KeyToLock"
    LOCK_BREAKER = "LockBreaker"
    COMBATABLE = "Combatable"
    LIMITED_SPACE = "LimitedSpace"
    INCREASE_SPACE = "IncreaseSpace"
    INCREASE_SPACE_WHEN_EQUIPPED = "IncreaseSpaceWhenEquipped"
    SIGNATURE = "Signature"
    MEMBER_OF_UNION = "MemberOfUnion"
    BEING_MOVED = "BeingMoved"
    BINDABLE = "Bindable"


class MissingPropertyException(ValueError):
    pass


class PropertyBase:
    __property__ = None

    def __init__(self, entity):
        self.entity = entity
        self.entity_property = self.entity.get_entity_property(self.__property__)
        if self.property_dict is None:
            raise MissingPropertyException("{} is missing property {}".format(self.entity, self.__property__))

    @property
    def property_dict(self):
        return self.entity.get_property(self.__property__)


class OptionalPropertyBase:
    __property__ = None

    def __init__(self, entity):
        self.entity = entity

    @property
    def property_dict(self):
        return self.entity.get_property(self.__property__)

    @property
    def property_exists(self):
        return self.property_dict is not None

    @property
    def entity_property(self):
        return self.entity.get_entity_property(self.__property__)
