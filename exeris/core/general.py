import collections
import copy
import logging
import math
import random
import string
import time
from collections import deque

import itertools
import shapely
import sqlalchemy as sql
from geoalchemy2.shape import to_shape
from shapely import affinity
from shapely.geometry import LineString, MultiLineString, Point, Polygon

from exeris.core import models, main, util, map_data
from exeris.core.main import db

logger = logging.getLogger(__name__)

# monkey-patch math module to contain function from python3.5
math.isclose = lambda a, b, rel_tol=1e-09, abs_tol=0.0: abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class GameDate:
    """
    Class handling in-game date and in-game time intervals. It can be used to get current in-game time (NOW), and also
    perform basic addition and compare operations.
    1 minute = 60 seconds, 1 hour = 60 minutes, 1 day = 24 hours (odd days mean sunlight, even are night), 1 moon = 14 days
    """

    SEC_IN_MIN = 60
    MIN_IN_HOUR = 60
    HOUR_IN_DAY = 24
    DAYLIGHT_HOURS = 24
    DAY_IN_MOON = 28

    SEC_IN_HOUR = SEC_IN_MIN * MIN_IN_HOUR
    SEC_IN_DAY = SEC_IN_HOUR * HOUR_IN_DAY
    SEC_IN_MOON = SEC_IN_DAY * DAY_IN_MOON

    def __init__(self, game_timestamp):
        self.game_timestamp = game_timestamp
        self.second, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.SEC_IN_MIN)

        self.minute, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.MIN_IN_HOUR)

        self.hour, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.HOUR_IN_DAY)

        self.day, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.DAY_IN_MOON)

        self.is_night = self.day >= GameDate.DAYLIGHT_HOURS
        self.is_day = not self.is_night

        self.moon = game_timestamp

        self.sun_progression = (self.game_timestamp % GameDate.SEC_IN_DAY) / GameDate.SEC_IN_DAY

        self.moon_progression = (self.game_timestamp % GameDate.SEC_IN_MOON) / GameDate.SEC_IN_MOON

    def __get_modulo_and_divided(self, dividend, divisor):
        return dividend % divisor, dividend // divisor

    @classmethod
    def from_date(cls, moon, day, hour=0, minute=0, second=0):
        timestamp = moon * cls.SEC_IN_MOON + day * cls.SEC_IN_DAY + \
                    hour * cls.MIN_IN_HOUR * cls.SEC_IN_MIN + minute * cls.SEC_IN_MIN + second
        return GameDate(timestamp)

    @staticmethod
    def now():
        last_date_point = models.GameDateCheckpoint.query.one()
        now_timestamp = GameDate._get_timestamp()

        real_timestamp_base = last_date_point.real_date
        game_timestamp_base = last_date_point.game_date

        real_time_difference = int(now_timestamp) - real_timestamp_base
        return GameDate(game_timestamp_base + real_time_difference)  # 1 sec in game = 1 rl sec

    @staticmethod
    def _get_timestamp():
        return time.time()

    # comparison operators
    __lt__ = lambda self, other: self.game_timestamp < other.game_timestamp
    __le__ = lambda self, other: self.game_timestamp <= other.game_timestamp
    __eq__ = lambda self, other: self.game_timestamp == other.game_timestamp
    __ne__ = lambda self, other: self.game_timestamp != other.game_timestamp
    __ge__ = lambda self, other: self.game_timestamp >= other.game_timestamp
    __gt__ = lambda self, other: self.game_timestamp > other.game_timestamp

    def __add__(self, other):
        if hasattr(other, "game_timestamp"):
            return GameDate(self.game_timestamp + other.game_timestamp)
        return GameDate(self.game_timestamp + other)

    def __radd__(self, other):
        return self + other


