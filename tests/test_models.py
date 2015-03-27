from flask.ext.testing import TestCase
from pygeoif import Point, geometry

from exeris.core.main import GameDate, db
from exeris.core.map import MAP_HEIGHT, MAP_WIDTH
from exeris.core.models import GameDateCheckpoint, RootLocation, Location, Item, EntityProperty, EntityTypeProperty, \
    ItemType
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

        good_query_results = db.session.query(RootLocation).filter(RootLocation.position==Point(10, 20).to_wkt()).all()
        bad_query_results = db.session.query(RootLocation).filter(RootLocation.position==Point(20, 20).to_wkt()).all()

        self.assertEqual(1, len(good_query_results))
        self.assertEqual(0, len(bad_query_results))

    def test_find_root(self):
        pos = Point(10, 20)
        root_loc = RootLocation(pos, False, 100)  # the simplest
        db.session.add(root_loc)

        farmyard = Location(0, root_loc)
        db.session.add(farmyard)

        building = Location(0, farmyard)
        db.session.add(building)

        room = Location(0, building)
        db.session.add(room)

        self.assertEqual(root_loc, room.get_root())

    tearDown = util.tear_down_rollback


class EntityTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_property_call_by_property(self):

        @properties.property_methods
        class HappyPropertyType(properties.PropertyType):
            __property__ = "Happy"
            @properties.registered
            def be_happy(entity):
                pass

        item_type = ItemType()

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
