import collections
import copy
import logging
import math
import time
from collections import deque

from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon, LineString

from exeris.core import models, main
from exeris.core.main import db

logger = logging.getLogger(__name__)


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

    SEC_IN_DAY = SEC_IN_MIN * MIN_IN_HOUR * HOUR_IN_DAY
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


class RangeSpec:
    def characters_near(self, entity):
        locs = []
        for loc in self._locationize(entity):
            locs += self.locations_near(loc)
        return models.Character.query.filter(models.Character.is_in(locs)).all()

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
        for a in self._locationize(entity_a):
            locations_near_a = self.locations_near(a)
            return any([True for b in self._locationize(entity_b) if b in locations_near_a])

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
        return [entity.being_in]


class NeighbouringLocationsRange(RangeSpec):
    def __init__(self, only_through_unlimited):
        self.only_through_unlimited = only_through_unlimited

    def locations_near(self, entity):
        loc = self._locationize(entity)[0]
        return visit_subgraph(loc, self.only_through_unlimited)


def visit_subgraph(node, only_through_unlimited=False):
    passages_all = node.passages_to_neighbours
    passages_left = deque(passages_all)
    number_of_door_passed = {node: 0}
    visited_locations = {node}
    while len(passages_left):
        passage = passages_left.popleft()
        if passage.passage.is_accessible(only_through_unlimited=only_through_unlimited):
            if passage.other_side not in visited_locations:
                number_of_door_passed[passage.other_side] = number_of_door_passed[passage.own_side]
                if not passage.passage.type.unlimited:
                    number_of_door_passed[passage.other_side] += 1
                visited_locations.add(passage.other_side)
                new_passages = passage.other_side.passages_to_neighbours
                passages_left.extend([p for p in new_passages if p.other_side not in visited_locations])
    return {loc for loc in visited_locations if number_of_door_passed[loc] <= 2}


