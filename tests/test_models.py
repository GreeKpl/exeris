from flask.ext.testing import TestCase
from pygeoif import Point, geometry

from exeris.core.main import GameDate, db
from exeris.core.map import MAP_HEIGHT, MAP_WIDTH
from exeris.core.models import GameDateCheckpoint, RootLocation
from tests import util


class RootLocationTest(TestCase):

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

    tearDown = util.tear_down_rollback