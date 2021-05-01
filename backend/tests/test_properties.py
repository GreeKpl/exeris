import math
from flask_testing import TestCase
from shapely.geometry import Point

from exeris.core.main import db
from exeris.core.models import RootLocation, LocationType, Location, EntityTypeProperty, ObservedName, SkillType, \
    EntityProperty, \
    ItemType, Item, TextContent, TypeGroup
# noinspection PyUnresolvedReferences
from exeris.core import properties, main
from exeris.core.properties_base import P
from tests import util


class EntityPropertiesTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_set_and_alter_dynamic_name_success(self):
        rl = RootLocation(Point(1, 1), 123)
        building_type = LocationType("building", 1000)
        building = Location(rl, building_type)

        doer = util.create_character("doer", rl, util.create_player("ABC"))

        # make BUILDING nameable
        building_type.properties.append(EntityTypeProperty(P.DYNAMIC_NAMEABLE))
        db.session.add_all([rl, building_type, building])

        # use method taken from property
        dynamic_nameable_property = properties.DynamicNameableProperty(building)
        dynamic_nameable_property.set_dynamic_name(doer, "Krakow")

        # check if name is really changed
        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Krakow", new_name.name)

        # change the existing name
        dynamic_nameable_property = properties.DynamicNameableProperty(building)
        dynamic_nameable_property.set_dynamic_name(doer, "Wroclaw")

        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Wroclaw", new_name.name)

    def test_get_and_alter_skill_success(self):
        rl = RootLocation(Point(1, 1), 111)
        char = util.create_character("ABC", rl, util.create_player("wololo"))

        db.session.add_all([rl, SkillType("baking", "cooking"),
                            SkillType("frying", "cooking")])
        db.session.flush()

        char_skills = properties.SkillsProperty(char)

        self.assertAlmostEqual(0.1, char_skills.get_raw_skill("baking"))

        char_skills.alter_skill_by("frying", 0.2)  # 0.1 changed by 0.2 means 0.3 frying

        self.assertAlmostEqual(0.1, char_skills.get_raw_skill("baking"))
        self.assertAlmostEqual(0.3, char_skills.get_raw_skill("frying"))

        self.assertAlmostEqual(0.2, char_skills.get_skill_factor("frying"))  # mean of 0.1 cooking and 0.3 frying = 0.2


class ItemPropertiesTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_readable_property_read_then_alter_text_and_then_read_again(self):
        rl = RootLocation(Point(1, 1), 122)
        book_type = ItemType("book", 100)
        book_type.properties.append(EntityTypeProperty(P.READABLE))
        book = Item(book_type, rl)

        db.session.add_all([rl, book_type, book])

        # read for the first time

        book_readable_property = properties.ReadableProperty(book)
        self.assertEqual("", book_readable_property.read_title())
        self.assertEqual("", book_readable_property.read_contents())

        book_readable_property.alter_contents("NEW TITLE", "NEW TEXT", TextContent.FORMAT_MD)

        self.assertEqual("NEW TITLE", book_readable_property.read_title())
        self.assertEqual("<p>NEW TEXT</p>", book_readable_property.read_contents())
        self.assertEqual("NEW TEXT", book_readable_property.read_raw_contents())

        book_readable_property.alter_contents("NEW TITLE", "**abc** hehe", TextContent.FORMAT_MD)
        self.assertEqual("<p><strong>abc</strong> hehe</p>", book_readable_property.read_contents())
        self.assertEqual("**abc** hehe", book_readable_property.read_raw_contents())


class CharacterPropertiesTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_line_of_sight_property_to_affect_visibility_based_range(self):
        rl = RootLocation(Point(1, 1), 122)
        char = util.create_character("test1", rl, util.create_player("ala123"))

        db.session.add_all([rl])

        line_of_sight_property = properties.LineOfSightProperty(char)
        self.assertEqual(10, line_of_sight_property.get_line_of_sight())

        spyglass_type = ItemType("spyglass", 300)
        spyglass_type.properties.append(EntityTypeProperty(P.AFFECT_LINE_OF_SIGHT, data={"multiplier": 3}))
        spyglass = Item(spyglass_type, char)

        db.session.add_all([spyglass_type, spyglass])

        self.assertEqual(30, line_of_sight_property.get_line_of_sight())

    def test_mobile_property_to_affect_land_traversability_based_range(self):
        rl = RootLocation(Point(1, 1), 122)
        char = util.create_character("test1", rl, util.create_player("ala123"))

        cart_type = LocationType("cart", 500)
        cart_type.properties.append(EntityTypeProperty(P.MOBILE, data={"speed": 20}))
        cart = Location(rl, cart_type)

        db.session.add_all([rl, cart_type, cart])

        char_mobile_property = properties.MobileProperty(char)
        cart_mobile_property = properties.MobileProperty(cart)

        self.assertEqual(10, char_mobile_property.get_max_speed())
        self.assertEqual(20, cart_mobile_property.get_max_speed())

    def test_preferred_equipment_to_wear(self):
        rl = RootLocation(Point(1, 1), 122)
        char = util.create_character("test1", rl, util.create_player("ala123"))

        coat_type = ItemType("coat", 200)
        coat_type.properties.append(EntityTypeProperty(P.EQUIPPABLE, {"eq_part": main.EqParts.BODY}))
        coat = Item(coat_type, char)

        two_handed_sword_type = ItemType("two_handed_sword", 200)
        two_handed_sword_type.properties.append(
            EntityTypeProperty(P.EQUIPPABLE, {"eq_part": main.EqParts.WEAPON,
                                              "disallow_eq_parts": [main.EqParts.SHIELD]}))
        two_handed_sword = Item(two_handed_sword_type, char)

        jacket_type = ItemType("jacket", 200)
        jacket_type.properties.append(EntityTypeProperty(P.EQUIPPABLE, {"eq_part": main.EqParts.BODY}))
        jacket = Item(jacket_type, char)

        wooden_shield_type = ItemType("wooden_shield", 200)
        wooden_shield_type.properties.append(EntityTypeProperty(P.EQUIPPABLE, {"eq_part": main.EqParts.SHIELD}))
        wooden_shield = Item(wooden_shield_type, char)

        db.session.add_all([rl, coat_type, coat, two_handed_sword_type, two_handed_sword,
                            jacket_type, jacket, wooden_shield_type, wooden_shield])
        char_optional_preferred_equipment_property = properties.OptionalPreferredEquipmentProperty(char)

        char_optional_preferred_equipment_property.set_preferred_equipment_part(coat)
        char_optional_preferred_equipment_property.set_preferred_equipment_part(wooden_shield)
        char_optional_preferred_equipment_property.set_preferred_equipment_part(jacket)

        self.assertCountEqual({main.EqParts.BODY: jacket, main.EqParts.SHIELD: wooden_shield},
                              char_optional_preferred_equipment_property.get_equipment())

        char_optional_preferred_equipment_property.set_preferred_equipment_part(two_handed_sword)

        # wooden shield is blocked by a two handed sword
        self.assertCountEqual({main.EqParts.BODY: jacket, main.EqParts.WEAPON: two_handed_sword},
                              char_optional_preferred_equipment_property.get_equipment())


class LocationPropertyTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_entity_union_creation(self):
        rl = RootLocation(Point(1, 1), 10)
        cog_type = LocationType("cog", 1000)

        cog1 = Location(rl, cog_type)
        cog2 = Location(rl, cog_type)
        cog3 = Location(rl, cog_type)
        cog4 = Location(rl, cog_type)
        db.session.add_all([rl, cog_type, cog1, cog2, cog3, cog4])

        cog1_member_of_union_property = properties.OptionalMemberOfUnionProperty(cog1)
        cog1_member_of_union_property.union(cog2)

        cog1_and_2_properties = cog1_member_of_union_property.get_entity_properties_of_own_union()
        cog1_entity_property = EntityProperty.query.filter_by(name=P.MEMBER_OF_UNION, entity=cog1).one()
        cog2_entity_property = EntityProperty.query.filter_by(name=P.MEMBER_OF_UNION, entity=cog2).one()
        self.assertCountEqual([cog1_entity_property, cog2_entity_property], cog1_and_2_properties)
        self.assertEqual(1, cog1_entity_property.data["priority"])

        cog1_member_of_union_property.union(cog3, other_priority=0)
        cog3_entity_property = EntityProperty.query.filter_by(name=P.MEMBER_OF_UNION, entity=cog3).one()
        self.assertEqual(0, cog3_entity_property.data["priority"])

    def test_entity_union_disband(self):
        rl = RootLocation(Point(1, 1), 10)
        cog_type = LocationType("cog", 1000)

        cog1 = Location(rl, cog_type)
        cog2 = Location(rl, cog_type)
        cog3 = Location(rl, cog_type)
        cog4 = Location(rl, cog_type)
        db.session.add_all([rl, cog_type, cog1, cog2, cog3, cog4])

        cog1_member_of_union_property = properties.OptionalMemberOfUnionProperty(cog1)
        cog1_member_of_union_property.union(cog2)
        cog1_member_of_union_property.union(cog3)

        cog1_member_of_union_property.disband_union()

        number_of_union_members = EntityProperty.query.filter_by(name=P.MEMBER_OF_UNION).count()
        self.assertEqual(0, number_of_union_members)

    def test_entity_union_leave(self):
        rl = RootLocation(Point(1, 1), 10)
        cog_type = LocationType("cog", 1000)

        cog1 = Location(rl, cog_type)
        cog2 = Location(rl, cog_type)
        cog3 = Location(rl, cog_type)
        cog4 = Location(rl, cog_type)
        db.session.add_all([rl, cog_type, cog1, cog2, cog3, cog4])

        cog1_member_of_union_property = properties.OptionalMemberOfUnionProperty(cog1)
        cog1_member_of_union_property.union(cog2)
        cog1_member_of_union_property.union(cog3)

        cog1_member_of_union_property.leave_union()

        cog2_entity_property = EntityProperty.query.filter_by(name=P.MEMBER_OF_UNION, entity=cog2).one()
        cog3_entity_property = EntityProperty.query.filter_by(name=P.MEMBER_OF_UNION, entity=cog3).one()
        # cog2 and cog3 still members of the same union
        self.assertEqual(cog2_entity_property.data["union_id"], cog3_entity_property.data["union_id"])

    def test_union_split(self):
        rl = RootLocation(Point(1, 1), 10)
        cog_type = LocationType("cog", 1000)

        cog1 = Location(rl, cog_type, title="cog1")
        cog2 = Location(cog1, cog_type, title="cog2")
        cog3 = Location(cog1, cog_type, title="cog3")
        cog4 = Location(cog2, cog_type, title="cog4")
        cog5 = Location(cog1, cog_type, title="cog5")

        cog1_member_of_union_property = properties.OptionalMemberOfUnionProperty(cog1)
        cog1_member_of_union_property.union(cog2)
        cog1_member_of_union_property.union(cog3)
        cog1_member_of_union_property.union(cog4)
        cog1_member_of_union_property.union(cog5)
        db.session.add_all([rl, cog_type, cog1, cog2, cog3, cog4, cog5])

        cog1_member_of_union_property.split_union(cog2)

        cog1_union_id = cog1_member_of_union_property.get_union_id()
        self.assertEqual(self._get_union_id(cog3), cog1_union_id)
        self.assertEqual(self._get_union_id(cog5), cog1_union_id)

        self.assertEqual(self._get_union_id(cog2), self._get_union_id(cog4))

    def _get_union_id(self, entity):
        entity_property = EntityProperty.query.filter_by(entity=entity, name=P.MEMBER_OF_UNION).one()
        return entity_property.data["union_id"]

    def test_being_moved_property(self):
        rl = RootLocation(Point(1, 1), 10)
        cog_type = LocationType("cog", 1000)

        cog1 = Location(rl, cog_type)
        db.session.add_all([rl, cog_type, cog1])

        cog1_being_moved_property = properties.OptionalBeingMovedProperty(cog1)
        cog1_being_moved_property.set_movement(1, math.pi)

        cog1_entity_property = EntityProperty.query.filter_by(name=P.BEING_MOVED).one()
        self.assertEqual([1, math.pi], cog1_entity_property.data["movement"])
        self.assertNotIn("inertia", cog1_entity_property.data)

        cog1_being_moved_property.remove()

        self.assertIn(cog1_entity_property, db.session.deleted)

        cog1_being_moved_property.set_movement(1, 1.5 * math.pi)
        cog1_being_moved_property.set_inertia(3, 0.7 * math.pi)
        cog1_being_moved_property.set_inertia(0)

        cog1_entity_property = EntityProperty.query.filter_by(name=P.BEING_MOVED).one()
        self.assertEqual({"movement": [1, 1.5 * math.pi], "inertia": [0, 0]}, cog1_entity_property.data)

    def test_boardable_property(self):
        rl = RootLocation(Point(1, 1), 10)
        ships_group = TypeGroup("ships")
        cog_type = LocationType("cog", 1000)
        ships_group.add_to_group(cog_type)

        cog = Location(rl, cog_type)
        db.session.add_all([rl, cog_type, cog])

        cog_type.properties.append(EntityTypeProperty(P.BOARDABLE, {"allowed_ship_types": ["cog"]}))

        cog_boardable_property = properties.BoardableProperty(cog)
        self.assertEqual({cog_type}, cog_boardable_property.get_concrete_types_to_board_to())

    def test_in_boarding_property(self):
        rl = RootLocation(Point(1, 1), 10)
        cog_type = LocationType("cog", 1000)

        cog1 = Location(rl, cog_type)
        cog2 = Location(rl, cog_type)
        db.session.add_all([rl, cog_type, cog1, cog2])

        self.assertEqual(0, EntityProperty.query.filter_by(name=P.IN_BOARDING).count())

        cog1_in_boarding_property = properties.OptionalInBoardingProperty(cog1)
        cog2_in_boarding_property = properties.OptionalInBoardingProperty(cog2)

        cog1_in_boarding_property.append_ship_in_boarding(cog2)

        # check whether the relation is stored on both sides
        self.assertEqual({"ships_in_boarding": [cog2.id]}, cog1_in_boarding_property.entity_property.data)
        self.assertEqual({"ships_in_boarding": [cog1.id]}, cog2_in_boarding_property.entity_property.data)

        cog2_in_boarding_property.remove_ship_from_boarding(cog1)

        self.assertEqual(0, EntityProperty.query.filter_by(name=P.IN_BOARDING).count())