class AreaRangeSpec(RangeSpec):  # TODO! It still doesn't work for edges of the map
    def __init__(self, distance, only_through_unlimited=False):
        self.distance = distance
        self.only_through_unlimited = only_through_unlimited

    def locations_near(self, entity):
        locs = visit_subgraph(entity, self.only_through_unlimited)

        roots = [r for r in locs if isinstance(r, models.RootLocation)]
        if len(roots):
            root = roots[0]

            area = self.create_circular_area(root.position, self.distance)

            other_locs = models.RootLocation.query. \
                filter(models.RootLocation.position.ST_Intersects(area.wkt)). \
                filter(models.RootLocation.id != root.id).all()

            for other_loc in other_locs:
                locs.update(visit_subgraph(other_loc, self.only_through_unlimited))

        return locs

    def create_circular_area(self, center_pos, distance):
        """
        Real circular range from center (based on "toughness" of passing certain property area)
        calculated as 8-point polygon being approximation of a circle.
        First, 8 lines from center to candidate vertices are created. Then all PropertyAreas of the specific kind
        intersecting with the line are taken from the database. Then it's calculated how much can be passed considering
        the "toughness" of the highest priority on the interval.
        Example:
        Line from center (0, 0) to (0, 10); distance = 5 (because line length * global_max_traversability = 10)

        The lines taken from intersecting areas are:
         1. (0, 0) to (0, 5) having traversability value = 1, priority = 1
         2. (0, 5) to (0, 10) having traversability value = 0.5, priority = 1
         3. (0, 1) to (0, 4) having traversability value = 2, priority = 2
         4. (0, 2) to (0, 3) having traversability value = 1, priority = 3

        So we start with distance_left = distance = 5
        For (0,0) to (0,1) take 1. (value = 1);
                it consumed 1 (len / value) point so distance_left = 4
        For (0, 1) to (0, 2) we take 3. (value = 2) because it has higher priority than 1.;
                it consumed 0.5 (len / value) so distance_left = 3.5
        For (0, 2) to (0, 3) we take 4. (value = 1) because it has higher priority than 3.;
                it consumed 1 (len / value) so distance_left = 2.5
        For (0, 3) to (0, 4) we take 3. (value = 2), because it has the best priority on this range;
                it consumed 0.5 (len / value) so distance_left = 2
        For (0, 4) to (0, 5) we take 1. (value = 1) because it's the only interval on this range;
                it consumed 1 (len / value) so distance_left = 1
        For (0, 5) to (0, 6) we take 2. (value = 1) because it's the only interval on this range;
                it consumed 1 (len / value) so distance_left = 0
        distance_left = 0, so it's over. It means the real point is (0, 6)
        It's done for every of 8 points, so polygon is created.

        :param center_pos:
        :param distance:
        :return:
        """
        points = []
        for angle in range(0, 360, 45):
            max_estimated_radius = self.MAX_RANGE_MULTIPLIER * distance

            map_distance = self.get_real_range_from_estimate(center_pos, angle, distance, max_estimated_radius)

            threshold_x = center_pos.x + math.sin(math.radians(angle)) * map_distance
            threshold_y = center_pos.y + math.cos(math.radians(angle)) * map_distance

            points += [(threshold_x, threshold_y)]
        return Polygon(points)

    def get_real_range_from_estimate(self, center_pos, angle, distance, max_estimated_radius):
        x = center_pos.x + math.sin(math.radians(angle)) * max_estimated_radius
        y = center_pos.y + math.cos(math.radians(angle)) * max_estimated_radius
        radius_line = LineString([center_pos.coords[0], (x, y)])
        logger.debug("x: %s, y: %s, radius: %s", x, y, radius_line)
        intersecting_areas = db.session.query(models.PropertyArea.area.ST_Intersection(radius_line.wkt),
                                              models.PropertyArea) \
            .filter(models.PropertyArea.area.ST_Intersects(radius_line.wkt)) \
            .filter(models.PropertyArea.kind.in_(self.AREA_KINDS)) \
            .all()

        BEGIN = 1
        END = 2

        changes = []
        for intersection_wkb, area in intersecting_areas:
            intersection = to_shape(intersection_wkb)
            if intersection.geom_type == "Point":
                continue  # points have no meaning
            logger.debug("intersection: %s", intersection)

            def distance_for_intersection(index):
                return self.point_to_distance(center_pos.coords[0], intersection.coords[index])

            begin_distance = min(distance_for_intersection(0), distance_for_intersection(1))
            end_distance = max(distance_for_intersection(0), distance_for_intersection(1))

            changes.append((begin_distance, area.priority, BEGIN, area.value))
            changes.append((end_distance, area.priority, END, area.value))

        DISTANCE, PRIORITY, TYPE, VALUE = 0, 1, 2, 3

        current_intervals = []
        distance_left = distance
        real_length = 0
        last_checkpoint_distance = 0
        for change in sorted(changes):
            logger.debug("### change %s", change)
            current_intervals.sort()
            if distance_left and current_intervals:
                interval_length = change[DISTANCE] - last_checkpoint_distance
                logger.debug("interval length: %s", interval_length)
                value_with_top_prio = current_intervals[-1][1]
                logger.debug("value with top prio: %s", value_with_top_prio)
                interval_cost = interval_length / value_with_top_prio
                logger.debug("interval cost: %s", interval_cost)
                logger.debug("distance left: %s", distance_left)
                if distance_left >= interval_cost:
                    logger.debug("decrease distance_left by %s", interval_cost)
                    distance_left -= interval_cost
                    real_length = change[DISTANCE]
                else:
                    real_length = last_checkpoint_distance + distance_left * value_with_top_prio
                    distance_left = 0
                last_checkpoint_distance = change[DISTANCE]

            if change[TYPE] == BEGIN:
                current_intervals.append((change[PRIORITY], change[VALUE]))
            else:
                current_intervals.remove((change[PRIORITY], change[VALUE]))

        return real_length

    def point_to_distance(self, center_pos, point):
        return math.sqrt(abs(center_pos[0] - point[0]) ** 2 + abs(center_pos[1] - point[1]) ** 2)


