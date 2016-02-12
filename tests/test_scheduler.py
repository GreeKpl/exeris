from unittest.mock import patch
from flask.ext.testing import TestCase
from shapely.geometry import Point
from exeris.core import main

from exeris.core.main import db
from exeris.core.models import Activity, ItemType, RootLocation, Item, ScheduledTask, TypeGroup, EntityType, \
    EntityProperty, SkillType, Character
from exeris.core.actions import ActivitiesProgressProcess, SingleActivityProgressProcess, EatingProcess
from exeris.core.properties_base import P
from exeris.core.scheduler import Scheduler
from tests import util


class SchedulerTravelTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_travel_process(self):
        pass


class SchedulerActivityTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

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
        with patch("exeris.core.scheduler.Scheduler._start_transaction", new=lambda slf: None):
            with patch("exeris.core.scheduler.Scheduler._commit_transaction", new=lambda slf: None):
                with patch("exeris.core.scheduler.Scheduler._rollback_transaction", new=lambda slf: None):
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

        activity = Activity(hammer_worked_on, "dummy_activity_name", {}, {"mandatory_tools": [hammer_type.name]}, 1,
                            self.worker)
        db.session.add(activity)
        db.session.flush()
        result = ["exeris.core.actions.CreateItemAction",
                  {"item_type": result_type.name, "properties": {"Edible": True}, "used_materials": "all"}]
        activity.result_actions = [result]

        self.worker.activity = activity

    def test_check_mandatory_tools(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(rl, "name", {}, {"doesnt matter": True}, 1, worker)
        process = SingleActivityProgressProcess(activity)

        bone_hammer = ItemType("bone_hammer", 200)
        stone_axe = ItemType("stone_axe", 300)

        hammers_group = TypeGroup("group_hammers")
        hammers_group.add_to_group(bone_hammer, efficiency=2.0)

        db.session.add_all([rl, worker, activity, bone_hammer, stone_axe, hammers_group])

        self.assertRaises(main.NoToolForActivityException,
                          lambda: process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"]))

        # recreate the process
        process = SingleActivityProgressProcess(activity)

        hammer_in_inv = Item(bone_hammer, worker, quality=1.5)
        db.session.add(hammer_in_inv)
        self.assertRaises(main.NoToolForActivityException,
                          lambda: process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"]))

        # recreate the process
        process = SingleActivityProgressProcess(activity)

        axe_in_inv = Item(stone_axe, worker, quality=0.75)
        db.session.add(axe_in_inv)

        # should return without raising an exception
        process.check_mandatory_tools(worker, ["group_hammers", "stone_axe"])

        # check quality change for an activity. It'd add 0.75 for axe and 3 for bone hammer
        self.assertCountEqual([0.75, 3.0], process.tool_based_quality)

    def test_check_optional_tools(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(rl, "name", {}, {"doesnt matter": True}, 1, worker)
        process = SingleActivityProgressProcess(activity)

        bone_hammer = ItemType("bone_hammer", 200)
        stone_axe = ItemType("stone_axe", 300)

        hammers_group = TypeGroup("group_hammers")
        hammers_group.add_to_group(bone_hammer, efficiency=2.0)

        db.session.add_all([rl, worker, activity, bone_hammer, stone_axe, hammers_group])

        process.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0})

        self.assertEqual(0.0, process.progress_ratio)  # no tools = no bonus

        # nothing affecting quality
        self.assertCountEqual([], process.tool_based_quality)

        # recreate the process
        process = SingleActivityProgressProcess(activity)

        hammer_in_inv = Item(bone_hammer, worker, quality=1.5)
        db.session.add(hammer_in_inv)
        process.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0})

        # optional tools DO AFFECT progress ratio bonus
        self.assertAlmostEqual(0.6, process.progress_ratio,
                               places=3)  # hammer = 0.2 bonus, relative q = 3.0 => 1 + 0.2 * 3

        # check quality change for an activity. Optional tools DON'T AFFECT tool_based_quality
        self.assertCountEqual([], process.tool_based_quality)

        # recreate the process
        process = SingleActivityProgressProcess(activity)

        axe_in_inv = Item(stone_axe, worker, quality=0.75)
        db.session.add(axe_in_inv)

        # should return without raising an exception
        process.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0})

        # both tools, hammer => 0.2 * 2 * 1.5, axe = 1.0 * 0.75; so increase by 1.35
        self.assertEqual(1.35, process.progress_ratio)

    def test_check_mandatory_machines(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(worked_on, "name", {}, {"doesnt matter": True}, 1, worker)
        process = SingleActivityProgressProcess(activity)

        bucket_type = ItemType("bucket", 200, portable=False)
        wooden_spindle_type = ItemType("wooden_spindle", 300, portable=False)

        spindles_group = TypeGroup("group_spindles")
        spindles_group.add_to_group(wooden_spindle_type, efficiency=2.0)

        db.session.add_all(
            [rl, worked_on_type, worked_on, worker, activity, bucket_type, wooden_spindle_type, spindles_group])

        self.assertRaises(main.NoMachineForActivityException,
                          lambda: process.check_mandatory_machines(["group_spindles", "bucket"]))

        # recreate the process
        process = SingleActivityProgressProcess(activity)

        bucket = Item(bucket_type, worker, quality=2)
        db.session.add(bucket)
        self.assertRaises(main.NoMachineForActivityException,
                          lambda: process.check_mandatory_machines(["group_spindles", "bucket"]))

        # recreate the process
        process = SingleActivityProgressProcess(activity)

        spindle_on_ground = Item(wooden_spindle_type, rl, quality=0.75)
        db.session.add(spindle_on_ground)

        # should return without raising an exception
        process.check_mandatory_machines(["group_spindles", "bucket"])

        # check quality change for an activity. It'd add 0.75 for axe and 3 for bone hammer
        self.assertCountEqual([2, 1.5], process.machine_based_quality)

    def test_activitys_skills(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)
        worker = util.create_character("ABC", rl, util.create_player("DEF"))

        frying_skill = SkillType("frying", "cooking")
        baking_skill = SkillType("baking", "cooking")

        worker.properties.append(EntityProperty(P.SKILLS, data={"cooking": 0.1, "frying": 0.5, "baking": 0.1}))

        activity = Activity(worked_on, "name", {}, {"doesnt matter": True}, 1, worker)

        db.session.add_all([rl, worked_on_type, worked_on, frying_skill, baking_skill, activity])
        process = SingleActivityProgressProcess(activity)

        process.check_skills(worker, ("frying", 0.3))
        self.assertRaises(main.TooLowSkillException, lambda: process.check_skills(worker, ("frying", 0.4)))

        process.check_skills(worker, ("baking", 0.1))
        self.assertRaises(main.TooLowSkillException, lambda: process.check_skills(worker, ("baking", 1.01)))

    def test_activitys_target_proximity(self):
        rl = RootLocation(Point(1, 1), False, 123)
        far_away = RootLocation(Point(5, 5), False, 123)
        some_item_type = ItemType("some_item", 100)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)

        worker = util.create_character("John", rl, util.create_player("ABC"))

        target_item1 = Item(some_item_type, rl)
        target_item2 = Item(some_item_type, worker)

        db.session.add_all([rl, far_away, worked_on_type, some_item_type, worked_on, target_item1, target_item2])
        db.session.flush()

        activity = Activity(worked_on, "name", {}, {"doesnt matter": True}, 1, worker)
        process = SingleActivityProgressProcess(activity)

        process.check_target_proximity([target_item1.id, target_item2.id])

        # move target_item2 away
        target_item2.being_in = far_away
        self.assertRaises(main.ActivityTargetTooFarAwayException,
                          lambda: process.check_target_proximity([target_item1.id, target_item2.id]))

    def test_number_of_workers(self):
        rl = RootLocation(Point(1, 1), False, 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)

        plr = util.create_player("ABC")
        worker1 = util.create_character("1", rl, plr)
        worker2 = util.create_character("2", rl, plr)

        db.session.add_all([rl, worked_on_type, worked_on, worker1, worker2])

        activity = Activity(worked_on, "name", {}, {"doesnt matter": True}, 1, worker1)
        process = SingleActivityProgressProcess(activity)

        workers = [worker1, worker2]

        process.check_min_workers(workers, 1)
        process.check_min_workers(workers, 2)
        self.assertRaises(main.TooFewParticipantsException,
                          lambda: process.check_min_workers(workers, 3))

        process.check_max_workers(workers, 3)
        process.check_max_workers(workers, 2)
        self.assertRaises(main.TooManyParticipantsException,
                          lambda: process.check_max_workers(workers, 1))


class SchedulerEatingTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_eating_process_nothing_eaten(self):
        rl = RootLocation(Point(1, 1), False, 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))

        process = EatingProcess()
        process.perform()

        self.assertEqual(EatingProcess.HUNGER_INCREASE, char.hunger)

        process = EatingProcess()
        process.perform()

        self.assertEqual(2 * EatingProcess.HUNGER_INCREASE, char.hunger)

        value_after_two_ticks = Character.FOOD_BASED_ATTR_INITIAL_VALUE - 2 * EatingProcess.FOOD_BASED_ATTR_DECAY
        self.assertAlmostEqual(value_after_two_ticks, char.strength)
        self.assertAlmostEqual(value_after_two_ticks, char.durability)
        self.assertAlmostEqual(value_after_two_ticks, char.fitness)
        self.assertAlmostEqual(value_after_two_ticks, char.perception)

    def test_eating_applying_single_attr_food(self):
        rl = RootLocation(Point(1, 1), False, 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))

        char.eating_queue = dict(strength=0.3, hunger=0.2)

        char.hunger = 0.3

        process = EatingProcess()
        process.perform()

        hunger_after_tick = 0.3 + EatingProcess.HUNGER_INCREASE - EatingProcess.HUNGER_MAX_DECREASE
        self.assertAlmostEqual(hunger_after_tick, char.hunger)

        # increase of just a single parameter, so no diversity bonus applies
        value_after_tick = Character.FOOD_BASED_ATTR_INITIAL_VALUE - EatingProcess.FOOD_BASED_ATTR_DECAY \
                           + EatingProcess.FOOD_BASED_ATTR_MAX_POSSIBLE_INCREASE
        self.assertEqual(value_after_tick, char.strength)

    def test_bonus_multiplier_value(self):
        values = [0.01]
        self.assertAlmostEqual(1, EatingProcess.bonus_mult(values))

        values = [0.01, 0.01]
        self.assertAlmostEqual(1.3, EatingProcess.bonus_mult(values))

        values = [0.01, 0.01, 0.005]
        self.assertAlmostEqual(1.45, EatingProcess.bonus_mult(values))

        values = [0.01, 0.01, 0.005]
        self.assertAlmostEqual(1.45, EatingProcess.bonus_mult(values))

        values = [0.003, 0.01]
        self.assertAlmostEqual(1.09, EatingProcess.bonus_mult(values))

    def test_eating_applying_multi_attr_food(self):
        rl = RootLocation(Point(1, 1), False, 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))

        char.eating_queue = dict(strength=0.003, hunger=0.2, durability=0.01)

        process = EatingProcess()
        process.perform()

        # increase all parameters parameter, diversity bonus applies
        value_after_tick = Character.FOOD_BASED_ATTR_INITIAL_VALUE + 0.003 * 1.09 - EatingProcess.FOOD_BASED_ATTR_DECAY
        self.assertEqual(value_after_tick, char.strength)

        value_after_tick = Character.FOOD_BASED_ATTR_INITIAL_VALUE + 0.01 * 1.09 - EatingProcess.FOOD_BASED_ATTR_DECAY
        self.assertEqual(value_after_tick, char.durability)

    def test_death_of_starvation(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), False, 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))

        char.hunger = 0.99  # very hungry

        process = EatingProcess()
        process.perform()

        self.assertEqual(main.Types.DEAD_CHARACTER, char.type.name)
        # no more assertions needed, because DeathOfStarvationAction is tested separately