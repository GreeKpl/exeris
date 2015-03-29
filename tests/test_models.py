import datetime
from flask.ext.testing import TestCase
from pygeoif import Point, geometry
import time

from exeris.core.main import GameDate, db
from exeris.core.map import MAP_HEIGHT, MAP_WIDTH
from exeris.core.models import GameDateCheckpoint, RootLocation, Location, Item, EntityProperty, EntityTypeProperty, \
    ItemType, Character, Player, Entity
from exeris.core import properties
from exeris.core.properties import EntityPropertyException
from tests import util


class LocationTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_insert_basic(self):
        pos = Point(10, 20)
        root_loc = RootLocation(pos, False, 100)  # the simplest
        db.session.add(root_loc)

        root_loc2 = RootLocation(pos, False, 370)  # normalize direction
        self.assertEqual(10, root_loc2.direction)
        db.session.add(root_loc2)
        self.assertEqual(10, root_loc2.direction)

    def test_insert_validate_position(self):
        pos = Point(MAP_WIDTH + 20, 30)
        root_loc = RootLocation(pos, False, 30)  # normalize position
        db.session.add(root_loc)

        self.assertAlmostEqual(20, root_loc.position.x, places=6)
        self.assertAlmostEqual(30, root_loc.position.y, places=6)

        pos2 = Point(20, MAP_HEIGHT + 30)
        root_loc2 = RootLocation(pos2, False, 30)  # normalize position
        db.session.add(root_loc2)

        self.assertAlmostEqual(MAP_WIDTH / 2 + 20, root_loc2.position.x, places=6)
        self.assertAlmostEqual(MAP_HEIGHT - 30, root_loc2.position.y, places=6)

    def test_find_position(self):
        pos = Point(10, 20)
        root_loc = RootLocation(pos, False, 100)  # the simplest
        db.session.add(root_loc)

        good_query_results = db.session.query(RootLocation).filter_by(position=Point(10, 20).to_wkt()).all()
        bad_query_results = db.session.query(RootLocation).filter_by(position=Point(20, 20).to_wkt()).all()

        self.assertEqual(1, len(good_query_results))
        self.assertEqual(0, len(bad_query_results))

    def test_find_root(self):
        pos = Point(10, 20)
        root_loc = RootLocation(pos, False, 100)  # the simplest
        db.session.add(root_loc)

        farmyard = Location(root_loc, 0)
        db.session.add(farmyard)

        building = Location(farmyard, 0)
        db.session.add(building)

        room = Location(building, 0)
        db.session.add(room)

        self.assertEqual(root_loc, room.get_root())

    def test_methods__get_inside(self):
        print("#######")
        print(Entity.is_in)
        print("#######")
        root_loc = RootLocation(Point(20, 20), False, 100)
        loc = Location(root_loc, 100)

        db.session.add_all([root_loc, loc])

        # items
        type1 = ItemType("sword")
        item1 = Item(type1, loc, 200)
        item2 = Item(type1, loc, 300)

        db.session.add(type1)
        db.session.add_all([item1, item2])

        self.assertCountEqual([item1, item2], loc.get_items_inside())

        plr = Player(login="jan", email="aa@gmail.com", register_date=datetime.datetime.now(), register_game_date=GameDate(1000),
                     sex=Player.SEX_MALE, password="ala123")

        # characters
        ch1 = Character("Janusz", Character.SEX_MALE, plr, GameDate(1200), Point(10, 20), loc)

        db.session.add(plr)
        db.session.add(ch1)

        self.assertCountEqual([ch1], loc.get_characters_inside())

    tearDown = util.tear_down_rollback


class EntityTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_property_call_by_property(self):

        @properties.property_class
        class HappyPropertyType(properties.PropertyType):
            __property__ = "Happy"
            @properties.property_method
            def be_happy(self):
                pass

        item_type = ItemType("sickle")

        item = Item(item_type, None, 100)
        prop = EntityProperty(entity=item, name="Happy", data={})
        db.session.add(prop)

        item.be_happy()  # item has property enabling the method, so it should be possible to call it

        item2 = Item(item_type, None, 200)
        type_prop = EntityTypeProperty(type=item_type, name="Happy", data={})
        db.session.add(type_prop)

        item2.be_happy()  # item has property enabling the method, so it should be possible to call it

        db.session.delete(type_prop)

        self.assertRaises(EntityPropertyException, item2.be_happy)

    tearDown = util.tear_down_rollback

