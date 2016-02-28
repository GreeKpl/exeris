from unittest.mock import patch

from flask.ext.testing import TestCase
from shapely.geometry import Point, Polygon

from exeris.core import models
from exeris.core.main import db
from exeris.core.general import GameDate, SameLocationRange, NeighbouringLocationsRange, VisibilityBasedRange, \
    TraversabilityBasedRange, EventCreator
from exeris.core.models import GameDateCheckpoint, RootLocation, Location, Item, ItemType, Passage, EntityProperty, \
    EventType, EventObserver, LocationType, PassageType, TerrainType, TerrainArea, PropertyArea
from exeris.core.properties import P
from tests import util


class GameDateTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_basic_now_precision(self):
        last_checkpoint_timestamp = 1000
        checkpoint = GameDateCheckpoint(game_date=100, real_date=last_checkpoint_timestamp)
        db.session.add(checkpoint)
        with patch("exeris.core.general.GameDate._get_timestamp", new=lambda: 1100):
            now = GameDate.now()
            self.assertAlmostEqual(200, now.game_timestamp)

    def test_timestamp_to_date_conversion(self):
        date = GameDate(3600 * 48 * 14 * 5 + 3600 * 48 * 3 + 3600 * 30 + 60 * 17 + 33)
        # 5-3-11:17:33
        self.assertEqual(33, date.second)
        self.assertEqual(17, date.minute)
        self.assertEqual(6, date.hour)
        self.assertEqual(7, date.day)
        self.assertEqual(5, date.moon)

        self.assertAlmostEqual(0.2621, date.sun_progression, places=3)
        self.assertAlmostEqual(0.25936, date.moon_progression, places=3)

        # check if it's  the day
        self.assertTrue(date.is_day)

    def test_date_objects_comparison(self):
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


class RangeSpecTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_circular_area(self):
        grass_type = TerrainType("grass")
        road_type = TerrainType("road")
        forest_type = TerrainType("forest")

        area1 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1,
                             Polygon([(0, 0), (0, 5), (3, 5), (3, 0), (0, 0)]))
        area2 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 0.5, 1,
                             Polygon([(0, 5), (0, 10), (2, 10), (3, 0), (0, 5)]))
        area3 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 2, 2,
                             Polygon([(0, 1), (0, 4), (3, 4), (3, 0), (0, 1)]))
        area4 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 3,
                             Polygon([(0, 2), (0, 3), (3, 3), (3, 0), (0, 2)]))

        db.session.add_all([area1, area2, area3, area4])
        db.session.add_all([grass_type, road_type, forest_type])

        rng = TraversabilityBasedRange(20)

        self.assertEqual(5.5, rng.get_real_range_from_estimate(Point(0, 0), 0, 5, 10))  # 1 + 1 + 1 + 1 + 1 + 0.5

        self.assertEqual(5, rng.get_real_range_from_estimate(Point(0, 0), 0, 4, 8))  # 1 + 1 + 1 + 1 + 1 + 0.5

        self.assertEqual(1.5, rng.get_real_range_from_estimate(Point(0, 1), 0, 1, 2))  # 1 + 0.5

        self.assertEqual(1, rng.get_real_range_from_estimate(Point(0, 2), 0, 1, 2))  # 1

        self.assertEqual(2.5, rng.get_real_range_from_estimate(Point(0, 5), 0, 5, 10))  # 5 * 0.5

    def test_entities_near(self):
        self.maxDiff = None

        loc_type = LocationType("building", 300)
        unlimited = PassageType("unlimited", True)

        grass_type = TerrainType("grass")
        grass_poly = Polygon([(0, 0), (0, 30), (30, 30), (30, 0)])
        grass_terrain = TerrainArea(grass_poly, grass_type)
        grass_visibility_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, grass_poly)
        grass_traversability_area = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, grass_poly)

        db.session.add_all([grass_type, grass_terrain, grass_visibility_area, grass_traversability_area])

        rl = RootLocation(Point(10, 20), 122)
        loc1 = Location(rl, loc_type, unlimited)
        loc2 = Location(rl, loc_type)
        loc11 = Location(loc1, loc_type, unlimited)
        loc12 = Location(loc1, loc_type)
        loc21 = Location(loc2, loc_type, unlimited)
        loc22 = Location(loc2, loc_type)

        loc221 = Location(loc22, loc_type, unlimited)

        orl = RootLocation(Point(20, 20), 100)
        oloc1 = Location(orl, loc_type, unlimited)
        db.session.add_all([rl, loc_type, loc1, loc2, loc11, loc12, loc21, loc22, loc221, orl, oloc1])

        knife_type = ItemType("knife", 300)
        db.session.add(knife_type)

        irl_1 = Item(knife_type, rl, weight=381)

        i2_1 = Item(knife_type, loc2, weight=100)
        i2_2 = Item(knife_type, loc2, weight=130)

        i22_1 = Item(knife_type, loc22, weight=130)

        i11_1 = Item(knife_type, loc11, weight=100)
        i11_2 = Item(knife_type, loc11, weight=100)

        i21_1 = Item(knife_type, loc21, weight=100)

        i221_1 = Item(knife_type, loc221, weight=123)

        iorl_1 = Item(knife_type, orl, weight=123)
        io1_1 = Item(knife_type, oloc1, weight=123)

        db.session.add_all([irl_1, i2_1, i2_2, i11_1, i11_2, i21_1, i22_1, i221_1, iorl_1, io1_1])

        rl_loc2_psg = Passage.query.filter(Passage.between(rl, loc2)).first()
        loc2_loc22_psg = Passage.query.filter(Passage.between(loc2, loc22)).first()
        loc1_loc12_psg = Passage.query.filter(Passage.between(loc1, loc12)).first()

        db.session.add_all([EntityProperty(entity=rl_loc2_psg, name=P.CLOSEABLE, data={"closed": False})])
        db.session.add_all([EntityProperty(entity=loc2_loc22_psg, name=P.CLOSEABLE, data={"closed": True})])
        db.session.add_all([EntityProperty(entity=loc1_loc12_psg, name=P.CLOSEABLE, data={"closed": True})])

        # items in the same location
        rng = SameLocationRange()
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2], items)

        # items in the same and neighbouring locations

        rng = NeighbouringLocationsRange(only_through_unlimited=False)
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2], items)

        rng = NeighbouringLocationsRange(only_through_unlimited=True)
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, i21_1], items)

        rng = VisibilityBasedRange(100)
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2, iorl_1, io1_1], items)

        rng = VisibilityBasedRange(5)
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2], items)

        rng = TraversabilityBasedRange(100, only_through_unlimited=True)
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, i21_1], items)

        rng = TraversabilityBasedRange(100, only_through_unlimited=True)
        items = rng.items_near(loc1)

        self.assertCountEqual([irl_1, i11_1, i11_2, iorl_1, io1_1], items)

        rng = TraversabilityBasedRange(100, only_through_unlimited=False)
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2, iorl_1, io1_1], items)


class EventCreatorTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_event_creation(self):
        util.initialize_date()

        et1 = EventType("slap_doer", EventType.IMPORTANT)
        et2 = EventType("slap_target", EventType.IMPORTANT)
        et3 = EventType("slap_observer", EventType.NORMAL)
        unlimited = PassageType("unlimited", True)
        db.session.add_all([et1, et2, et3])

        rl = RootLocation(Point(10, 10), 103)
        loc_type = LocationType("building", 200)
        loc1 = Location(rl, loc_type, unlimited)
        loc2 = Location(rl, loc_type, unlimited)

        plr = util.create_player("plr1")
        doer = util.create_character("doer", loc1, plr)
        target = util.create_character("target", loc2, plr)
        observer = util.create_character("observer", loc2, plr)

        db.session.add_all([rl, loc_type, loc1, loc2, doer, target, observer])

        db.session.flush()

        EventCreator.base("slap", doer=doer, target=target,
                          rng=VisibilityBasedRange(100), params={"hi": "hehe"})

        event_doer = EventObserver.query.filter_by(observer=doer).one()
        self.assertEqual(et1, event_doer.event.type)
        self.assertEqual({"hi": "hehe", "groups": {
            "target": target.pyslatize()
        }}, event_doer.event.params)

        event_target = EventObserver.query.filter_by(observer=target).one()
        self.assertEqual(et2, event_target.event.type)
        self.assertEqual({"hi": "hehe", "groups": {
            "doer": doer.pyslatize()
        }}, event_target.event.params)

        event_obs = EventObserver.query.filter_by(observer=observer).one()
        self.assertEqual(et3, event_obs.event.type)
        self.assertEqual({"hi": "hehe", "groups": {
            "doer": doer.pyslatize(),
            "target": target.pyslatize()
        }}, event_obs.event.params)


def test_event_for_observer_in_targets_location(self):
    util.initialize_date()

    et1 = EventType("slap_doer", EventType.IMPORTANT)
    et2 = EventType("slap_target", EventType.IMPORTANT)
    et3 = EventType("slap_observer", EventType.NORMAL)
    db.session.add_all([et1, et2, et3])

    rl = RootLocation(Point(10, 10), 103)
    unlimited = PassageType("unlimited", True)
    loc_type = LocationType("building", 200)
    loc1 = Location(rl, loc_type, unlimited)
    loc2 = Location(rl, loc_type, unlimited)

    plr = util.create_player("plr1")
    doer = util.create_character("doer", loc1, plr)
    target = util.create_character("target", loc2, plr)
    observer = util.create_character("observer", loc2, plr)
    observer_in_root_loc = util.create_character("observer_too_far_away", rl, plr)

    db.session.add_all([rl, loc_type, loc1, loc2])

    psg1 = Passage.query.filter(Passage.between(rl, loc1)).first()
    psg1.properties.append(EntityProperty(P.unlimited))
    psg2 = Passage.query.filter(Passage.between(rl, loc2)).first()
    psg2.properties.append(EntityProperty(P.unlimited))
    db.session.add_all([psg1, psg2])

    EventCreator.base("slap", doer=doer, target=target,
                      rng=SameLocationRange())

    event_doer = EventObserver.query.filter_by(observer=doer).one()
    self.assertEqual(et1, event_doer.event.type)

    event_target = EventObserver.query.filter_by(observer=target).one()
    self.assertEqual(et2, event_target.event.type)

    event_obs = EventObserver.query.filter_by(observer=observer).one()
    self.assertEqual(et3, event_obs.event.type)

    observer_in_root_loc_count = EventObserver.query.filter_by(observer=observer_in_root_loc).count()
    self.assertEqual(0, observer_in_root_loc_count)
