from flask.ext.testing import TestCase
from shapely.geometry import Point
from exeris.core import deferred
from exeris.core.actions import CreateItemAction
from exeris.core.main import db
from exeris.core.models import Activity, ItemType, RootLocation, Item, Entity
from exeris.core.scheduler import ActivityProcess
from tests import util

__author__ = 'alek'


class SchedulerTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_travel_process(self):
        pass

    # kind of integration test
    def test_activity_process(self):
        process = ActivityProcess()

        hammer_type = ItemType("hammer")
        db.session.add(hammer_type)

        rt = RootLocation(Point(1, 1), False, 134)
        db.session.add(rt)
        hammer_worked_on = Item(hammer_type, rt, 100)
        db.session.add(hammer_worked_on)

        worker = util.create_character("John", rt, util.create_player("ABC"))

        hammer = Item(hammer_type, worker, 111)
        db.session.add(hammer)
        db.session.flush()

        activity = Activity(hammer_worked_on, {"tools": [hammer_type.id]}, 1, 1)
        db.session.add(activity)
        db.session.flush()
        result = deferred.dumps((CreateItemAction, (ItemType.by_id, hammer_type.id), (Activity.by_id, activity.id), {"Edible": False}))
        activity.result_actions = [result]

        worker.activity = activity

        process.run()

    tearDown = util.tear_down_rollback

