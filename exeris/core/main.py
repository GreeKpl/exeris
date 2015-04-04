from collections import deque
from enum import Enum

__author__ = 'aleksander chrabąszcz'

from flask import Flask
import time
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = None

from exeris.core import models
from exeris.core.models import Character, Item, RootLocation, Event, EventType, EventObserver

import logging


def create_app(database=db, config_object_module="config.DevelopmentConfig"):
    global app
    app = Flask(__name__)
    app.config.from_object(config_object_module)
    database.init_app(app)
    return app


class GameDate:
    """
    Class handling in-game date and in-game time intervals. It can be used to get current in-game time (NOW), and also
    perform basic addition and compare operations.
    1 minute = 60 seconds, 1 hour = 60 minutes, 1 Sol = 48 hours (24 day + 24 night), 1 moon = 14 Sols
    """

    SEC_IN_MIN = 60
    MIN_IN_HOUR = 60
    HOUR_IN_SOL = 48
    DAYLIGHT_HOURS = 24
    SOL_IN_MOON = 14

    SEC_IN_SOL = SEC_IN_MIN * MIN_IN_HOUR * HOUR_IN_SOL
    SEC_IN_MOON = SEC_IN_SOL * SOL_IN_MOON

    def __init__(self, game_timestamp):
        self.game_timestamp = game_timestamp
        self.second, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.SEC_IN_MIN)

        self.minute, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.MIN_IN_HOUR)

        self.hour, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.HOUR_IN_SOL)

        self.sol, game_timestamp = self.__get_modulo_and_divided(game_timestamp, GameDate.SOL_IN_MOON)

        self.after_twilight = self.hour >= GameDate.DAYLIGHT_HOURS

        self.moon = game_timestamp

        self.sol_progression = (self.game_timestamp % GameDate.SEC_IN_SOL) / GameDate.SEC_IN_SOL

        self.moon_progression = (self.game_timestamp % GameDate.SEC_IN_MOON) / GameDate.SEC_IN_MOON

        self.logger = logging.getLogger(__name__)

    def __get_modulo_and_divided(self, dividend, divisor):
        return dividend % divisor, dividend // divisor

    @staticmethod
    def now():
        last_date_point = models.GameDateCheckpoint.query.one()
        now_timestamp = GameDate._get_timestamp()

        real_timestamp_base = last_date_point.real_date
        game_timestamp_base = last_date_point.game_date

        real_time_difference = now_timestamp - real_timestamp_base
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

    def characters_near(self):
        locs = self.get_locations_near()
        return Character.query.filter(Character.is_in(locs)).all()

    def items_near(self):
        locs = self.get_locations_near()
        return Item.query.filter(Item.is_in(locs)).all()

    def locations_near(self):
        locs = self.get_locations_near()
        return locs

    def root_locations_near(self):
        locs = self.get_locations_near()
        return [loc for loc in locs if type(loc) is RootLocation]


class SameLocationRange(RangeSpec):
    def __init__(self, center):
        self.center = center

    def get_locations_near(self):
        return self.center


class NeighbouringLocationsRange(RangeSpec):

    def __init__(self, center):
        self.center = center

    def get_locations_near(self):

        passages = self.center.passages_to_neighbours
        accessible_sides = [psg.other_side for psg in passages if psg.passage.is_accessible()]

        accessible_sides += [self.center]

        return accessible_sides


def visit_subgraph(node):
    passages_all = node.passages_to_neighbours
    passages_left = deque(passages_all)
    visited_locations = {node}
    while len(passages_left):
        passage = passages_left.popleft()
        if passage.passage.is_accessible():
            if passage.other_side not in visited_locations:
                visited_locations.add(passage.other_side)
                new_passages = passage.other_side.passages_to_neighbours
                passages_left.extend([p for p in new_passages if p.other_side not in visited_locations])
    return visited_locations


class VisibilityBasedRange(RangeSpec):

    def __init__(self, center, distance):
        self.center = center
        self.distance = distance

    def get_locations_near(self):

        locs = visit_subgraph(self.center)

        roots = [r for r in locs if type(r) is RootLocation]
        if len(roots):
            root = roots[0]
            other_locs = RootLocation.query.\
                filter(RootLocation.position.ST_DWithin(root.position.to_wkt(), self.distance)).\
                filter(RootLocation.id != root.id).all()

            for other_loc in other_locs:
                locs.update(visit_subgraph(other_loc))

        return locs


class TraversabilityBasedRange(RangeSpec):

    def __init__(self, center, distance):
        self.center = center
        self.distance = distance

    def get_locations_near(self):

        locs = visit_subgraph(self.center)

        roots = [r for r in locs if type(r) is RootLocation]
        if len(roots):
            root = roots[0]
            other_locs = RootLocation.query.\
                filter(RootLocation.position.ST_DWithin(root.position.to_wkt(), self.distance)).\
                filter(RootLocation.id != root.id).all()

            for other_loc in other_locs:
                locs.update(visit_subgraph(other_loc))

        return locs


class EventCreator():

    def get_event_type_by_name(self, name):
        return EventType.query.filter_by(name=name).one()

    @classmethod
    def base(cls, tag_base, doer=None, target=None, rng=None, params=None):

        tag_doer = tag_base + "_doer"
        tag_target = tag_base + "_target"
        tag_observer = tag_base + "_observer"
        return EventCreator(rng, tag_doer, tag_target, tag_observer, params, doer, target)

    def __init__(self, rng=None, tag_doer=None, tag_target=None, tag_observer=None, params=None, doer=None, target=None):
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

        if tag_doer and doer:
            event_doer = Event(self.get_event_type_by_name(tag_doer), params)
            db.session.add(event_doer)
            db.session.add(EventObserver(event_doer, doer))
        if target and tag_target:
            event_target = Event(tag_target, params)
            db.session.add(event_target)
            db.session.add(EventObserver(event_target, doer))
        if rng and tag_observer:
            event_observer = Event(tag_observer, params)
            event_obs = [EventObserver(event_observer, char) for char in rng.characters_near()
                         if char not in (doer, target)]

            db.session.add_all(event_obs)


