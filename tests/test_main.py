from unittest.mock import patch

from flask.ext.testing import TestCase
from pygeoif import Point

from exeris.core.main import db, GameDate, SameLocationRange, NeighbouringLocationsRange
from exeris.core.models import GameDateCheckpoint, RootLocation, Location, Item, ItemType
from tests import util


class GameDateTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_basic(self):
        last_checkpoint_timestamp = 1000
        checkpoint = GameDateCheckpoint(game_date=100, real_date=last_checkpoint_timestamp)
        db.session.add(checkpoint)
        with patch("exeris.core.main.GameDate._get_timestamp", new=lambda: 1100):
            now = GameDate.now()
            self.assertAlmostEqual(200, now.game_timestamp)  # non-deterministic in a slow environment!!!

    def test_params(self):
        date = GameDate(3600 * 48 * 14 * 5 + 3600 * 48 * 3 + 3600 * 30 + 60 * 17 + 33)
        # 5-3-11:17:33
        self.assertEqual(33, date.second)
        self.assertEqual(17, date.minute)
        self.assertEqual(30, date.hour)
        self.assertEqual(3, date.sol)
        self.assertEqual(5, date.moon)

        self.assertAlmostEqual(0.631, date.sol_progression, places=3)
        self.assertAlmostEqual(0.25936, date.moon_progression, places=3)

        # check if it's night
        self.assertTrue(date.after_twilight)

    def test_comparisons(self):
        old = GameDate(1000)
        new = GameDate(1100)
        like_old = GameDate(1000)

        self.assertTrue(old < new)
        self.assertTrue(old <= new)
        self.assertFalse(old > new)
        self.assertFalse(old >= new)
        self.assertFalse(old == new)
        self.assertTrue(old != new)

        self.assertTrue(old == like_old)
        self.assertFalse(old != like_old)

    tearDown = util.tear_down_rollback


class RangeSpecTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_simple_search(self):
        rl = RootLocation(Point(10, 20), False, 122)
        loc1 = Location(rl, 100)
        loc2 = Location(rl, 100)
        loc11 = Location(loc1, 200)
        loc12 = Location(loc1, 200)
        loc22 = Location(loc2, 300)

        loc221 = Location(loc22, 300)
        db.session.add_all([rl, loc1, loc2, loc11, loc12, loc22])

        knife_type = ItemType("knife")
        db.session.add(knife_type)

        irl_1 = Item(knife_type, rl, 381)

        i2_1 = Item(knife_type, loc2, 100)
        i2_2 = Item(knife_type, loc2, 130)

        i22_1 = Item(knife_type, loc22, 130)

        i11_1 = Item(knife_type, loc11, 100)
        i11_2 = Item(knife_type, loc11, 100)

        i221_1 = Item(knife_type, loc221, 123)

        db.session.add_all([irl_1, i2_1, i2_2, i11_1, i11_2, i22_1, i221_1])

        # items in the same location
        rng = SameLocationRange(loc2)
        items = rng.items_near()

        self.assertCountEqual([i2_1, i2_2], items)

        # items in the same and neighbouring locations

        rng = NeighbouringLocationsRange(loc2)
        items = rng.items_near()

        self.assertCountEqual([i2_1, i2_2, irl_1, i22_1], items)

    tearDown = util.tear_down_rollback