class RangeSpec:
    def characters_near(self, entity):
        locs = []
        for loc in self._locationize(entity):
            locs += self.locations_near(loc)
        return models.Character.query.filter(models.Character.is_in(locs), models.Character.is_alive).all()

    def items_near(self, entity):
        locs = []
        for loc in self._locationize(entity):
            locs += self.locations_near(loc)
        return models.Item.query.filter(models.Item.is_in(locs)).all()

    def root_locations_near(self, entity):
        locs = []
        for loc in self._locationize(entity):
            locs += self.locations_near(loc)
        return [loc for loc in locs if isinstance(loc, models.RootLocation)]

    def locations_near(self, entity):
        raise NotImplementedError  # abstract

    def is_near(self, entity_a, entity_b):
        """
        Checks whether entity_a has access to entity_b.
        :param entity_a:
        :param entity_b:
        :return:
        """
        try:
            for a in self._locationize(entity_a):
                locations_near_a = self.locations_near(a)
                return any([True for b in self._locationize(entity_b) if b in locations_near_a])
        except Exception as e:
            logger.debug("Exception when checking is_near(%s, %s): %s", entity_a, entity_b, e)
            return False

    def _locationize(self, entity):
        """
        Gets entity's location or returns itself if entity is a location
        :param entity: entity whose direct location(s) need to be found
        :return: list of locations
        """

        if isinstance(entity, models.Activity):
            entity = entity.being_in
        if isinstance(entity, models.Passage):
            return [entity.left_location, entity.right_location]

        if isinstance(entity, models.Location):
            return [entity]

        if not entity:
            return []

        entity = entity.being_in

        if isinstance(entity, models.Location):
            return [entity]
        return [entity.being_in]

    @staticmethod
    def get_path_between_locations(loc1, loc2, only_through_unlimited=False):
        if loc1 == loc2:
            return [loc1]

        if loc1.get_root() == loc2.get_root():
            passages_all = loc1.passages_to_neighbours
            passages_left = deque([[direct_neighbour] for direct_neighbour in passages_all])
            number_of_door_passed = {loc1: 0}
            visited_locations = {loc1}
            while len(passages_left):
                directed_passage_path_list = passages_left.popleft()
                farthest_directed_passage = directed_passage_path_list[-1]
                if farthest_directed_passage.passage.is_accessible(only_through_unlimited=only_through_unlimited):
                    if farthest_directed_passage.other_side == loc2:  # found the path
                        return [p.own_side for p in directed_passage_path_list] + [loc2]
                    if farthest_directed_passage.other_side not in visited_locations:
                        number_of_door_passed[farthest_directed_passage.other_side] = number_of_door_passed[
                            farthest_directed_passage.own_side]
                        if not farthest_directed_passage.passage.type.unlimited:
                            number_of_door_passed[farthest_directed_passage.other_side] += 1
                        visited_locations.add(farthest_directed_passage.other_side)
                        new_passages = farthest_directed_passage.other_side.passages_to_neighbours
                        passages_left.extend([directed_passage_path_list + [p]
                                              for p in new_passages if p.other_side not in visited_locations])
            raise ValueError("it's impossible to go from {} to {} with given criteria".format(loc1, loc2))
        else:
            path_from_loc1_to_root = RangeSpec._path_to_root_location(loc1)
            path_from_root_to_loc2 = list(reversed(RangeSpec._path_to_root_location(loc2)))
            return path_from_loc1_to_root + path_from_root_to_loc2

    @staticmethod
    def _path_to_root_location(loc):
        path_to_root = [loc]
        while not isinstance(path_to_root[-1], models.RootLocation):
            path_to_root.append(path_to_root[-1].being_in)
        return path_to_root


class InsideRange(RangeSpec):
    def locations_near(self, entity):
        return []

    def characters_near(self, entity):
        return []

    def items_near(self, entity):
        return models.Item.query.filter(models.Item.is_in(entity)).all()  # will be recursive

    def is_near(self, entity_a, entity_b, strict=True):
        return entity_b.being_in == entity_a


class SameLocationRange(RangeSpec):
    def locations_near(self, entity):
        if isinstance(entity, models.Location):
            return [entity]
        if isinstance(entity, models.Passage):
            return [entity.left_location, entity.right_location]
        return [entity.being_in]


class NeighbouringLocationsRange(RangeSpec):
    def __init__(self, only_through_unlimited):
        self.only_through_unlimited = only_through_unlimited

    def locations_near(self, entity):
        loc = self._locationize(entity)[0]
        return visit_subgraph(loc, self.only_through_unlimited)


