from exeris.core import models
from exeris.core.properties_base import property_class, PropertyType, property_method, __registry, P

__author__ = 'Aleksander Chrabąszcz'


@property_class
class TakeablePropertyType(PropertyType):
    __property__ = "Takeable"

    @property_method
    def take_by(self, character):
        pass


@property_class
class DynamicNamePropertyType(PropertyType):
    __property__ = P.DYNAMIC_NAMEABLE

    @property_method
    def set_dynamic_name(self, name, observer):
        if not observer:
            raise ValueError

        models.ObservedName(self, name, observer)

print("metody: ", __registry)