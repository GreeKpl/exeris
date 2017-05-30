import html
import logging
import math
import statistics

import markdown

import sqlalchemy as sql
from shapely.geometry import Point

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

    def get_all_skills(self):

        skill_values = {}
        skill_parents = {}

        specific_skills = models.SkillType.query.all()
        for skill_type in specific_skills:
            skill_values[skill_type.name] = self.get_raw_skill(skill_type.name)
            skill_values[skill_type.general_name] = self.get_raw_skill(skill_type.general_name)
            skill_parents[skill_type.name] = skill_type.general_name
        general_skill_names = set(skill_parents.values())

        all_skills = []
        for general_skill_name in general_skill_names:
            general_skill_dict = self._dict_representation(general_skill_name, skill_values[general_skill_name])
            general_skill_dict["children"] = self.get_dict_representation_of_children(general_skill_name, skill_parents)
            all_skills.append(general_skill_dict)

        return all_skills

    def get_dict_representation_of_children(self, general_skill_name, skill_parents):
        child_skill_names = [skill_name for skill_name, skill_parent
                             in skill_parents.items() if skill_parent == general_skill_name]
        a = [self._dict_representation(child_skill_name,
                                       self.get_raw_skill(child_skill_name))
             for child_skill_name in child_skill_names]
        return a

    def _dict_representation(self, name, value):
        return {
            "name": name,
            "value": value,
        }

    def alter_skill_by(self, skill_name, change):
        skill_val = self.get_raw_skill(skill_name)
        self.entity_property.data[skill_name] = skill_val + change


class MobileProperty(PropertyBase):
    __property__ = P.MOBILE

    def get_max_speed(self):
        return self.property_dict["speed"]

    def get_inertiality(self):
        return self.property_dict.get("inertiality", 0)

    def get_traversable_terrains(self):
        return self.property_dict["traversable_terrains"]


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
        self.entity.title = title
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

    def get_preferred_equipment(self, return_ids=False):
        if not self.property_exists:
            return []
        equipment_ids = self.property_dict.values()
        if return_ids:
            return equipment_ids
        return models.Item.query.filter(models.Item.id.in_(equipment_ids)).all()

    def set_preferred_equipment_part(self, item):
        if not item.has_property(P.EQUIPPABLE):
            raise ValueError("Entity {} is not Equippable".format(item))

        eq_part = item.get_property(P.EQUIPPABLE)["eq_part"]
        self.entity_property.data[eq_part] = item.id


class OptionalCloseableProperty(OptionalPropertyBase):
    __property__ = P.CLOSEABLE

    def is_open(self):
        return not self.property_exists or not self.property_dict.get("closed", False)


class OptionalMemberOfUnionProperty(OptionalPropertyBase):
    __property__ = P.MEMBER_OF_UNION

    def union(self, other_location, own_priority=1, other_priority=1):
        other_entitys_union_prop = other_location.get_property(P.MEMBER_OF_UNION)
        if self.property_exists and other_entitys_union_prop is not None:
            entities_properties_in_union = self.get_entity_properties_of_own_union()
            for entity_property in entities_properties_in_union:
                entity_property.data["union_id"] = other_entitys_union_prop["union_id"]
            self.entity_property.data["priority"] = own_priority
        elif self.property_exists and other_entitys_union_prop is None:
            other_location.properties.append(models.EntityProperty(self.__property__, {
                "union_id": self.entity_property.data["union_id"],
                "priority": other_priority,
            }))
            self.entity_property.data["priority"] = own_priority
        elif not self.property_exists and other_entitys_union_prop is not None:
            self.entity.properties.append(models.EntityProperty(self.__property__, {
                "union_id": other_entitys_union_prop["union_id"],
                "priority": own_priority,
            }))
        else:
            new_union_id = self.create_new_union_id()
            self.entity.properties.append(models.EntityProperty(self.__property__, {
                "union_id": new_union_id,
                "priority": own_priority,
            }))
            other_location.properties.append(models.EntityProperty(self.__property__, {
                "union_id": new_union_id,
                "priority": other_priority,
            }))

    def get_union_id(self):
        if not self.property_exists:
            return None
        return self.entity_property.data["union_id"]

    def leave_union(self):
        db.session.delete(self.entity_property)

    def disband_union(self):
        union_entity_properties = self.get_entity_properties_of_own_union()
        for entity_property in union_entity_properties:
            db.session.delete(entity_property)

    def get_entity_properties_of_own_union(self):
        own_property = self.entity_property
        if not own_property:
            return []
        return models.EntityProperty.query \
            .filter_by(name=P.MEMBER_OF_UNION) \
            .filter(self.json_to_int(models.EntityProperty.data["union_id"]) == own_property.data["union_id"]).all()

    def is_in_same_union_as(self, other_entity):
        return other_entity in [ep.entity for ep in self.get_entity_properties_of_own_union()]

    def is_in_nontrivial_union(self):
        return len(self.get_entity_properties_of_own_union()) > 1

    @staticmethod
    def create_new_union_id():
        return db.engine.execute(models.Sequences.entity_union_sequence)

    @staticmethod
    def json_to_int(what):
        return what.astext.cast(sql.Integer)

    def split_union(self, neighbouring_location):
        """Split union into two unions. It is split across the passage between `self.entity` and `neighbouring_location`
        It is required that there is no other path from `self.entity` and `neighbouring_location`
        except the single direct passage"""
        entities_in_former_union = [prop.entity for prop in self.get_entity_properties_of_own_union()]

        new_union_id = self.create_new_union_id()
        self._update_union_id(self.entity, new_union_id)

        passages_to_visit = self.entity.passages_to_neighbours
        visited_locations = []
        while len(passages_to_visit):
            passage = passages_to_visit.pop()
            loc_on_other_side = passage.other_side
            if loc_on_other_side != neighbouring_location and loc_on_other_side in entities_in_former_union:
                self._update_union_id(loc_on_other_side, new_union_id)
                visited_locations.append(loc_on_other_side)
                passages_to_visit += [psg for psg in loc_on_other_side.passages_to_neighbours if
                                      psg.other_side not in visited_locations]

    def _update_union_id(self, location, new_union_id):
        entity_prop = location.get_entity_property(P.MEMBER_OF_UNION)
        entity_prop.data["union_id"] = new_union_id


