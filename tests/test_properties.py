from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core.main import db
from exeris.core.models import RootLocation, LocationType, Location, EntityTypeProperty, ObservedName, SkillType, \
    EntityProperty, \
    ItemType, Item, TextContent
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
        building.set_dynamic_name(doer, "Krakow")

        # check if name is really changed
        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Krakow", new_name.name)

        # change the existing name
        building.set_dynamic_name(doer, "Wroclaw")

        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Wroclaw", new_name.name)

    def test_get_and_alter_skill_success(self):
        rl = RootLocation(Point(1, 1), 111)
        char = util.create_character("ABC", rl, util.create_player("wololo"))

        char.properties.append(EntityProperty(P.SKILLS, {}))

        db.session.add_all([rl, SkillType("baking", "cooking"),
                            SkillType("frying", "cooking")])
        db.session.flush()

        self.assertAlmostEqual(0.1, char.get_raw_skill("baking"))

        char.alter_skill_by("frying", 0.2)  # 0.1 changed by 0.2 means 0.3 frying

        self.assertAlmostEqual(0.1, char.get_raw_skill("baking"))
        self.assertAlmostEqual(0.3, char.get_raw_skill("frying"))

        self.assertAlmostEqual(0.2, char.get_skill_factor("frying"))  # mean value of 0.1 cooking and 0.3 frying = 0.2


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

        self.assertEqual("", book.read_title())
        self.assertEqual("", book.read_contents())

        book.alter_contents("NEW TITLE", "NEW TEXT", TextContent.FORMAT_MD)

        self.assertEqual("NEW TITLE", book.read_title())
        self.assertEqual("<p>NEW TEXT</p>", book.read_contents())
        self.assertEqual("NEW TEXT", book.read_raw_contents())

        book.alter_contents("NEW TITLE", "**abc** hehe", TextContent.FORMAT_MD)
        self.assertEqual("<p><strong>abc</strong> hehe</p>", book.read_contents())
        self.assertEqual("**abc** hehe", book.read_raw_contents())


class CharacterPropertiesTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_line_of_sight_property_to_affect_visibility_based_range(self):
        rl = RootLocation(Point(1, 1), 122)
        char = util.create_character("test1", rl, util.create_player("ala123"))

        db.session.add_all([rl])

        self.assertEqual(10, char.get_line_of_sight())

        spyglass_type = ItemType("spyglass", 300)
        spyglass_type.properties.append(EntityTypeProperty(P.AFFECT_LINE_OF_SIGHT, data={"multiplier": 3}))
        spyglass = Item(spyglass_type, char)

        db.session.add_all([spyglass_type, spyglass])

        self.assertEqual(30, char.get_line_of_sight())

    def test_mobile_property_to_affect_land_traversability_based_range(self):
        rl = RootLocation(Point(1, 1), 122)
        char = util.create_character("test1", rl, util.create_player("ala123"))

        cart_type = LocationType("cart", 500)
        cart_type.properties.append(EntityTypeProperty(P.MOBILE, data={"speed": 20}))
        cart = Location(rl, cart_type)

        db.session.add_all([rl, cart_type, cart])

        self.assertEqual(10, char.get_max_speed())

        self.assertEqual(20, cart.get_max_speed())

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

        char.set_preferred_equipment_part(coat)
        char.set_preferred_equipment_part(wooden_shield)
        char.set_preferred_equipment_part(jacket)

        self.assertCountEqual({main.EqParts.BODY: jacket, main.EqParts.SHIELD: wooden_shield}, char.get_equipment())

        char.set_preferred_equipment_part(two_handed_sword)

        # wooden shield is blocked by a two handed sword
        self.assertCountEqual({main.EqParts.BODY: jacket, main.EqParts.WEAPON: two_handed_sword}, char.get_equipment())
