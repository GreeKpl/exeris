# property
class P:
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


class PropertyBase:
    __property__ = None

    def __init__(self, entity):
        self.entity = entity
        self.entity_property = self.entity.get_entity_property(self.__property__)
        if self.property_dict is None:
            raise ValueError("{} is missing property {}".format(self.entity, self.__property__))

    @property
    def property_dict(self):
        return self.entity.get_property(self.__property__)


class OptionalPropertyBase:
    __property__ = None

    def __init__(self, entity):
        self.entity = entity
        self.entity_property = self.entity.get_entity_property(self.__property__)
        self.property_exists = self.property_dict is not None

    @property
    def property_dict(self):
        return self.entity.get_property(self.__property__)