class AdjacentLocationsRange(RangeSpec):
    def __init__(self, only_through_unlimited):
        self.only_through_unlimited = only_through_unlimited

    def locations_near(self, entity):
        loc = self._locationize(entity)[0]
        return [loc] + [psg.other_side for psg in loc.passages_to_neighbours
                        if psg.passage.is_accessible(self.only_through_unlimited)]


def visit_subgraph(node, only_through_unlimited=False):
    passages_all = node.passages_to_neighbours
    passages_left = deque(passages_all)
    number_of_door_passed = {node: 0}
    visited_locations = {node}
    while len(passages_left):
        directed_passage = passages_left.popleft()
        if directed_passage.passage.is_accessible(only_through_unlimited=only_through_unlimited):
            if directed_passage.other_side not in visited_locations:
                number_of_door_passed[directed_passage.other_side] = number_of_door_passed[directed_passage.own_side]
                if not directed_passage.passage.type.unlimited:
                    number_of_door_passed[directed_passage.other_side] += 1
                visited_locations.add(directed_passage.other_side)
                new_passages = directed_passage.other_side.passages_to_neighbours
                passages_left.extend([p for p in new_passages if p.other_side not in visited_locations])
    return {loc for loc in visited_locations if number_of_door_passed[loc] <= 2}


