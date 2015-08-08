from flask.ext.testing import TestCase
from shapely.geometry import Point
from exeris.core import main

from exeris.core.main import db
from exeris.core.models import Activity, ItemType, RootLocation, Item, ScheduledTask, TypeGroup
from exeris.core.actions import ActivitiesProgressProcess, ActivityProgressProcess
from exeris.core.scheduler import Scheduler
from tests import util


__author__ = 'alek'


class SchedulerTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_travel_process(self):
        pass

    # kind of integration test
    def test_activity_process(self):

        self._before_activity_process()

        process = ActivitiesProgressProcess()
        process.perform()

        result_type = ItemType.query.filter_by(name="result").one()
        result_item = Item.query.filter_by(type=result_type).one()

        self.assertEqual(self.worker, result_item.being_in)
        self.assertEqual("result", result_item.type.name)

    def test_scheduler(self):
        """
        Test the same like test_activity_process, but testing if ScheduledTask is found correctly
        """
        util.initialize_date()
        self._before_activity_process()

        task = ScheduledTask(["exeris.core.actions.ActivitiesProgressProcess", {}], 0)
        db.session.add(task)

        db.session.flush()

        scheduler = Scheduler()
        scheduler.run_iteration()

        result_type = ItemType.query.filter_by(name="result").one()
        result_item = Item.query.filter_by(type=result_type).one()

        self.assertEqual(self.worker, result_item.being_in)
        self.assertEqual("result", result_item.type.name)

    def _before_activity_process(self):
        """
        Prepares environment for unit tests. Requires a tool called "hammer". Takes 1 tick.
        Creates an activity which results in CreateItemAction which creates an item of type "result"
        """
        hammer_type = ItemType("hammer", 300)
        result_type = ItemType("result", 200)
        db.session.add_all([hammer_type, result_type])

        rl = RootLocation(Point(1, 1), False, 134)
        db.session.add(rl)
        hammer_worked_on = Item(hammer_type, rl, weight=100)
        db.session.add(hammer_worked_on)

        self.worker = util.create_character("John", rl, util.create_player("ABC"))

        hammer = Item(hammer_type, self.worker, weight=111)
        db.session.add(hammer)
        db.session.flush()

        activity = Activity(hammer_worked_on, "dummy_activity_name", {}, {"mandatory_tools": [hammer_type.name]}, 1, self.worker)
        db.session.add(activity)
        db.session.flush()
        result = ["exeris.core.actions.CreateItemAction",
                  {"item_type": result_type.name, "properties": {"Edible": True}, "used_materials": "all"}]
        activity.result_actions = [result]

        self.worker.activity = activity

    def test_check_mandatory_items(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(rl, "name", {}, {"mandatory_tools": ["group_hammers", "group_axes"]}, 1, worker)
        process = ActivityProgressProcess(activity)

        bone_hammer = ItemType("bone_hammer", 200)
        stone_axe = ItemType("stone_axe", 300)

        hammers_group = TypeGroup("group_hammers")
        hammers_group.add_to_group(bone_hammer)

        db.session.add_all([rl, worker, activity, bone_hammer, stone_axe, hammers_group])

        self.assertRaises(main.NoToolForActivityException,
                          lambda: process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"]))

        hammer_in_inv = Item(bone_hammer, worker)
        db.session.add(hammer_in_inv)
        self.assertRaises(main.NoToolForActivityException,
                          lambda: process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"]))

        axe_in_inv = Item(stone_axe, worker)
        db.session.add(axe_in_inv)

        # should return without raising an exception
        process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"])

    tearDown = util.tear_down_rollback
