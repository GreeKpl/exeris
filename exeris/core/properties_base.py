import inspect


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


__registry = {}


class EntityPropertyException(Exception):
    pass


def get_method(name):
    return __registry[name]


def check_entity_property(fun, prop_name):
    def inner(entity, *args, **kwargs):
        if not entity.has_property(prop_name):
            raise EntityPropertyException(str(entity.id) + " has no property " + prop_name)
        return fun(entity, *args, **kwargs)

    if hasattr(fun, "__emulate_property__"):  # pass the 'property' flag
        inner.__emulate_property__ = True

    return inner


def property_class(clazz):
    for cls in inspect.getmro(clazz):
        for attr in cls.__dict__.values():
            if hasattr(attr, "__call__") and not attr.__name__.startswith("__"):
                __registry[attr.__name__] = check_entity_property(attr, cls.__property__)
    return clazz


def emulate_property(method):
    method.__emulate_property__ = True
    return method


class PropertyType:
    __property__ = None
