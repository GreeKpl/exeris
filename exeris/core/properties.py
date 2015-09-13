import copy
import statistics
import markdown
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


@property_class
class SkillsPropertyType(PropertyType):
    __property__ = P.SKILLS

    SKILL_DEFAULT_VALUE = 0.1

    @property_method
    def get_raw_skill(self, skill_name):
        skills = self.get_property(P.SKILLS)
        return skills.get(skill_name, SkillsPropertyType.SKILL_DEFAULT_VALUE)

    @property_method
    def get_skill_factor(self, specific_skill):
        skills = self.get_property(P.SKILLS)

        skill_type = models.SkillType.query.filter_by(name=specific_skill).one()
        specific_skill_value = skills.get(specific_skill, SkillsPropertyType.SKILL_DEFAULT_VALUE)
        general_skill_value = skills.get(skill_type.general_name, SkillsPropertyType.SKILL_DEFAULT_VALUE)

        return statistics.mean([specific_skill_value, general_skill_value])

    @property_method
    def alter_skill_by(self, skill_name, change):
        skills_prop = models.EntityProperty.query.filter_by(name=P.SKILLS, entity=self).one()

        skill_val = skills_prop.data.get(skill_name, SkillsPropertyType.SKILL_DEFAULT_VALUE)
        skills_prop.data[skill_name] = skill_val + change


@property_class
class EdiblePropertyType(PropertyType):
    __property__ = P.EDIBLE

    @property_method
    def get_max_edible(self, eater):
        edible_prop = self.get_property(P.EDIBLE)

        max_edible = 0
        if edible_prop.get("hunger"):
            max_edible = max(max_edible, - eater.hunger / edible_prop["hunger"])

        return max_edible

    @property_method
    def eat(self, eater, amount):
        edible_prop = self.get_property(P.EDIBLE)

        if edible_prop.get("hunger"):
            eater.hunger += amount * edible_prop.get("hunger")


@property_class
class ReadablePropertyType(PropertyType):
    __property__ = P.READABLE

    @property_method
    def read_title(self):
        return self.get_property(P.READABLE).get("title", "title")

    @property_method
    def read_contents(self):
        md = markdown.Markdown()
        return md.convert(self.read_raw_contents())

    @property_method
    def read_raw_contents(self):
        return self.get_property(P.READABLE).get("text", "empty")

    @property_method
    def alter_contents(self, title, text):

        readable_prop = models.EntityProperty.query.filter_by(entity=self, name=P.READABLE).one()
        text_data = readable_prop.data

        text_data["title"] = title
        text_data["text"] = text

        models.EntityProperty.query.filter_by(entity=self, name=P.READABLE).update({"data": text_data})
        db.session.flush()



print("metody: ")
for prop in __registry.items():
    print(prop)