class OptionalBeingMovedProperty(OptionalPropertyBase):
    __property__ = P.BEING_MOVED

    def set_movement(self, radius, direction=0):
        """
        In polar coordinates
        :param radius: in travel cost
        :param direction: in radians
        """
        self._update_value("movement", [radius, direction])

    def get_movement(self):
        """
        :return: tuple with distance (travel cost) and direction (in radians)
        """
        return tuple(self.entity_property.data.get("movement", [0, 0]))

    def set_inertia(self, radius, direction=0):
        """
        In polar coordinates
        :param radius: in travel cost
        :param direction: in radians
        """
        self._update_value("inertia", [radius, direction])

    def get_inertia(self):
        """
        :return: tuple with distance (travel cost) and direction (in radians)
        """
        return tuple(self.entity_property.data.get("inertia", [0, 0]))

    def set_target(self, location):
        self._update_value("target", location.id)

    def get_target(self):
        target_id = self.entity_property.data.get("target", None)
        if not target_id:
            return None
        return models.Location.by_id(target_id)

    def set_terrain_types(self, terrain_types):
        self._update_value("terrain_types", [self._extract_name(t) for t in terrain_types])

    def _extract_name(self, entity_type):
        if isinstance(entity_type, str):
            return entity_type
        return entity_type.name

    def get_terrain_types(self):
        terrain_types = self.entity_property.data.get("terrain_types", [])
        return [models.EntityType.by_name(t) for t in terrain_types]

    def remove(self):
        entity_property = self.entity_property
        if entity_property:
            entity_property.data = {}
            db.session.delete(entity_property)

    def _update_value(self, key_name, value):
        entity_property = self.entity_property
        if not self.property_exists:
            entity_property = models.EntityProperty(self.__property__)
            self.entity.properties.append(entity_property)
        entity_property.data[key_name] = value


class BindableProperty(PropertyBase):
    __property__ = P.BINDABLE

    def get_allowed_types(self):
        prop_dict = self.property_dict
        allowed_types = prop_dict["to_types"]
        return [models.EntityType.by_name(type_name) for type_name in allowed_types]


class BoardableProperty(PropertyBase):
    __property__ = P.BOARDABLE

    def get_concrete_types_to_board_to(self):
        allowed_ship_types = self.property_dict.get("allowed_ship_types", [])
        allowed_ship_types = [models.EntityType.by_name(ship_type) for ship_type in allowed_ship_types]
        return models.get_concrete_types_for_groups(allowed_ship_types)


class OptionalInBoardingProperty(OptionalPropertyBase):
    __property__ = P.IN_BOARDING

    def get_ids_of_ships_in_boarding(self):
        entity_property = self.entity_property
        if not entity_property:
            return []
        return entity_property.data.get("ships_in_boarding", [])

    def append_ship_in_boarding(self, other_ship):
        other_ship_in_boarding_property = OptionalInBoardingProperty(other_ship)
        other_ship_in_boarding_property._add_entry_about_ship_in_boarding(self.entity)
        self._add_entry_about_ship_in_boarding(other_ship)

    def _add_entry_about_ship_in_boarding(self, neighbour_to_add):
        entity_property = self.entity_property
        if not entity_property:
            entity_property = models.EntityProperty(self.__property__, entity=self.entity)
            db.session.add(entity_property)
            entity_property.data["ships_in_boarding"] = [neighbour_to_add.id]
        else:
            entity_property.data["ships_in_boarding"].append(neighbour_to_add.id)

    def remove_ship_from_boarding(self, other_ship):
        other_ship_in_boarding_property = OptionalInBoardingProperty(other_ship)
        other_ship_in_boarding_property._remove_entry_about_ship_in_boarding(self.entity)
        self._remove_entry_about_ship_in_boarding(other_ship)

    def _remove_entry_about_ship_in_boarding(self, neighbour_to_remove):
        entity_property = self.entity_property
        entity_property.data["ships_in_boarding"].remove(neighbour_to_remove.id)
        if not len(entity_property.data["ships_in_boarding"]):
            db.session.delete(entity_property)
