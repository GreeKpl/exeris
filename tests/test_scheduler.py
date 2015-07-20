from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core.main import db
from exeris.core.models import Activity, ItemType, RootLocation, Item, ScheduledTask
from exeris.core.scheduler import ActivityProcess, Scheduler
from tests import util


__author__ = 'alek'


class SchedulerTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_travel_process(self):
        pass

    # kind of integration test
    def test_activity_process(self):

        self._before_activity_process()
        process = ActivityProcess()

        process.run()

        result_type = ItemType.query.filter_by(name="result").one()

        result_item = Item.query.filter_by(type=result_type).one()
        rt = RootLocation.query.one()

        self.assertEqual(self.worker, result_item.being_in)
        self.assertEqual("result", result_item.type.name)

    def test_scheduler(self):
        util.initialize_date()
        self._before_activity_process()

        task = ScheduledTask(["exeris.core.ActivityProcess", {}], 0)
        db.session.add(task)

        db.session.flush()

        scheduler = Scheduler()
        scheduler.run_iteration()

    def _before_activity_process(self):
        hammer_type = ItemType("hammer", 300)
        result_type = ItemType("result", 200)
        db.session.add_all([hammer_type, result_type])

        rt = RootLocation(Point(1, 1), False, 134)
        db.session.add(rt)
        hammer_worked_on = Item(hammer_type, rt, weight=100)
        db.session.add(hammer_worked_on)

        self.worker = util.create_character("John", rt, util.create_player("ABC"))

        hammer = Item(hammer_type, self.worker, weight=111)
        db.session.add(hammer)
        db.session.flush()

        activity = Activity(hammer_worked_on, {"tools": [hammer_type.name]}, 1, self.worker)
        db.session.add(activity)
        db.session.flush()
        result = ["exeris.core.actions.CreateItemAction",
                  {"item_type": result_type.name, "properties": {"Edible": True}, "used_materials": "all"}]
        activity.result_actions = [result]

        self.worker.activity = activity

    tearDown = util.tear_down_rollback