class AreaRangeSpec(RangeSpec):
    def __init__(self, travel_credits, only_through_unlimited=False, allowed_terrain_types=None):
        """
        Abstract class for creating all area-based range specifications (Visibility, Traversability)
        which is based on distance on map between RootLocations. It also visits all the locations in every RootLocation
        :param travel_credits: max allowed travel credits cost from from the center
        :param only_through_unlimited: true when only "unlimited" passages between Locations should be passed (not door)
        :param allowed_terrain_types: list of terrain type names (or group names) which should be passable.
            Defaults to any terrain type.
        :return: object of specific subclass
        """
        self.distance = travel_credits
        self.only_through_unlimited = only_through_unlimited
        if allowed_terrain_types:
            self.allowed_terrain_types = [models.EntityType.by_name(terrain_type)
                                          if isinstance(terrain_type, str) else terrain_type
                                          for terrain_type in allowed_terrain_types]
        else:
            self.allowed_terrain_types = [models.EntityType.by_name(main.Types.ANY_TERRAIN)]

    def locations_near(self, entity):
        locs = visit_subgraph(entity, self.only_through_unlimited)

        roots = [r for r in locs if isinstance(r, models.RootLocation)]

        assert len(roots) <= 1

        if len(roots):
            root = roots[0]

            max_estimated_distance = self.MAX_RANGE_MULTIPLIER * self.distance

            wrapped_point_clauses = self.get_clauses_for_points_wrapped_around_map_edges(max_estimated_distance, root)

            other_locs = models.RootLocation.query. \
                filter(sql.or_(*wrapped_point_clauses)). \
                filter(models.RootLocation.id != root.id).all()  # get RootLocations in big circle

            for other_loc in other_locs:

                direction_from_center = util.direction_degrees(root.position, other_loc.position)
                distance_to_point = util.distance(root.position, other_loc.position)

                maximum_accessible_range = self.get_maximum_range_from_estimate(root.position,
                                                                                direction_from_center,
                                                                                self.distance, distance_to_point)

                if maximum_accessible_range > distance_to_point or math.isclose(maximum_accessible_range,
                                                                                distance_to_point):
                    locs.update(visit_subgraph(other_loc, self.only_through_unlimited))

        return locs

    def get_clauses_for_points_wrapped_around_map_edges(self, max_estimated_distance, root):
        """wrapping map edges requires cloning the point into 6 additional positions which are beyond the map,
        (2 clones above (mirrored OY), 2 clones next to it, 2 clones below it (mirrored OY))
        because their circle buffer can contain points on the map
        For example, a point at X = 10 is cloned to X = MAP_WIDTH + 10,
        because the points near the right edge can be in range.
        """

        cloned_points = util.get_all_projected_points(root.position)
        return [models.RootLocation.position.ST_DWithin(point.wkt, max_estimated_distance) for point in cloned_points]

    def get_maximum_range_from_estimate(self, center_pos, direction, travel_credits, max_possible_radius):
        """
        Real maximum distance taken from the center (based on toughness/cost of passing a certain property area)
        that can be passed when going into a certain direction. To do it, all PropertyAreas of the specific kind
        intersecting with the line are taken from the database. Then it's calculated how much can be passed considering
        the "toughness" of the intersection with the highest priority on the interval.
        Example:
        A line from center (0, 0) to (0, 10); travel_credits = 5
            (we know it's not possible to pass more than 10 units with 5 travel credits)

        The lines taken from the intersecting areas are:
         1. (0, 0) to (0, 5) having traversability value = 1, priority = 1
         2. (0, 5) to (0, 10) having traversability value = 0.5, priority = 1
         3. (0, 1) to (0, 4) having traversability value = 2, priority = 2
         4. (0, 2) to (0, 3) having traversability value = 1, priority = 3

        So we start with credits_left = travel_credits = 5
        For (0,0) to (0,1) take 1 credit. (value = 1);
                it consumed 1 (len / value) credit so credits_left = 4
        For (0, 1) to (0, 2) we take 3. (value = 2) because it has a higher priority than 1.;
                it consumed 0.5 (len / value) so credits_left = 3.5
        For (0, 2) to (0, 3) we take 4. (value = 1) because it has a higher priority than 3.;
                it consumed 1 (len / value) so credits_left = 2.5
        For (0, 3) to (0, 4) we take 3. (value = 2), because it has the best priority on this range;
                it consumed 0.5 (len / value) so credits_left = 2
        For (0, 4) to (0, 5) we take 1. (value = 1) because it's the only interval on this range;
                it consumed 1 (len / value) so credits_left = 1
        For (0, 5) to (0, 6) we take 2. (value = 1) because it's the only interval on this range;
                it consumed 1 (len / value) so credits_left = 0
        credits_left = 0, so it's over. It means the real destination is (0, 6).
        :param max_possible_radius: estimated value (upper bound) which is never lower than potential function result.
        :param travel_credits: number of visibility/traversability points that can be consumed to "move forward"
        :param direction: angle (from beginning of coord system) in which the line starting in center should go
        :param center_pos: a point where the line should be started
        """
        x = center_pos.x + math.cos(math.radians(direction)) * max_possible_radius
        y = center_pos.y + math.sin(math.radians(direction)) * max_possible_radius

        radius_multi_line = self.create_multi_line_string_for_wrapped_edges(center_pos, Point(x, y))

        logger.debug("x: %s, y: %s, radius: %s", x, y, radius_multi_line)
        intersecting_areas = db.session.query(models.PropertyArea.area.ST_Intersection(radius_multi_line.wkt),
                                              models.PropertyArea) \
            .filter(models.PropertyArea.area.ST_Intersects(radius_multi_line.wkt)) \
            .filter(models.PropertyArea.kind == self.AREA_KIND) \
            .all()

        BEGIN = 1
        END = 2

        concrete_allowed_terrain_types = models.get_concrete_types_for_groups(self.allowed_terrain_types)
        changes = []
        for intersection_wkb, area in intersecting_areas:
            intersection = to_shape(intersection_wkb)
            if intersection.geom_type in ("Point", "MultiPoint"):
                continue  # points have no meaning
            logger.debug("intersection: %s %s", intersection, area)

            # the intersection must be of an acceptable terrain type
            if area.terrain_area.type not in concrete_allowed_terrain_types:
                continue

            line_strings = self.extract_line_strings(intersection)
            for line_string in line_strings:
                def distance_for_intersection(index):
                    return util.distance(center_pos, Point(line_string.coords[index]))

                begin_distance = min(distance_for_intersection(0), distance_for_intersection(1))
                end_distance = max(distance_for_intersection(0), distance_for_intersection(1))

                changes.append((begin_distance, area.priority, BEGIN, area.value))
                changes.append((end_distance, area.priority, END, area.value))

        DISTANCE, PRIORITY, TYPE, VALUE = 0, 1, 2, 3
        logger.debug("intervals are: %s", changes)

        # a bucket is a group of changes which happen in the same distance from the beginning
        buckets = []
        for bucket_distance, bucket in itertools.groupby(sorted(changes), lambda change: change[DISTANCE]):
            buckets.append({"distance": bucket_distance, "changes": list(bucket)})

        current_intervals = []
        # the first bucket is special, because it must create current_intervals
        if buckets and math.isclose(buckets[0]["distance"], 0.0, abs_tol=1e-9):
            self.update_intervals_based_on(buckets[0]["changes"], current_intervals)
            buckets.pop(0)

        credits_left = travel_credits
        passed_distance = 0
        for bucket in buckets:
            logger.debug("### change %s", bucket["distance"])
            current_intervals.sort()

            # if any interval is missing or no credits then stop processing
            if len(current_intervals) == 0 or credits_left == 0:
                return passed_distance

            value_of_interval_with_top_prio = current_intervals[-1][1]
            # if any interval is impassable then stop processing
            if value_of_interval_with_top_prio == 0:
                return passed_distance

            logger.debug("value with top prio: %s", value_of_interval_with_top_prio)
            interval_length = bucket["distance"] - passed_distance
            credits_cost_of_interval = interval_length / value_of_interval_with_top_prio
            logger.debug("interval length: %s; interval cost: %s", interval_length, credits_cost_of_interval)
            if credits_cost_of_interval < credits_left:
                passed_distance = bucket["distance"]
                logger.debug("decrease credits_left by %s", credits_cost_of_interval)
                credits_left -= credits_cost_of_interval
            else:
                passed_distance += credits_left * value_of_interval_with_top_prio
                credits_left = 0

            self.update_intervals_based_on(bucket["changes"], current_intervals)
        return passed_distance

    def update_intervals_based_on(self, changes, current_intervals):
        DISTANCE, PRIORITY, TYPE, VALUE = 0, 1, 2, 3
        BEGIN, END = 1, 2
        for change in changes:
            if change[TYPE] == BEGIN:
                current_intervals.append((change[PRIORITY], change[VALUE]))
            else:
                current_intervals.remove((change[PRIORITY], change[VALUE]))

    def extract_line_strings(self, intersection):
        if intersection.geom_type == "MultiLineString":  # happens by the edge of the map
            lines_to_process = intersection[:]
        else:
            lines_to_process = [intersection]
        return lines_to_process

    @staticmethod
    def create_multi_line_string_for_wrapped_edges(from_point, to_point):
        """
        Wrapping logic is complicated. See https://tree.taiga.io/project/greekpl-exeris/wiki/map
        :param from_point:
        :param to_point:
        :return:
        """
        closest_projection_of_to_point = util.get_closest_projection_of_second_point(from_point, to_point)

        line = LineString([from_point, closest_projection_of_to_point])

        line_parts = []
        map_rectangle = Polygon([(0, 0), (0, map_data.MAP_HEIGHT),
                                 (map_data.MAP_WIDTH, map_data.MAP_HEIGHT), (map_data.MAP_WIDTH, 0)])
        for translation_x in [-map_data.MAP_WIDTH, 0, map_data.MAP_WIDTH]:
            translated_square = shapely.affinity.translate(map_rectangle, xoff=translation_x)
            line_part = translated_square.intersection(line)

            if not line_part.is_empty and line_part.geom_type == "LineString":
                line_parts += [shapely.affinity.translate(line_part, xoff=-translation_x)]
        for translation_y in [- map_data.MAP_HEIGHT, map_data.MAP_HEIGHT]:
            for translation_x in [-0.5 * map_data.MAP_WIDTH, 0.5 * map_data.MAP_WIDTH]:
                translated_square = shapely.affinity.translate(map_rectangle, xoff=translation_x, yoff=translation_y)
                line_part = translated_square.intersection(line)
                if not line_part.is_empty and line_part.geom_type == "LineString":
                    # translate
                    line_part = shapely.affinity.translate(line_part, xoff=-translation_x, yoff=-translation_y)
                    x_es, y_es = line_part.xy
                    y_es = [map_data.MAP_HEIGHT - y for y in y_es]  # turn Y around
                    line_parts += [LineString([(x_es[0], y_es[0]), (x_es[1], y_es[1])])]

        return MultiLineString(line_parts)

    def is_passable(self, position):
        """
        :return: True if it's possible to find direction
            for which `AreaRangeSpec.get_maximum_range_from_estimate` is greater than zero
        """
        intersecting_areas = db.session.query(models.PropertyArea) \
            .filter(models.PropertyArea.area.ST_Intersects(position.wkt)) \
            .filter(models.PropertyArea.kind == self.AREA_KIND) \
            .all()

        allowed_concrete_terrain_types = models.get_concrete_types_for_groups(self.allowed_terrain_types)
        return any([area.terrain_area.type in allowed_concrete_terrain_types for area in intersecting_areas])


