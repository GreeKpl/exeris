import statistics
import math

import markdown

from exeris.core import models
from exeris.core.main import db
from exeris.core.properties_base import property_class, PropertyType, property_method, __registry, P


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
class MobilePropertyType(PropertyType):
    __property__ = P.MOBILE

    @property_method
    def get_max_speed(self):
        mobile_property = self.get_property(P.MOBILE)

        return mobile_property["speed"]


@property_class
class LineOfSightPropertyType(PropertyType):
    __property__ = P.LINE_OF_SIGHT

    @property_method
    def get_line_of_sight(self):
        mobile_property = self.get_property(P.LINE_OF_SIGHT)
        items_affecting_vision = models.Item.query_entities_having_property(P.AFFECT_LINE_OF_SIGHT) \
            .filter(models.Entity.is_in(self)).all()

        base_range = mobile_property["base_range"]
        item_effect_multiplier = max(
            [item.get_property(P.AFFECT_LINE_OF_SIGHT)["multiplier"] for item in items_affecting_vision], default=1.0)

        return base_range * item_effect_multiplier


@property_class
class EdiblePropertyType(PropertyType):
    __property__ = P.EDIBLE

    FOOD_BASED_ATTR = ["strength", "durability", "fitness", "perception"]

    @property_method
    def get_max_edible(self, eater):
        edible_prop = self.get_property(P.EDIBLE)
        satiation_left = (1 - eater.satiation)
        return math.floor(satiation_left / edible_prop["satiation"])

    @property_method
    def eat(self, eater, amount):
        edible_prop = self.get_property(P.EDIBLE)

        queue = eater.eating_queue
        for attribute in list(EdiblePropertyType.FOOD_BASED_ATTR) + ["hunger"]:
            if edible_prop.get(attribute):
                queue[attribute] = queue.get(attribute, 0) + amount * edible_prop.get(attribute)
        eater.satiation += amount * edible_prop["satiation"]

        eater.eating_queue = queue


@property_class
class ReadablePropertyType(PropertyType):
    __property__ = P.READABLE

    @property_method
    def _fetch_text_content(self):
        text_content = models.TextContent.query.filter_by(entity=self).first()
        if not text_content:
            text_content = models.TextContent(self)
            db.session.add(text_content)
        return text_content

    @property_method
    def read_title(self):
        text_content = self._fetch_text_content()
        return text_content.title or ""

    @property_method
    def read_contents(self):
        md = markdown.Markdown()
        return md.convert(self.read_raw_contents())

    @property_method
    def read_raw_contents(self):
        text_content = self._fetch_text_content()
        return text_content.md_text or ""

    @property_method
    def alter_contents(self, title, text, text_format):
        text_content = self._fetch_text_content()
        text_content.title = title
        text_content.format = text_format
        if text_format == models.TextContent.FORMAT_MD:
            text_content.md_text = text
        else:
            text_content.html = text


print("metody: ", __registry.keys())
