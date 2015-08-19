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

    def test_check_mandatory_tools(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(rl, "name", {}, {"mandatory_tools": ["group_hammers", "group_axes"]}, 1, worker)
        process = ActivityProgressProcess(activity)

        bone_hammer = ItemType("bone_hammer", 200)
        stone_axe = ItemType("stone_axe", 300)

        hammers_group = TypeGroup("group_hammers")
        hammers_group.add_to_group(bone_hammer, efficiency=2.0)

        db.session.add_all([rl, worker, activity, bone_hammer, stone_axe, hammers_group])

        self.assertRaises(main.NoToolForActivityException,
                          lambda: process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"]))

        # recreate the process
        process = ActivityProgressProcess(activity)

        hammer_in_inv = Item(bone_hammer, worker, quality=1.5)
        db.session.add(hammer_in_inv)
        self.assertRaises(main.NoToolForActivityException,
                          lambda: process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"]))

        # recreate the process
        process = ActivityProgressProcess(activity)

        axe_in_inv = Item(stone_axe, worker, quality=0.75)
        db.session.add(axe_in_inv)

        # should return without raising an exception
        process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"])

        # check quality change for an activity. It'd add 0.75 for axe and 3 for bone hammer
        self.assertCountEqual([0.75, 3.0], process.tool_based_quality)

    def test_check_optional_tools(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(rl, "name", {}, {"optional_tools": {"group_hammers": 0.2, "group_axes": 1.0}}, 1, worker)
        process = ActivityProgressProcess(activity)

        bone_hammer = ItemType("bone_hammer", 200)
        stone_axe = ItemType("stone_axe", 300)

        hammers_group = TypeGroup("group_hammers")
        hammers_group.add_to_group(bone_hammer, efficiency=2.0)

        db.session.add_all([rl, worker, activity, bone_hammer, stone_axe, hammers_group])

        process.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0})

        self.assertEqual(1.0, process.progress_ratio)  # no tools = no bonus

        # nothing affecting quality
        self.assertCountEqual([], process.tool_based_quality)

        # recreate the process
        process = ActivityProgressProcess(activity)

        hammer_in_inv = Item(bone_hammer, worker, quality=1.5)
        db.session.add(hammer_in_inv)
        process.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0})

        # optional tools DO AFFECT progress ratio bonus
        self.assertEqual(1.6, process.progress_ratio)  # hammer = 0.2 bonus, relative q = 3.0 => 1 + 0.2 * 3

        # check quality change for an activity. Optional tools DON'T AFFECT tool_based_quality
        self.assertCountEqual([], process.tool_based_quality)

        # recreate the process
        process = ActivityProgressProcess(activity)

        axe_in_inv = Item(stone_axe, worker, quality=0.75)
        db.session.add(axe_in_inv)

        # should return without raising an exception
        process.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0})

        # both tools, hammer => 0.2 * 2 * 1.5, axe = 1.0 * 0.75; so increase by 1.35
        self.assertEqual(2.35, process.progress_ratio)

    def test_check_mandatory_machines(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(worked_on, "name", {}, {"mandatory_machines": ["group_spindles", "bucket"]}, 1, worker)
        process = ActivityProgressProcess(activity)

        bucket_type = ItemType("bucket", 200, portable=False)
        wooden_spindle_type = ItemType("wooden_spindle", 300, portable=False)

        spindles_group = TypeGroup("group_spindles")
        spindles_group.add_to_group(wooden_spindle_type, efficiency=2.0)

        db.session.add_all([rl, worked_on_type, worked_on, worker, activity, bucket_type, wooden_spindle_type, spindles_group])

        self.assertRaises(main.NoMachineForActivityException,
                          lambda: process.check_mandatory_machines(["group_spindles", "bucket"]))

        # recreate the process
        process = ActivityProgressProcess(activity)

        bucket = Item(bucket_type, worker, quality=2)
        db.session.add(bucket)
        self.assertRaises(main.NoMachineForActivityException,
                          lambda: process.check_mandatory_machines(["group_spindles", "bucket"]))

        # recreate the process
        process = ActivityProgressProcess(activity)

        spindle_on_ground = Item(wooden_spindle_type, rl, quality=0.75)
        db.session.add(spindle_on_ground)

        # should return without raising an exception
        process.check_mandatory_machines(["group_spindles", "bucket"])

        # check quality change for an activity. It'd add 0.75 for axe and 3 for bone hammer
        self.assertCountEqual([2, 1.5], process.machine_based_quality)

    def test_targets(self):
        rl = RootLocation(Point(1, 1), False, 123)
        some_item_type = ItemType("some_item", 100)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)

        worker = util.create_character("John", rl, util.create_player("ABC"))

        target_item1 = Item(some_item_type, rl)
        target_item2 = Item(some_item_type, worker)

        db.session.add_all([rl, worked_on_type, some_item_type, worked_on, target_item1, target_item2])
        db.session.flush()

        activity = Activity(worked_on, "name", {}, {"targets": [target_item1.id, target_item2.id]}, 1, worker)
        process = ActivityProgressProcess(activity)

        process.check_target_proximity([target_item1.id, target_item2.id])

    tearDown = util.tear_down_rollback