class VisibilityBasedRange(AreaRangeSpec):
    AREA_KIND = models.AREA_KIND_VISIBILITY
    MAX_RANGE_MULTIPLIER = 1.0

    def __init__(self, distance, only_through_unlimited=False, allowed_terrain_types=None):
        super().__init__(distance, only_through_unlimited, allowed_terrain_types)


class TraversabilityBasedRange(AreaRangeSpec):
    AREA_KIND = models.AREA_KIND_TRAVERSABILITY
    MAX_RANGE_MULTIPLIER = 2.0

    def __init__(self, distance, only_through_unlimited=False, allowed_terrain_types=None):
        super().__init__(distance, only_through_unlimited, allowed_terrain_types)


class ItemQueryHelper:
    @staticmethod
    def query_all_types_in(types, being_in):
        """
        Return pre-prepared query which will filter Item query to specified types and "being_in" property
        :param types: list of ItemType instances or ItemType.type_name identifiers
        :param being_in: where should these items be located
        :return: query with two filters applied
        """
        type_names = [entry if entry is str else entry.name for entry in types]
        return models.Item.query.filter(models.Item.type_name.in_(type_names)).filter(models.Item.is_in(being_in))

    @staticmethod
    def query_all_types_near(types, being_in):
        """
        Return pre-prepared query which will filter Item query to specified types, and are in `being_in`
        or are in the same entity as the one specified in `being_in`
        :param types: list of ItemType instances or ItemType.type_name identifiers
        :param being_in: list of places where items should be located (their 'being_in' attribute)
        :return: query with two filters applied
        """
        type_names = [entry if entry is str else entry.name for entry in types]

        places = []
        if isinstance(being_in, collections.Iterable):
            places += being_in
        else:
            places.append(being_in)

        entities = models.Entity.query.filter(models.Item.is_in(being_in)).all()
        places += entities
        return models.Item.query.filter(models.Item.type_name.in_(type_names)).filter(models.Item.is_in(places))


