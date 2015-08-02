from exeris.core import models
from exeris.core.main import db
from exeris.core.properties_base import property_class, PropertyType, property_method, __registry, P

__author__ = 'Aleksander Chrabąszcz'


@property_class
class DynamicNameablePropertyType(PropertyType):
    __property__ = P.DYNAMIC_NAMEABLE

    @property_method
    def set_dynamic_name(self, observer, name):
        if not observer:
            raise ValueError

        existing_name = models.ObservedName.query.filter_by(observer=observer, target=self).first()
        if existing_name:
            existing_name.name = name
        else:
            new_name = models.ObservedName(observer, self, name)
            db.session.add(new_name)

print("metody: ", __registry)