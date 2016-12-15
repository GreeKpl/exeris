import html
import logging
import math
import statistics

import markdown

from exeris.core import models, main, deferred
from exeris.core.main import db
from exeris.core.properties_base import P, PropertyBase, OptionalPropertyBase

logger = logging.getLogger(__name__)


class DynamicNameableProperty(PropertyBase):
    __property__ = P.DYNAMIC_NAMEABLE

    def set_dynamic_name(self, observer, name):
        if not observer:
            raise ValueError

        existing_name = models.ObservedName.query.filter_by(observer=observer, target=self.entity).first()
        if existing_name:
            existing_name.name = name
        else:
            new_name = models.ObservedName(observer, self.entity, name)
            db.session.add(new_name)


class SkillsProperty(PropertyBase):
    __property__ = P.SKILLS

    SKILL_DEFAULT_VALUE = 0.1

    def get_raw_skill(self, skill_name):
        return self.property_dict.get(skill_name, SkillsProperty.SKILL_DEFAULT_VALUE)

    def get_skill_factor(self, specific_skill):
        skill_type = models.SkillType.query.filter_by(name=specific_skill).one()
        specific_skill_value = self.property_dict.get(specific_skill, SkillsProperty.SKILL_DEFAULT_VALUE)
        general_skill_value = self.property_dict.get(skill_type.general_name, SkillsProperty.SKILL_DEFAULT_VALUE)

        return statistics.mean([specific_skill_value, general_skill_value])

    def alter_skill_by(self, skill_name, change):
        skill_val = self.entity_property.data.get(skill_name, SkillsProperty.SKILL_DEFAULT_VALUE)
        self.entity_property.data[skill_name] = skill_val + change


class MobileProperty(PropertyBase):
    __property__ = P.MOBILE

    def get_max_speed(self):
        return self.property_dict["speed"]


class LineOfSightProperty(PropertyBase):
    __property__ = P.LINE_OF_SIGHT

    def get_line_of_sight(self):
        items_affecting_vision = models.Item.query.filter(models.Item.has_property(P.AFFECT_LINE_OF_SIGHT)) \
            .filter(models.Entity.is_in(self.entity)).all()

        base_range = self.property_dict["base_range"]
        item_effect_multiplier = max(
            [item.get_property(P.AFFECT_LINE_OF_SIGHT)["multiplier"] for item in items_affecting_vision], default=1.0)

        return base_range * item_effect_multiplier


class EdibleProperty(PropertyBase):
    __property__ = P.EDIBLE

    FOOD_BASED_ATTR = [main.States.STRENGTH, main.States.DURABILITY, main.States.FITNESS, main.States.PERCEPTION]

    def get_max_edible(self, eater):
        edible_prop = self.property_dict
        satiation_left = (1 - eater.states[main.States.SATIATION])
        return math.floor(satiation_left / edible_prop["states"][main.States.SATIATION])

    def eat(self, eater, amount):
        edible_prop = self.property_dict

        queue = eater.eating_queue
        for attribute in list(EdibleProperty.FOOD_BASED_ATTR) + [main.States.HUNGER]:
            if edible_prop["states"].get(attribute):
                queue[attribute] = queue.get(attribute, 0) + amount * edible_prop["states"].get(attribute)
        eater.states[main.States.SATIATION] += amount * edible_prop["states"][main.States.SATIATION]

        eater.eating_queue = queue


class ReadableProperty(PropertyBase):
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
        text_content = models.TextContent.query.filter_by(entity=self.entity).first()
        if not text_content:
            text_content = models.TextContent(self.entity)
            db.session.add(text_content)
        return text_content


class OptionalLockableProperty(OptionalPropertyBase):
    def can_pass(self, executor):
        return not self.lock_exists() or self.has_key_to_lock(executor)

    def has_key_to_lock(self, executor):
        has_key = models.Item.query.filter(models.Item.is_in(executor)) \
            .filter(models.Item.has_property(P.KEY_TO_LOCK, lock_id=self.get_lock_id())).first()
        return has_key is not None

    def lock_exists(self):
        return self.property_dict is not None and self.property_dict["lock_exists"]

    def get_lock_id(self):
        return self.property_dict["lock_id"]


class CombatableProperty(PropertyBase):
    __property__ = P.COMBATABLE

    def __init__(self, entity):
        super().__init__(entity)
        self.optional_preferred_equipment_property = OptionalPreferredEquipmentProperty(entity)

    @property
    def combat_action(self):
        combat_intent = models.Intent.query.filter_by(type=main.Intents.COMBAT, executor=self.entity).first()
        if combat_intent:
            return deferred.call(combat_intent.serialized_action)
        return None

    @combat_action.setter
    def combat_action(self, combat_action):
        combat_intent = models.Intent.query.filter_by(type=main.Intents.COMBAT, executor=self.entity).first()
        if combat_intent:
            combat_intent.serialized_action = deferred.serialize(combat_action)
        raise ValueError("Can't update combat action, {} is not in combat".format(self.entity))

    def get_weapon(self):
        weapon_used = None
        if self.optional_preferred_equipment_property.property_exists:
            weapon_used = self.optional_preferred_equipment_property.get_equipment().get(main.EqParts.WEAPON, None)
        if not weapon_used:
            if not self.entity.has_property(P.WEAPONIZABLE):
                raise ValueError("{} doesn't have a weapon and cannot be a weapon itself".format(self.entity))
            return self.entity  # entity is a weapon itself
        return weapon_used


class OptionalPreferredEquipmentProperty(OptionalPropertyBase):
    __property__ = P.PREFERRED_EQUIPMENT

    def get_equipment(self):
        eq_property = self.property_dict
        eq_property = eq_property if eq_property else {}
        equipment = {k: models.Item.by_id(v) for k, v in eq_property.items()}

        def in_range(item):
            from exeris.core import general
            return self.entity.has_access(item, rng=general.InsideRange())

        def eq_part_is_disallowed_by_other(eq_part, all_equipment):
            for eq_item in all_equipment.values():
                equippable_prop = eq_item.get_property(P.EQUIPPABLE)
                if eq_part in equippable_prop.get("disallow_eq_parts", []):
                    return True
            return False

        equipment = {eq_part: item for eq_part, item in equipment.items() if
                     item is not None and in_range(item)}
        return {eq_part: item for eq_part, item in equipment.items()
                if not eq_part_is_disallowed_by_other(eq_part, equipment)}

    def set_preferred_equipment_part(self, item):
        if not item.has_property(P.EQUIPPABLE):
            raise ValueError("Entity {} is not Equippable".format(item))

        eq_part = item.get_property(P.EQUIPPABLE)["eq_part"]
        self.entity_property.data[eq_part] = item.id
