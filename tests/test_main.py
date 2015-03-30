from unittest.mock import patch

from flask.ext.testing import TestCase
from pygeoif import Point

from exeris.core.main import db, GameDate, SameLocationRange, NeighbouringLocationsRange, VisibilityBasedRange, \
    TraversabilityBasedRange
from exeris.core.models import GameDateCheckpoint, RootLocation, Location, Item, ItemType, Passage, EntityProperty
from exeris.core.properties import P
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

    def test_entities_near(self):
        self.maxDiff = None

        rl = RootLocation(Point(10, 20), False, 122)
        loc1 = Location(rl, 100)
        loc2 = Location(rl, 100)
        loc11 = Location(loc1, 200)
        loc12 = Location(loc1, 200)
        loc21 = Location(loc2, 300)
        loc22 = Location(loc2, 300)

        loc221 = Location(loc22, 300)

        orl = RootLocation(Point(20, 20), False, 100)
        oloc1 = Location(orl, 231)
        db.session.add_all([rl, loc1, loc2, loc11, loc12, loc21, loc22, loc221, orl, oloc1])

        knife_type = ItemType("knife")
        db.session.add(knife_type)

        irl_1 = Item(knife_type, rl, 381)

        i2_1 = Item(knife_type, loc2, 100)
        i2_2 = Item(knife_type, loc2, 130)

        i22_1 = Item(knife_type, loc22, 130)

        i11_1 = Item(knife_type, loc11, 100)
        i11_2 = Item(knife_type, loc11, 100)

        i21_1 = Item(knife_type, loc21, 100)

        i221_1 = Item(knife_type, loc221, 123)

        iorl_1 = Item(knife_type, orl, 123)
        io1_1 = Item(knife_type, oloc1, 123)

        db.session.add_all([irl_1, i2_1, i2_2, i11_1, i11_2, i21_1, i22_1, i221_1, iorl_1, io1_1])

        loc2_loc21_psg = Passage.query.filter(Passage.between(loc2, loc21)).first()
        rl_loc1_psg = Passage.query.filter(Passage.between(rl, loc1)).first()
        rl_loc2_psg = Passage.query.filter(Passage.between(rl, loc2)).first()
        loc1_loc11_psg = Passage.query.filter(Passage.between(loc1, loc11)).first()
        loc22_loc221_psg = Passage.query.filter(Passage.between(loc22, loc221)).first()
        orl_oloc1_psg = Passage.query.filter(Passage.between(orl, oloc1)).first()

        db.session.add_all([EntityProperty(entity=rl_loc2_psg, name=P.WINDOW, data={"open": True}),
                            EntityProperty(entity=loc2_loc21_psg, name=P.OPEN_PASSAGE),
                            EntityProperty(entity=rl_loc1_psg, name=P.OPEN_PASSAGE),
                            EntityProperty(entity=loc1_loc11_psg, name=P.OPEN_PASSAGE),
                            EntityProperty(entity=loc22_loc221_psg, name=P.OPEN_PASSAGE),
                            EntityProperty(entity=orl_oloc1_psg, name=P.OPEN_PASSAGE),

                            ])

        # items in the same location
        rng = SameLocationRange(loc2)
        items = rng.items_near()

        self.assertCountEqual([i2_1, i2_2], items)

        # items in the same and neighbouring locations

        rng = NeighbouringLocationsRange(loc2)
        items = rng.items_near()

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1], items)

        rng = VisibilityBasedRange(loc2, 100)
        items = rng.items_near()

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2, iorl_1, io1_1], items)

        rng = VisibilityBasedRange(loc2, 5)
        items = rng.items_near()

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2], items)

        rng = TraversabilityBasedRange(loc2, 100)
        items = rng.items_near()

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2, iorl_1, io1_1], items)



    tearDown = util.tear_down_rollback