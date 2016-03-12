from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core.main import db
from exeris.core.models import RootLocation, LocationType, Location, EntityTypeProperty, ObservedName, SkillType, \
    EntityProperty, \
    ItemType, Item, TextContent
# noinspection PyUnresolvedReferences
from exeris.core import properties
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



