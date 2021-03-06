import string
from unittest.mock import patch

from flask_testing import TestCase
from shapely.geometry import Point, Polygon

from exeris.core import models, map_data
from exeris.core.main import db, Types
from exeris.core.general import GameDate, SameLocationRange, NeighbouringLocationsRange, VisibilityBasedRange, \
    EventCreator, TraversabilityBasedRange, RangeSpec, Identifiers
from exeris.core.models import GameDateCheckpoint, RootLocation, Location, Item, ItemType, Passage, EntityProperty, \
    EventType, EventObserver, LocationType, PassageType, TerrainType, TerrainArea, PropertyArea, TypeGroup, \
    UniqueIdentifier
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

    def test_game_date_addition(self):
        first_date = GameDate(1000)
        second_date = GameDate(345)

        # addition of two GameDate objects
        self.assertEqual(1345, (first_date + second_date).game_timestamp)
        self.assertEqual(1345, (second_date + first_date).game_timestamp)

        # addition of GameDate with an integer
        self.assertEqual(545, (second_date + 200).game_timestamp)
        self.assertEqual(545, (200 + second_date).game_timestamp)


class RangeSpecTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_edge_wrapping(self):
        grass_type = TerrainType("grassland")
        land_terrain = TypeGroup.by_name(Types.LAND_TERRAIN)
        land_terrain.add_to_group(grass_type)

        area1_poly = Polygon([(0, 0), (0, 5), (3, 5), (3, 0)])
        area1_terrain = TerrainArea(area1_poly, grass_type)
        area1 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1,
                             area1_poly, terrain_area=area1_terrain)

        area1_poly = Polygon([(map_data.MAP_WIDTH, 0), (map_data.MAP_WIDTH, 5),
                              (map_data.MAP_WIDTH - 3, 5), (map_data.MAP_WIDTH - 3, 0)])
        area2_terrain = TerrainArea(area1_poly, grass_type)
        area2 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1,
                             area1_poly, terrain_area=area2_terrain)

        db.session.add_all([grass_type, area1_terrain, area1, area2_terrain, area2])

        rng = TraversabilityBasedRange(10)

        # wrapping on X axis
        point_a = Point(2, 2)
        point_b = Point(map_data.MAP_WIDTH - 2, 2)
        multi_line_string = rng.create_multi_line_string_for_wrapped_edges(point_a, point_b)
        line_strings = multi_line_string.geoms

        self.assertEqual([(map_data.MAP_WIDTH, 2), (map_data.MAP_WIDTH - 2, 2)], list(line_strings[0].coords))
        self.assertEqual([(2, 2), (0, 2)], list(line_strings[1].coords))

        # wrapping on Y axis
        point_a = Point(2, 2)
        point_b = Point(0.5 * map_data.MAP_WIDTH + 2, 2)
        multi_line_string = rng.create_multi_line_string_for_wrapped_edges(point_a, point_b)
        line_strings = multi_line_string.geoms

        self.assertEqual([(2, 2), (2, 0)], list(line_strings[0].coords))
        self.assertEqual([(0.5 * map_data.MAP_WIDTH + 2, 0), (0.5 * map_data.MAP_WIDTH + 2, 2)],
                         list(line_strings[1].coords))

        # wrapping on both axes  #1
        point_a = Point(2, 4)
        point_b = Point(0.5 * map_data.MAP_WIDTH - 4, 2)
        multi_line_string = rng.create_multi_line_string_for_wrapped_edges(point_a, point_b)
        line_strings = multi_line_string.geoms

        self.assertEqual([(map_data.MAP_WIDTH, 2), (map_data.MAP_WIDTH - 2, 0)], list(line_strings[0].coords))
        self.assertEqual([(2, 4), (0, 2)], list(line_strings[1].coords))
        self.assertEqual([(0.5 * map_data.MAP_WIDTH - 2, 0),
                          (0.5 * map_data.MAP_WIDTH - 4, 2)],
                         list(line_strings[2].coords))

        # wrapping on both axes  #2
        point_a = Point(0.5 * map_data.MAP_WIDTH + 2, 2)
        point_b = Point(map_data.MAP_WIDTH - 4, 2)
        multi_line_string = rng.create_multi_line_string_for_wrapped_edges(point_a, point_b)
        line_strings = multi_line_string.geoms

        self.assertEqual([(0.5 * map_data.MAP_WIDTH + 2, 2),
                          (0.5 * map_data.MAP_WIDTH - 1, 0)], list(line_strings[0].coords))

        self.assertEqual([(map_data.MAP_WIDTH - 1, 0),
                          (map_data.MAP_WIDTH - 4, 2)], list(line_strings[1].coords))

    def test_circular_area(self):
        grass_type = TerrainType("grassland")
        road_type = TerrainType("road")
        forest_type = TerrainType("forest")
        land_terrain = TypeGroup.by_name(Types.LAND_TERRAIN)
        land_terrain.add_to_group(grass_type)
        land_terrain.add_to_group(road_type)
        land_terrain.add_to_group(forest_type)

        area1_poly = Polygon([(0, 0), (0, 5), (3, 5), (3, 0)])
        area1_terrain = TerrainArea(area1_poly, grass_type)
        area1 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1,
                             area1_poly, terrain_area=area1_terrain)
        area2_poly = Polygon([(0, 5), (0, 10), (2, 10), (3, 0)])
        area2_terrain = TerrainArea(area2_poly, forest_type)
        area2 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 0.5, 1,
                             area2_poly, terrain_area=area2_terrain)
        area3_poly = Polygon([(0, 1), (0, 4), (3, 4), (3, 0)])
        area3_terrain = TerrainArea(area3_poly, road_type)
        area3 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 2, 2,
                             area3_poly, terrain_area=area3_terrain)
        area4_poly = Polygon([(0, 2), (0, 3), (3, 3), (3, 0)])
        area4_terrain = TerrainArea(area4_poly, grass_type)
        area4 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 3,
                             area4_poly, terrain_area=area4_terrain)

        db.session.add_all([area1, area2, area3, area4])
        db.session.add_all([grass_type, road_type, forest_type])

        rng = TraversabilityBasedRange(20, allowed_terrain_types=[Types.LAND_TERRAIN])

        self.assertEqual(5.5, rng.get_maximum_range_from_estimate(Point(0, 0), 90, 5, 10))  # 1 + 1 + 1 + 1 + 1 + 0.5

        self.assertEqual(5, rng.get_maximum_range_from_estimate(Point(0, 0), 90, 4, 8))  # 1 + 1 + 1 + 1 + 1 + 0.5

        self.assertEqual(1.5, rng.get_maximum_range_from_estimate(Point(0, 1), 90, 1, 2))  # 1 + 0.5

        self.assertEqual(1, rng.get_maximum_range_from_estimate(Point(0, 2), 90, 1, 2))  # 1

        self.assertEqual(2.5, rng.get_maximum_range_from_estimate(Point(0, 5), 90, 5, 10))  # 5 * 0.5

    def test_terrain_based_limitation_for_traversability(self):
        lava_type = TerrainType("lava")
        forest_type = TerrainType("forest")
        land_terrain = TypeGroup.by_name(Types.LAND_TERRAIN)
        # lava is not an element of "land terrain" group
        land_terrain.add_to_group(forest_type)

        area_poly = Polygon([(0, 0), (0, 30), (30, 30), (30, 0)])
        area1_terrain = TerrainArea(area_poly, lava_type)
        area1 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 2, 1,  # you'd run faster on lava, but you can't
                             area_poly, terrain_area=area1_terrain)

        area2_terrain = TerrainArea(area_poly, forest_type)
        area2 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 0.5, 1,
                             area_poly, terrain_area=area2_terrain)

        db.session.add_all([lava_type, forest_type, land_terrain, area1, area2, area1_terrain, area2_terrain])

        rng = TraversabilityBasedRange(20, allowed_terrain_types=[Types.LAND_TERRAIN])
        # lava would allow to pass 20 units on map, but it's not a subtype of land terrain
        self.assertEqual(5, rng.get_maximum_range_from_estimate(Point(0, 1), 0, 10, 20))

        rng = TraversabilityBasedRange(20, allowed_terrain_types=["forest"])
        # check the same again, this time terrain set explicitly
        self.assertEqual(5, rng.get_maximum_range_from_estimate(Point(0, 1), 0, 10, 20))

        rng = TraversabilityBasedRange(20, allowed_terrain_types=["lava"])
        # now we wear lava-walking boots
        self.assertEqual(20, rng.get_maximum_range_from_estimate(Point(0, 1), 0, 10, 20))

    def test_terrain_based_limitation_for_traversability_with_hole(self):
        grassland_type = TerrainType("grassland")
        land_terrain = TypeGroup.by_name(Types.LAND_TERRAIN)
        land_terrain.add_to_group(grassland_type)

        area_poly = Polygon([(5, 0), (12, 0), (12, 20), (5, 20)])

        area2_terrain = TerrainArea(area_poly, grassland_type)
        area2 = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1,
                             area_poly, terrain_area=area2_terrain)

        db.session.add_all([grassland_type, land_terrain, area2, area2_terrain])

        rng = TraversabilityBasedRange(6, allowed_terrain_types=[Types.LAND_TERRAIN])

        self.assertEqual(5, rng.get_maximum_range_from_estimate(Point(10, 1), 180, 6, 12))
        self.assertEqual(0, rng.get_maximum_range_from_estimate(Point(0, 1), 0, 6, 12))

    def test_entities_near(self):
        self.maxDiff = None

        loc_type = LocationType("building", 300)
        unlimited = PassageType("unlimited", True)

        grass_type = TerrainType("grassland")
        TypeGroup.by_name(Types.LAND_TERRAIN).add_to_group(grass_type)
        grass_poly = Polygon([(0, 0), (0, 30), (30, 30), (30, 0)])
        grass_terrain = TerrainArea(grass_poly, grass_type)
        grass_visibility_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, grass_poly, grass_terrain)
        grass_traversability_area = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, grass_poly, grass_terrain)

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

        rng = TraversabilityBasedRange(100, only_through_unlimited=True, allowed_terrain_types=[Types.LAND_TERRAIN])
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, i21_1], items)

        rng = TraversabilityBasedRange(100, only_through_unlimited=True, allowed_terrain_types=[Types.LAND_TERRAIN])
        items = rng.items_near(loc1)

        self.assertCountEqual([irl_1, i11_1, i11_2, iorl_1, io1_1], items)

        rng = TraversabilityBasedRange(100, only_through_unlimited=False, allowed_terrain_types=[Types.LAND_TERRAIN])
        items = rng.items_near(loc2)

        self.assertCountEqual([i2_1, i2_2, irl_1, i21_1, i11_1, i11_2, iorl_1, io1_1], items)

    def test_get_path_between_locations(self):
        building_type = LocationType("building", 1000)
        rl1 = RootLocation(Point(1, 1), 0)

        loc1 = Location(rl1, building_type)
        loc2 = Location(loc1, building_type)
        loc3 = Location(loc2, building_type)
        loc4 = Location(loc3, building_type)
        loc5 = Location(loc4, building_type)

        passage_from_1_to_5 = Passage(loc1, loc5)
        passage_from_1_to_5.properties.append(EntityProperty(P.CLOSEABLE, {"closed": True}))

        db.session.add_all([building_type, rl1, loc1, loc2, loc3, loc4, loc5, passage_from_1_to_5])

        self.assertEqual([loc1], RangeSpec.get_path_between_locations(loc1, loc1))
        self.assertEqual([loc1, loc2], RangeSpec.get_path_between_locations(loc1, loc2))
        self.assertEqual([loc1, loc2, loc3, loc4, loc5], RangeSpec.get_path_between_locations(loc1, loc5))


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
        psg1.type = PassageType.by_name(Types.INVISIBLE_PASSAGE)
        psg2 = Passage.query.filter(Passage.between(rl, loc2)).first()
        psg2.type = PassageType.by_name(Types.INVISIBLE_PASSAGE)
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


class IdentifiersTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_unique_identifier_property(self):
        identifiers = []
        for letter in string.ascii_uppercase:
            identifiers.append(UniqueIdentifier(letter, 0, "PLACEHOLDER"))
        db.session.add_all(identifiers)

        # all one letter identifiers are already used, so it needs to contain 2 letters
        Identifiers.MIN_LENGTH = 1
        unique_id = Identifiers.generate_unique_identifier()
        self.assertEqual(2, len(unique_id))
