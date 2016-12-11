import html
import logging
import math
import statistics

import markdown

from exeris.core import models, main
from exeris.core.main import db
from exeris.core.properties_base import property_class, PropertyType, __registry, P

logger = logging.getLogger(__name__)


@property_class
class DynamicNameablePropertyType(PropertyType):
    __property__ = P.DYNAMIC_NAMEABLE

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

    def get_raw_skill(self, skill_name):
        skills = self.get_property(P.SKILLS)
        return skills.get(skill_name, SkillsPropertyType.SKILL_DEFAULT_VALUE)

    def get_skill_factor(self, specific_skill):
        skills = self.get_property(P.SKILLS)

        skill_type = models.SkillType.query.filter_by(name=specific_skill).one()
        specific_skill_value = skills.get(specific_skill, SkillsPropertyType.SKILL_DEFAULT_VALUE)
        general_skill_value = skills.get(skill_type.general_name, SkillsPropertyType.SKILL_DEFAULT_VALUE)

        return statistics.mean([specific_skill_value, general_skill_value])

    def alter_skill_by(self, skill_name, change):
        skills_prop = models.EntityProperty.query.filter_by(name=P.SKILLS, entity=self).one()

        skill_val = skills_prop.data.get(skill_name, SkillsPropertyType.SKILL_DEFAULT_VALUE)
        skills_prop.data[skill_name] = skill_val + change


@property_class
class MobilePropertyType(PropertyType):
    __property__ = P.MOBILE

    def get_max_speed(self):
        mobile_property = self.get_property(P.MOBILE)

        return mobile_property["speed"]


@property_class
class LineOfSightPropertyType(PropertyType):
    __property__ = P.LINE_OF_SIGHT

    def get_line_of_sight(self):
        mobile_property = self.get_property(P.LINE_OF_SIGHT)
        items_affecting_vision = models.Item.query.filter(models.Item.has_property(P.AFFECT_LINE_OF_SIGHT)) \
            .filter(models.Entity.is_in(self)).all()

        base_range = mobile_property["base_range"]
        item_effect_multiplier = max(
            [item.get_property(P.AFFECT_LINE_OF_SIGHT)["multiplier"] for item in items_affecting_vision], default=1.0)

        return base_range * item_effect_multiplier


@property_class
class EdiblePropertyType(PropertyType):
    __property__ = P.EDIBLE

    FOOD_BASED_ATTR = [main.States.STRENGTH, main.States.DURABILITY, main.States.FITNESS, main.States.PERCEPTION]

    def get_max_edible(self, eater):
        edible_prop = self.get_property(P.EDIBLE)
        satiation_left = (1 - eater.states[main.States.SATIATION])
        return math.floor(satiation_left / edible_prop["states"][main.States.SATIATION])

    def eat(self, eater, amount):
        edible_prop = self.get_property(P.EDIBLE)

        queue = eater.eating_queue
        for attribute in list(EdiblePropertyType.FOOD_BASED_ATTR) + [main.States.HUNGER]:
            if edible_prop["states"].get(attribute):
                queue[attribute] = queue.get(attribute, 0) + amount * edible_prop["states"].get(attribute)
        eater.states[main.States.SATIATION] += amount * edible_prop["states"][main.States.SATIATION]

        eater.eating_queue = queue


@property_class
class ReadablePropertyType(PropertyType):
    __property__ = P.READABLE

    def read_title(self):
        text_content = self._fetch_text_content()
        return text_content.title or ""

    def read_contents(self, allow_html=False):
        md = markdown.Markdown()

        md_text = self.read_raw_contents()
        if not allow_html:
            md_text = html.escape(md_text)
        return md.convert(md_text)

    def read_raw_contents(self):
        text_content = self._fetch_text_content()
        return text_content.md_text or ""

    def alter_contents(self, title, text, text_format):
        text_content = self._fetch_text_content()
        text_content.title = title
        text_content.format = text_format
        if text_format == models.TextContent.FORMAT_MD:
            text_content.md_text = text
        else:
            text_content.html = text

    def _fetch_text_content(self):
        text_content = models.TextContent.query.filter_by(entity=self).first()
        if not text_content:
            text_content = models.TextContent(self)
            db.session.add(text_content)
        return text_content


logger.info("Methods of entity properties: %s", __registry.keys())