class EventCreator:
    @classmethod
    def get_event_type_by_name(cls, name):
        return models.EventType.query.filter_by(name=name).one()

    @classmethod
    def base(cls, tag_base, rng=None, params=None, doer=None, target=None):
        """
        An utility method for creating a set of events for the following groups of the characters:
        doer (a character performing the action), target (A CHARACTER being object of the action),
        observer (everyone else who is close enough based on the range specification.

        Adds 'doer' and 'target' to the event JSON parameters.

        :param tag_base: a base part of the event type names.
            The specific events are created by adding a correct suffix: "_doer", "_target" and "_observer"
        :param rng: a range specification used to get a group of characters next to the doer.
        :param params: custom params injected to
        :param doer: a character who is going to get tag_base + _doer event. It can be None.
        :param target: a character who is going to get tag_base + _target event. It can be None.
        :return:
        """

        tag_doer = tag_base + "_doer"
        tag_target = tag_base + "_target"
        tag_observer = tag_base + "_observer"
        EventCreator.create(rng, tag_doer, tag_target, tag_observer, params, doer, target)

    @classmethod
    def create(cls, rng=None, tag_doer=None, tag_target=None, tag_observer=None, params=None,
               doer=None, target=None, locations=None):
        """
        Preferable way is to explicitly specify tag shown for doer, target and observers.
        Everyone use the params dict, which is used as event JSON parameters for pyslate.
        It's also extended by 'doer' and 'target' if these are not None.

        To show an event for the observers tag_observer should be not None and either
        locations (locations with characters) or doer and rng (range specification for characters around doer)
        should be specified.
        """
        if not tag_doer and not tag_observer:
            raise ValueError("EventCreator doesn't have neither tag_doer nor tag_observer specified")

        if not params:
            params = {}

        def replace_dict_values(args):
            for param_key, param_value in list(args.items()):
                if isinstance(param_value, models.Entity):  # pyslatize all entities
                    pyslatized = param_value.pyslatize()
                    pyslatized.update(args)
                    del pyslatized[param_key]
                    args = pyslatized
                if isinstance(param_value, collections.Mapping):  # recursive for other dicts
                    args[param_key] = replace_dict_values(param_value)
            return args

        base_params = replace_dict_values(params)

        if tag_doer and cls.can_receive_action(doer):
            doer_params = copy.deepcopy(base_params)
            if target:
                doer_params.setdefault("groups", {})["target"] = target.pyslatize()

            event_for_doer = models.Event(tag_doer, doer_params)
            event_obs_doer = models.EventObserver(event_for_doer, doer)

            db.session.add_all([event_for_doer, event_obs_doer])
            main.call_hook(main.Hooks.NEW_EVENT, event_observer=event_obs_doer)

        if tag_target and cls.can_receive_action(target):
            target_params = copy.deepcopy(base_params)
            if doer:
                target_params.setdefault("groups", {})["doer"] = doer.pyslatize()

            event_for_target = models.Event(tag_target, target_params)
            event_obs_target = models.EventObserver(event_for_target, target)

            db.session.add_all([event_for_target, event_obs_target])
            main.call_hook(main.Hooks.NEW_EVENT, event_observer=event_obs_target)

        if (rng or locations) and tag_observer:
            obs_params = copy.deepcopy(base_params)
            if doer:
                obs_params.setdefault("groups", {})["doer"] = doer.pyslatize()
            if target:
                obs_params.setdefault("groups", {})["target"] = target.pyslatize()

            event_for_observer = models.Event(tag_observer, obs_params)
            db.session.add(event_for_observer)
            character_obs = cls.get_observers(rng, doer, target, locations)

            event_obs = [models.EventObserver(event_for_observer, char) for char in character_obs
                         if char not in (doer, target)]

            db.session.add_all(event_obs)

            for obs in event_obs:
                main.call_hook(main.Hooks.NEW_EVENT, event_observer=obs)

    @classmethod
    def can_receive_action(cls, entity):
        return entity and isinstance(entity, models.Character) and models.Character.is_alive

    @classmethod
    def get_observers(cls, rng, doer, target, locations):
        if rng:
            character_obs = set(rng.characters_near(doer))
            if target:
                character_obs.update(rng.characters_near(target))
        elif locations:
            character_obs = set()
            for loc in locations:
                character_obs.update(loc.characters_inside())
        else:
            raise ValueError("EventCreator requires either 'rng' or 'locations'")
        return character_obs


class Identifiers:
    MIN_LENGTH = 3

    @classmethod
    def generate_unique_identifier(cls):
        """
        Generates an (yet unused) unique identifier. It does so by generating 1000 candidates for a new id of length
        MIN_LENGTH and checking whether all of these are already used.
        If so, then it tries again with the length increased by 1.
        :return: the first id that is not used
        """
        length = cls.MIN_LENGTH
        generated_identifier = None
        while generated_identifier is None:
            generated_identifier = cls._try_to_generate_unique_identifier_for_length(length)
            length += 1
        return generated_identifier

    @classmethod
    def _try_to_generate_unique_identifier_for_length(cls, length):
        generated_identifiers = [cls._generate_identifier(length) for _ in range(1000)]  # 1000 candidates for id
        already_used_identifiers = db.session.query(models.UniqueIdentifier.value) \
            .filter(models.UniqueIdentifier.value.in_(generated_identifiers)).all()
        already_used_identifiers = {columns[0] for columns in already_used_identifiers}
        for generated_identifier in generated_identifiers:
            if generated_identifier not in already_used_identifiers:
                return generated_identifier

    @classmethod
    def _generate_identifier(cls, length):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(length))