class VisibilityBasedRange(AreaRangeSpec):
    def __init__(self, distance, only_through_unlimited=False):
        super().__init__(distance, only_through_unlimited)
        self.AREA_KINDS = [models.AREA_KIND_VISIBILITY]
        self.MAX_RANGE_MULTIPLIER = 1.0


class TraversabilityBasedRange(AreaRangeSpec):
    AREA_KINDS = [models.AREA_KIND_LAND_TRAVERSABILITY,
                  models.AREA_KIND_WATER_TRAVERSABILITY]
    MAX_RANGE_MULTIPLIER = 2.0

    def __init__(self, distance, only_through_unlimited=False):
        super().__init__(distance, only_through_unlimited)


class LandTraversabilityBasedRange(AreaRangeSpec):
    AREA_KINDS = [models.AREA_KIND_LAND_TRAVERSABILITY]
    MAX_RANGE_MULTIPLIER = 2.0

    def __init__(self, distance, only_through_unlimited=False):
        super().__init__(distance, only_through_unlimited)


class WaterTraversabilityBasedRange(AreaRangeSpec):
    AREA_KINDS = [models.AREA_KIND_WATER_TRAVERSABILITY]
    MAX_RANGE_MULTIPLIER = 1.0

    def __init__(self, distance, only_through_unlimited=False):
        super().__init__(distance, only_through_unlimited)


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
        Return pre-prepared query which will filter Item query to specified types and "being_in" property
        :param types: list of ItemType instances or ItemType.type_name identifiers
        :param being_in: list of places where items should be located in their being_in
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

        tag_doer = tag_base + "_doer"
        tag_target = tag_base + "_target"
        tag_observer = tag_base + "_observer"
        EventCreator.create(rng, tag_doer, tag_target, tag_observer, params, doer, target)

    @classmethod
    def create(cls, rng=None, tag_doer=None, tag_target=None, tag_observer=None, params=None, doer=None, target=None):
        """
        Either tag_base or tag_doer should be specified. If tag_base is specified then event
        for doer and observers (based on specified range) are emitted.

        Preferable way is to explicitly specify tag shown for doer, target and observers.
        Everyone use the same args dict, which is used as args parameters.
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

        if tag_doer and doer:
            doer_params = copy.deepcopy(base_params)
            if target:
                doer_params.setdefault("groups", {})["target"] = target.pyslatize()

            event_for_doer = models.Event(tag_doer, doer_params)
            event_obs_doer = models.EventObserver(event_for_doer, doer)

            db.session.add_all([event_for_doer, event_obs_doer])
            main.call_hook(main.Hooks.NEW_EVENT, event_observer=event_obs_doer)

        if target and tag_target:
            target_params = copy.deepcopy(base_params)
            if doer:
                target_params.setdefault("groups", {})["doer"] = doer.pyslatize()

            event_for_target = models.Event(tag_target, target_params)
            event_obs_target = models.EventObserver(event_for_target, target)

            db.session.add_all([event_for_target, event_obs_target])
            main.call_hook(main.Hooks.NEW_EVENT, event_observer=event_obs_target)

        if rng and tag_observer:
            obs_params = copy.deepcopy(base_params)
            if doer:
                obs_params.setdefault("groups", {})["doer"] = doer.pyslatize()
            if target:
                obs_params.setdefault("groups", {})["target"] = target.pyslatize()

            event_for_observer = models.Event(tag_observer, obs_params)
            db.session.add(event_for_observer)
            character_obs = set(rng.characters_near(doer))

            if target:
                character_obs.update(rng.characters_near(target))
            event_obs = [models.EventObserver(event_for_observer, char) for char in character_obs
                         if char not in (doer, target)]

            db.session.add_all(event_obs)

            for obs in event_obs:
                main.call_hook(main.Hooks.NEW_EVENT, event_observer=obs)
