import math
from unittest.mock import patch

import copy
import sqlalchemy as sql
from exeris.core import main, deferred, models
from exeris.core import properties
from exeris.core.actions import ActivityProgressProcess, EatingProcess, DecayProcess, \
    WorkProcess, EatAction, WorkOnActivityAction, TravelInDirectionAction, \
    CreateItemAction, ActivityProgress, StartControllingMovementAction, TravelToEntityAction, ControlMovementAction, \
    AnimalsProcess
from exeris.core.general import GameDate
from exeris.core.main import db, Types
from exeris.core.models import Activity, ItemType, RootLocation, Item, ScheduledTask, TypeGroup, EntityProperty, \
    SkillType, Character, EntityTypeProperty, Intent, PropertyArea, TerrainType, TerrainArea, Notification, \
    ResourceArea, \
    LocationType, Location, Passage
from exeris.core.properties_base import P
from exeris.extra.scheduler import Scheduler
from flask_testing import TestCase
from shapely.geometry import Point, Polygon
from tests import util

# noinspection PyUnresolvedReferences
from exeris.extra import hooks


class SchedulerTravelTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_character_travel_in_direction_in_travel_process(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 123)
        grass_type = TerrainType("grassland")
        land_terrain_type = TypeGroup.by_name(main.Types.LAND_TERRAIN)
        land_terrain_type.add_to_group(grass_type)
        traversability_area = Polygon([(0, 0), (0, 20), (20, 20), (20, 0)])
        grass_terrain = TerrainArea(traversability_area, grass_type)

        land_trav_area = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, traversability_area,
                                      terrain_area=grass_terrain)
        traveler = util.create_character("John", rl, util.create_player("ABC"))

        travel_action = TravelInDirectionAction(traveler, 45)
        travel_intent = Intent(traveler, main.Intents.WORK, 1, None, deferred.serialize(travel_action))

        db.session.add_all([rl, grass_type, grass_terrain, land_trav_area, travel_intent])

        travel_process = WorkProcess(None)
        travel_process.perform()

        distance_per_tick = 10 * WorkProcess.SCHEDULER_RUNNING_INTERVAL / GameDate.SEC_IN_DAY
        distance_on_diagonal = distance_per_tick / math.sqrt(2)

        self.assertAlmostEqual(1 + distance_on_diagonal, traveler.get_position().x, delta=0.01)
        self.assertAlmostEqual(1 + distance_on_diagonal, traveler.get_position().y, delta=0.01)

    def test_character_go_to_location_to_perform_action_process(self):
        util.initialize_date()

        rl = RootLocation(Point(2.8, 2.8), 123)
        grass_type = TerrainType("grassland")
        land_terrain_type = TypeGroup.by_name(main.Types.LAND_TERRAIN)
        land_terrain_type.add_to_group(grass_type)
        accessible_area = Polygon([(0, 0), (0, 20), (20, 20), (20, 0)])
        grass_terrain = TerrainArea(accessible_area, grass_type)

        potato_loc = RootLocation(Point(10, 10), 55)
        potato_type = ItemType("potato", 10, stackable=True)
        potato_type.properties.append(EntityTypeProperty(P.EDIBLE, {
            "states": {"satiation": 0.1, "strength": 0.01}
        }))
        potatoes = Item(potato_type, potato_loc, amount=10)

        land_trav_area = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, accessible_area,
                                      terrain_area=grass_terrain)
        visibility_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, accessible_area,
                                       terrain_area=grass_terrain)
        traveler = util.create_character("John", rl, util.create_player("ABC"))

        eat_action = EatAction(traveler, potatoes, 5)

        go_to_entity_and_eat_intent = StartControllingMovementAction(traveler).perform()
        with go_to_entity_and_eat_intent as go_to_entity_and_eat_action:
            go_to_entity_and_eat_action.travel_action = TravelToEntityAction(traveler, potatoes)
            go_to_entity_and_eat_action.target_action = eat_action

        db.session.add_all([rl, grass_type, grass_terrain, land_trav_area, visibility_area,
                            potato_loc, potato_type, potatoes])

        work_process = WorkProcess(None)
        for i in range(2):  # come closer
            go_to_entity_and_eat_action.perform()
            work_process.process_travel_movement()

        self.assertEqual(0, traveler.states["satiation"])
        self.assertAlmostEqual(2.89820927, traveler.get_root().position.x)
        self.assertAlmostEqual(2.89820927, traveler.get_root().position.y)

        go_to_entity_and_eat_action.perform()
        # after this travel action it should be close enough, but the movement is committed
        # during `WorkProcess.process_travel_movement` so potatoes will be eaten in the next tick
        work_process.process_travel_movement()

        go_to_entity_and_eat_action.perform()  # eat half of potatoes

        # food is eaten
        self.assertEqual(0.5, traveler.states["satiation"])

        # action if finished, so it's not necessary to move and do it again, so force to do it again
        go_to_entity_and_eat_action.travel_action = TravelToEntityAction(traveler, potatoes)
        go_to_entity_and_eat_action.target_action = eat_action
        go_to_entity_and_eat_action.perform()  # eat the rest of potatoes
        self.assertEqual(1, traveler.states["satiation"])

        self.assertTrue(sql.inspect(potatoes).deleted)

        # all potatoes are eaten, so they don't exist
        self.assertRaises(main.EntityTooFarAwayException, lambda: eat_action.perform())

    def test_integration_character_go_and_perform_action_in_travel_process(self):
        util.initialize_date()

        rl = RootLocation(Point(2.8, 2.8), 123)
        far_away_loc = RootLocation(Point(40, 40), 12)
        grass_type = TerrainType("grassland")
        land_terrain_type = TypeGroup.by_name(main.Types.LAND_TERRAIN)
        land_terrain_type.add_to_group(grass_type)
        accessible_area = Polygon([(0, 0), (0, 20), (20, 20), (20, 0)])
        grass_terrain = TerrainArea(accessible_area, grass_type)

        potato_loc = RootLocation(Point(10, 10), 55)
        potato_type = ItemType("potato", 10, stackable=True)
        potato_type.properties.append(EntityTypeProperty(P.EDIBLE, {
            "states": {"satiation": 0.1, "strength": 0.01}
        }))
        potatoes = Item(potato_type, potato_loc, amount=10)

        potatoes_away = Item(potato_type, far_away_loc, amount=11)

        land_trav_area = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, accessible_area,
                                      terrain_area=grass_terrain)
        visibility_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, accessible_area,
                                       terrain_area=grass_terrain)
        traveler = util.create_character("John", rl, util.create_player("ABC"))

        eat_action = EatAction(traveler, potatoes, 5)

        db.session.add_all([rl, far_away_loc, grass_type, grass_terrain, land_trav_area, visibility_area,
                            potato_loc, potato_type, potatoes, potatoes_away])

        # should result in creating Intent for this action
        deferred.perform_or_turn_into_intent(traveler, eat_action)

        go_and_perform_action_intent = Intent.query.one()

        go_and_perform_action = deferred.call(go_and_perform_action_intent.serialized_action)

        self.assertEqual(ControlMovementAction, go_and_perform_action.__class__)

        # make sure the action was correctly serialized
        self.assertEqual(eat_action.executor, go_and_perform_action.target_action.executor)
        self.assertEqual(eat_action.item, go_and_perform_action.target_action.item)
        self.assertEqual(eat_action.amount, go_and_perform_action.target_action.amount)

        travel_process = WorkProcess(None)

        # come closer, not eat the potatoes
        for _ in range(3):
            travel_process.perform()
        self.assertAlmostEqual(2.94731391, traveler.get_root().position.x)
        self.assertAlmostEqual(2.94731391, traveler.get_root().position.y)

        self.assertEqual(0, traveler.states["satiation"])
        self.assertEqual(10, potatoes.amount)

        travel_process.perform()  # now it's close enough

        self.assertEqual(0.5, traveler.states["satiation"])
        self.assertEqual(5, potatoes.amount)
        self.assertAlmostEqual(2.99641854, traveler.get_root().position.x)
        self.assertAlmostEqual(2.99641854, traveler.get_root().position.y)

        # intent's action is completed and thus removed
        control_movement_action = Intent.query.one().serialized_action
        self.assertIsNone(control_movement_action[1]["travel_action"])
        self.assertIsNone(control_movement_action[1]["target_action"])

        eat_too_far_away_action = EatAction(traveler, potatoes_away, 3)
        deferred.perform_or_turn_into_intent(traveler, eat_too_far_away_action)

        self.assertEqual("exeris.core.actions.ControlMovementAction", Intent.query.one().serialized_action[0])

        travel_process.perform()  # nothing will happen, because potatoes are not on line of sight
        # (but LoS can be hard to define!!!!)

        # intent executor is still located on the same position
        self.assertAlmostEqual(2.99641854, traveler.get_root().position.x)
        self.assertAlmostEqual(2.99641854, traveler.get_root().position.y)

        # the intent is still there, because action was stopped by subclass of TurningIntoIntentExceptionMixin
        # so the error preventing going there is potentially only temporary
        self.assertEqual(main.Intents.WORK, Intent.query.one().type)

    def test_travel_in_direction_action_near_edge_of_water(self):
        util.initialize_date()

        rl = RootLocation(Point(1.02, 1.972222222222221), 123)

        land_terrain = TypeGroup.by_name(Types.LAND_TERRAIN)
        grass_terrain = TerrainType("grassland")
        land_terrain.add_to_group(grass_terrain)
        water_terrain = TypeGroup.by_name(Types.WATER_TERRAIN)
        deep_water_terrain = TerrainType("deep_water")
        water_terrain.add_to_group(deep_water_terrain)

        poly_grass = Polygon([(0.1, 0.1), (0.1, 2), (1, 2), (3, 1)])
        grass = models.TerrainArea(poly_grass, grass_terrain)

        poly_water = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
        water = models.TerrainArea(poly_water, deep_water_terrain, priority=0)

        land_trav1 = models.PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, poly_grass, grass)

        traveler = util.create_character("John", rl, util.create_player("ABC"))

        travel_action = TravelInDirectionAction(traveler, 90)
        travel_intent = Intent(traveler, main.Intents.WORK, 1, None, deferred.serialize(travel_action))

        db.session.add_all([rl, grass, water, travel_intent, land_trav1, grass_terrain, deep_water_terrain])

        travel_process = WorkProcess(None)
        travel_process.perform()

        self.assertEqual(rl, traveler.being_in)
        self.assertAlmostEqual(1.02, traveler.get_position().x, places=15)
        self.assertAlmostEqual(1.99, traveler.get_position().y, places=15)

        # move by the edge of the land
        Intent.query.delete()
        travel_action = TravelInDirectionAction(traveler, 330)
        travel_intent = Intent(traveler, main.Intents.WORK, 1, None, deferred.serialize(travel_action))
        db.session.add(travel_intent)

        travel_process.perform()

        # make sure it has really moved
        self.assertAlmostEqual(1.0801406530405860, traveler.get_position().x, places=15)
        self.assertAlmostEqual(1.9552777777777777, traveler.get_position().y, places=15)

    def test_move_entities_which_are_being_moved(self):
        work_process = WorkProcess(None)

        rl = RootLocation(Point(5, 5), 10)
        cog_type = LocationType("cog", 1000)

        union1_cog1 = Location(rl, cog_type)
        union1_cog2 = Location(rl, cog_type)

        cog3 = Location(rl, cog_type)

        cog_type.properties.append(EntityTypeProperty(P.MOBILE, {"inertiality": 0.5, "speed": 40}))

        poly_grass = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        land_terrain = TypeGroup.by_name(Types.LAND_TERRAIN)
        grass_terrain = TerrainType("grassland")
        land_terrain.add_to_group(grass_terrain)
        grass = models.TerrainArea(poly_grass, grass_terrain)
        land_traversability = models.PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, poly_grass, grass)

        db.session.add_all([rl, cog_type, union1_cog1, union1_cog2, cog3,
                            grass_terrain, land_terrain, grass, land_traversability])

        union1_cog1_union_member_property = properties.OptionalMemberOfUnionProperty(union1_cog1)
        union1_cog1_union_member_property.union(union1_cog2)

        cog1_being_moved_property = properties.OptionalBeingMovedProperty(union1_cog1)
        cog1_being_moved_property.set_movement(10, math.radians(90))
        cog2_being_moved_property = properties.OptionalBeingMovedProperty(union1_cog2)
        cog2_being_moved_property.set_movement(10, math.radians(0))

        cog3_being_moved_property = properties.OptionalBeingMovedProperty(cog3)
        cog3_being_moved_property.set_movement(2, math.radians(300))
        work_process.process_travel_movement()

        resultant_movement_coord = 10 / 2 / 2
        self.assertAlmostEqual(5 + resultant_movement_coord, union1_cog1.get_position().x)
        self.assertAlmostEqual(5 + resultant_movement_coord, union1_cog1.get_position().y)

        # affected by inertia
        self.assertAlmostEqual(5 + 1 / 2, cog3.get_position().x)  # affected by inertia
        self.assertAlmostEqual(5 - math.sqrt(3) / 2, cog3.get_position().y)

        cog3_being_moved_property.set_inertia(2, math.radians(300))

        work_process.process_travel_movement()


class SchedulerActivityTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    # kind of integration test
    def test_activity_process(self):
        self._before_activity_process()

        process = WorkProcess(None)
        process.perform()

        result_type = ItemType.query.filter_by(name="result").one()
        result_item = Item.query.filter_by(type=result_type).one()

        self.assertEqual(self.worker, result_item.being_in)
        self.assertEqual("result", result_item.type.name)

    def test_activity_process_failure_notifications(self):
        util.initialize_date()
        self._before_activity_process()

        hammer_type = ItemType.by_name("hammer")

        worker = Character.query.one()
        hammer = Item.query.filter(Item.is_in(worker)).filter_by(type=hammer_type).one()
        hammer.being_in = hammer.being_in.being_in  # drop the hammer onto ground

        process = WorkProcess(None)
        process.perform()

        failure_notification = Notification.query.one()
        self.assertEqual(main.Errors.NO_TOOL_FOR_ACTIVITY, failure_notification.title_tag)
        self.assertEqual(worker, failure_notification.character)

    def test_scheduler(self):
        """
        Test the same like test_activity_process, but testing if ScheduledTask is found correctly
        """
        util.initialize_date()
        self._before_activity_process()

        task = ScheduledTask(["exeris.core.actions.WorkProcess", {}], 0)
        db.session.add(task)

        db.session.flush()

        scheduler = Scheduler()
        with patch("exeris.extra.scheduler.Scheduler._start_transaction", new=lambda slf: None):
            with patch("exeris.extra.scheduler.Scheduler._commit_transaction", new=lambda slf: None):
                with patch("exeris.extra.scheduler.Scheduler._rollback_transaction", new=lambda slf: None):
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

        rl = RootLocation(Point(1, 1), 134)
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
                  {"item_type": result_type.name, "properties": {"Edible": {}}, "used_materials": "all"}]
        activity.result_actions = [result]

        work_on_activity_intent = Intent(self.worker, main.Intents.WORK, 1, activity,
                                         deferred.serialize(WorkOnActivityAction(self.worker, activity)))
        db.session.add(work_on_activity_intent)

    def test_check_mandatory_tools(self):
        rl = RootLocation(Point(1, 1), 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        bone_hammer = ItemType("bone_hammer", 200)
        stone_axe = ItemType("stone_axe", 300)

        hammers_group = TypeGroup("group_hammers", stackable=False)
        hammers_group.add_to_group(bone_hammer, efficiency=2.0)

        db.session.add_all([rl, worker, bone_hammer, stone_axe, hammers_group])

        self.assertRaises(main.NoToolForActivityException,
                          lambda: ActivityProgress.check_mandatory_tools(worker, ["group_hammers", "stone_axe"], {}))

        hammer_in_inv = Item(bone_hammer, worker, quality=1.5)
        db.session.add(hammer_in_inv)
        self.assertRaises(main.NoToolForActivityException,
                          lambda: ActivityProgress.check_mandatory_tools(worker, ["group_hammers", "stone_axe"], {}))

        axe_in_inv = Item(stone_axe, worker, quality=0.75)
        db.session.add(axe_in_inv)

        worker_impact = {}
        # should return without raising an exception
        ActivityProgress.check_mandatory_tools(worker, ["group_hammers", "stone_axe"], worker_impact)

        # check quality change for an activity. It'd add 0.75 for axe and 3 for bone hammer
        self.assertCountEqual([0.75, 3.0], worker_impact["tool_based_quality"])

    def test_check_optional_tools(self):
        rl = RootLocation(Point(1, 1), 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        bone_hammer = ItemType("bone_hammer", 200)
        stone_axe = ItemType("stone_axe", 300)

        hammers_group = TypeGroup("group_hammers", stackable=False)
        hammers_group.add_to_group(bone_hammer, efficiency=2.0)

        db.session.add_all([rl, worker, bone_hammer, stone_axe, hammers_group])

        worker_impact = {}
        ActivityProgress.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0}, worker_impact)

        self.assertEqual(0.0, worker_impact.get("progress_ratio", 0))  # no tools = no bonus

        # nothing affecting quality
        self.assertEqual([], worker_impact.get("tool_based_quality", []))

        hammer_in_inv = Item(bone_hammer, worker, quality=1.5)
        db.session.add(hammer_in_inv)
        worker_impact = {}
        ActivityProgress.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0}, worker_impact)

        # optional tools DO AFFECT progress ratio bonus
        self.assertAlmostEqual(0.6, worker_impact["progress_ratio"],
                               places=3)  # hammer = 0.2 bonus, relative q = 3.0 => 1 + 0.2 * 3

        # check quality change for an activity. Optional tools DON'T AFFECT tool_based_quality
        self.assertEqual([], worker_impact.get("tool_based_quality", []))

        axe_in_inv = Item(stone_axe, worker, quality=0.75)
        db.session.add(axe_in_inv)

        # should return without raising an exception
        worker_impact = {}
        ActivityProgress.check_optional_tools(worker, {"group_hammers": 0.2, "stone_axe": 1.0}, worker_impact)

        # both tools, hammer => 0.2 * 2 * 1.5, axe = 1.0 * 0.75; so increase by 1.35
        self.assertEqual(1.35, worker_impact["progress_ratio"])

    def test_check_mandatory_machines(self):
        rl = RootLocation(Point(1, 1), 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        activity = Activity(worked_on, "name", {}, {"doesnt matter": True}, 1, worker)

        bucket_type = ItemType("bucket", 200, portable=False)
        wooden_spindle_type = ItemType("wooden_spindle", 300, portable=False)

        spindles_group = TypeGroup("group_spindles", stackable=False)
        spindles_group.add_to_group(wooden_spindle_type, efficiency=2.0)

        db.session.add_all([rl, worked_on_type, worked_on, worker, activity, bucket_type,
                            wooden_spindle_type, spindles_group])

        self.assertRaises(main.NoMachineForActivityException,
                          lambda: ActivityProgress.check_mandatory_machines(["group_spindles", "bucket"], worked_on,
                                                                            {}))

        bucket = Item(bucket_type, rl, quality=2)
        db.session.add(bucket)
        self.assertRaises(main.NoMachineForActivityException,
                          lambda: ActivityProgress.check_mandatory_machines(["group_spindles", "bucket"], worked_on,
                                                                            {}))

        spindle_on_ground = Item(wooden_spindle_type, rl, quality=0.75)
        db.session.add(spindle_on_ground)

        # should return without raising an exception
        activity_params = {}
        ActivityProgress.check_mandatory_machines(["group_spindles", "bucket"], worked_on, activity_params)

        # check quality change for an activity. It'd add 0.75 for axe and 3 for bone hammer
        self.assertCountEqual([2, 1.5], activity_params["machine_based_quality"])

        # it should be possible to have an activity in the passage
        building_type = LocationType("building", 500)
        building = Location(rl, building_type)
        db.session.add_all([building_type, building])

        passage_with_activity = Passage.query.filter(Passage.between(rl, building)).one()

        ActivityProgress.check_mandatory_machines(["group_spindles", "bucket"], passage_with_activity, activity_params)

        # entity storing activity should be a priority to fulfill the machine, ignoring all the others
        poor_spindle = Item(wooden_spindle_type, rl, quality=0.1)
        db.session.add(poor_spindle)
        db.session.flush()
        activity_params = {}
        ActivityProgress.check_mandatory_machines(["group_spindles"], poor_spindle, activity_params)
        self.assertCountEqual([0.2], activity_params["machine_based_quality"])

    def test_check_existence_of_resource(self):
        rl = RootLocation(Point(1, 1), 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        oak_type = ItemType("oak", 200, stackable=True)
        coal_type = ItemType("coal", 300, stackable=True)

        db.session.add_all([rl, worker, oak_type, coal_type])

        self.assertRaises(main.NoResourceAvailableException,
                          lambda: ActivityProgress.check_required_resources(["oak", "coal"], rl))

        oak_resource_area = ResourceArea(oak_type, Point(5, 5), 10, efficiency=100, max_amount=50)
        db.session.add(oak_resource_area)

        self.assertRaises(main.NoResourceAvailableException,
                          lambda: ActivityProgress.check_required_resources(["oak", "coal"], rl))

        coal_resource_area = ResourceArea(coal_type, Point(5, 5), 2, efficiency=100, max_amount=50)
        db.session.add(coal_resource_area)

        self.assertRaises(main.NoResourceAvailableException,
                          lambda: ActivityProgress.check_required_resources(["oak", "coal"], rl))

        coal_resource_area.radius = 10

        ActivityProgress.check_required_resources(["oak", "coal"], rl)

    def test_check_allowed_location_types(self):
        rl = RootLocation(Point(1, 1), 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        hut_type = LocationType("hut", 4000)
        building_type = LocationType("building", 4000)
        hut = Location(rl, hut_type, title="domek")
        anvil_type = ItemType("anvil", 300, portable=False)

        anvil = Item(anvil_type, hut)

        db.session.add_all([rl, hut_type, building_type, hut, anvil_type, anvil])

        self.assertRaises(main.InvalidLocationTypeException,
                          lambda: ActivityProgress.check_location_types(["building"], rl))

        ActivityProgress.check_location_types(["hut"], anvil.get_location())

        ActivityProgress.check_location_types(["hut", "building"], anvil.get_location())

    def test_check_required_terrain_type(self):
        rl = RootLocation(Point(1, 1), 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        swamp_type = TerrainType("swamp")
        grass_type = TerrainType("grassland")
        road_type = TerrainType("road")
        terrain_poly = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
        swamp_area = TerrainArea(terrain_poly, swamp_type, priority=1)
        road_area = TerrainArea(terrain_poly, road_type, priority=3)

        db.session.add_all([rl, swamp_type, road_type, grass_type, swamp_area, road_area])

        self.assertRaises(main.InvalidTerrainTypeException,
                          lambda: ActivityProgress.check_terrain_types(["grassland"], rl))

        ActivityProgress.check_terrain_types(["road", "grassland"], rl)

    def test_check_excluded_by_entities(self):
        rl = RootLocation(Point(1, 1), 123)
        worker = util.create_character("John", rl, util.create_player("ABC"))

        field_type = ItemType("field", 300, portable=False)

        db.session.add_all([rl, field_type])

        ActivityProgress.check_excluded_by_entities({"field": 2}, rl)

        # create first field
        field1 = Item(field_type, rl)
        db.session.add(field1)

        # activity resulting in creation of a field
        other_activity = Activity(rl, "name", {}, {"doesnt matter": True}, 1, worker)
        create_field_action = CreateItemAction(item_type=field_type, properties={}, used_materials={},
                                               activity=other_activity, initiator=worker)
        other_activity.result_actions = [deferred.serialize(create_field_action)]
        db.session.add(other_activity)
        # results of ongoing activities don't have any impact on excluded_entities
        ActivityProgress.check_excluded_by_entities({"field": 2}, rl)

        # create second field
        field2 = Item(field_type, rl)
        db.session.add(field2)

        self.assertRaises(main.TooManyExistingEntitiesException,
                          lambda: ActivityProgress.check_excluded_by_entities({"field": 2}, rl))

    def test_check_permanence_of_location(self):
        rl = RootLocation(Point(1, 1), 123)
        rl_near = RootLocation(Point(2, 2), 123)
        rl_far = RootLocation(Point(51, 51), 123)

        immobile_type = ItemType("immobile", 300, portable=False)
        portable_type = ItemType("portable", 300, portable=True)

        db.session.add_all([rl, rl_near, rl_far, immobile_type, portable_type])

        # nothing there, so it can be permanent
        ActivityProgress.check_permanence_of_location(rl)

        immobile_item = Item(immobile_type, rl)
        db.session.add(immobile_item)
        ActivityProgress.check_permanence_of_location(rl)

        portable_item_near = Item(portable_type, rl_near)
        db.session.add(portable_item_near)
        ActivityProgress.check_permanence_of_location(rl)

        immobile_item_far = Item(immobile_type, rl_far)
        db.session.add(immobile_item_far)
        ActivityProgress.check_permanence_of_location(rl)

        immobile_item_near = Item(immobile_type, rl_near)
        db.session.add(immobile_item_near)
        self.assertRaises(main.TooCloseToPermanentLocation,
                          lambda: ActivityProgress.check_permanence_of_location(rl))

    def test_check_optional_machines(self):
        rl = RootLocation(Point(1, 1), 123)

        bronze_anvil_type = ItemType("bronze_anvil", 300, portable=False)
        steel_anvil_type = ItemType("steel_anvil", 300, portable=False)
        bronze_anvil = Item(bronze_anvil_type, rl)

        anvil_group = TypeGroup("anvil")
        anvil_group.add_to_group(bronze_anvil_type, efficiency=1.5)
        anvil_group.add_to_group(steel_anvil_type, efficiency=2)

        db.session.add_all([rl, bronze_anvil_type, steel_anvil_type,
                            anvil_group, bronze_anvil])

        activity_params = {}
        ActivityProgress.check_optional_machines({"bronze_anvil": 0.5}, rl, activity_params)
        self.assertEqual(activity_params["progress_ratio"], 0.5)

        steel_anvil = Item(steel_anvil_type, rl)
        db.session.add(steel_anvil)

        activity_params = {}
        ActivityProgress.check_optional_machines({"anvil": 0.5}, rl, activity_params)
        self.assertEqual(activity_params["progress_ratio"], 1.0)

    def test_check_activitys_skills(self):
        rl = RootLocation(Point(1, 1), 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)
        worker = util.create_character("ABC", rl, util.create_player("DEF"))

        frying_skill = SkillType("frying", "cooking")
        baking_skill = SkillType("baking", "cooking")

        worker.properties.append(EntityProperty(P.SKILLS, data={"cooking": 0.1, "frying": 0.5, "baking": 0.1}))

        db.session.add_all([rl, worked_on_type, worked_on, frying_skill, baking_skill])

        ActivityProgress.check_skills(worker, {"frying": 0.3}, {})
        self.assertRaises(main.TooLowSkillException, lambda: ActivityProgress.check_skills(worker, {"frying": 0.4}, {}))

        ActivityProgress.check_skills(worker, {"baking": 0.1}, {})
        self.assertRaises(main.TooLowSkillException,
                          lambda: ActivityProgress.check_skills(worker, {"baking": 1.01}, {}))

    def test_activitys_target_proximity(self):
        rl = RootLocation(Point(1, 1), 123)
        far_away = RootLocation(Point(5, 5), 123)
        some_item_type = ItemType("some_item", 100)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)

        worker = util.create_character("John", rl, util.create_player("ABC"))

        target_item1 = Item(some_item_type, rl)
        target_item2 = Item(some_item_type, worker)

        activity = Activity(worked_on, "name", {}, {"doesnt matter": True}, 1, worker)
        db.session.add_all(
            [rl, far_away, worked_on_type, some_item_type, worked_on, target_item1, target_item2, activity])
        db.session.flush()

        ActivityProgress.check_target_proximity([target_item1.id, target_item2.id], rl)

        # move target_item2 away
        target_item2.being_in = far_away
        self.assertRaises(main.ActivityTargetTooFarAwayException,
                          lambda: ActivityProgress.check_target_proximity([target_item1.id, target_item2.id], rl))

    def test_number_of_workers(self):
        rl = RootLocation(Point(1, 1), 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)

        plr = util.create_player("ABC")
        worker1 = util.create_character("1", rl, plr)
        worker2 = util.create_character("2", rl, plr)

        db.session.add_all([rl, worked_on_type, worked_on, worker1, worker2])

        workers = [worker1, worker2]

        ActivityProgress.check_min_workers(workers, 1)
        ActivityProgress.check_min_workers(workers, 2)
        self.assertRaises(main.TooFewParticipantsException,
                          lambda: ActivityProgress.check_min_workers(workers, 3))

        ActivityProgress.check_max_workers(workers, 3)
        ActivityProgress.check_max_workers(workers, 2)
        self.assertRaises(main.TooManyParticipantsException,
                          lambda: ActivityProgress.check_max_workers(workers, 1))

    def test_input_nonstackable_affecting_result_quality(self):
        rl = RootLocation(Point(1, 1), 123)
        worked_on_type = ItemType("worked_on", 100)
        worked_on = Item(worked_on_type, rl)
        hammer_type = ItemType("hammer", 23)
        axe_type = ItemType("axe", 23)

        plr = util.create_player("ABC")
        worker1 = util.create_character("1", rl, plr)

        activity = Activity(worked_on, "name", {}, {"input": {
            "hammer": {"left": 0, "needed": 1, "quality": 1.5},
            "axe": {"left": 0, "needed": 1, "quality": 4.0},
        }}, 1, worker1)
        hammer = Item(hammer_type, activity, role_being_in=False)
        axe = Item(axe_type, activity, role_being_in=False)

        db.session.add_all([rl, worked_on_type, worked_on, hammer_type, axe_type, hammer, axe, activity])

        process = ActivityProgressProcess(activity, [])
        process.perform()

        self.assertEqual(5.5, activity.quality_sum)
        self.assertEqual(2, activity.quality_ticks)


class SchedulerEatingTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_eating_process_nothing_eaten(self):
        rl = RootLocation(Point(1, 1), 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))

        process = EatingProcess(None)
        process.perform()

        self.assertEqual(EatingProcess.HUNGER_INCREASE, char.states["hunger"])

        process = EatingProcess(None)
        process.perform()

        self.assertEqual(2 * EatingProcess.HUNGER_INCREASE, char.states["hunger"])

        value_after_two_ticks = Character.FOOD_BASED_ATTR_INITIAL_VALUE - 2 * EatingProcess.FOOD_BASED_ATTR_DECAY
        self.assertAlmostEqual(value_after_two_ticks, char.states["strength"])
        self.assertAlmostEqual(value_after_two_ticks, char.states["durability"])
        self.assertAlmostEqual(value_after_two_ticks, char.states["fitness"])
        self.assertAlmostEqual(value_after_two_ticks, char.states["perception"])

    def test_eating_applying_single_attr_food(self):
        rl = RootLocation(Point(1, 1), 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))

        char.eating_queue = dict(strength=0.3, hunger=0.2)

        char.states["hunger"] = 0.3

        process = EatingProcess(None)
        process.perform()

        hunger_after_tick = 0.3 + EatingProcess.HUNGER_INCREASE - EatingProcess.HUNGER_MAX_DECREASE
        self.assertAlmostEqual(hunger_after_tick, char.states["hunger"])

        # increase of just a single parameter, so no diversity bonus applies
        value_after_tick = Character.FOOD_BASED_ATTR_INITIAL_VALUE - EatingProcess.FOOD_BASED_ATTR_DECAY \
                           + EatingProcess.FOOD_BASED_ATTR_MAX_POSSIBLE_INCREASE
        self.assertEqual(value_after_tick, char.states["strength"])

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
        rl = RootLocation(Point(1, 1), 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))

        char.eating_queue = dict(strength=0.003, hunger=0.2, durability=0.01)

        process = EatingProcess(None)
        process.perform()

        # increase all parameters parameter, diversity bonus applies
        value_after_tick = Character.FOOD_BASED_ATTR_INITIAL_VALUE + 0.003 * 1.09 - EatingProcess.FOOD_BASED_ATTR_DECAY
        self.assertEqual(value_after_tick, char.states["strength"])

        value_after_tick = Character.FOOD_BASED_ATTR_INITIAL_VALUE + 0.01 * 1.09 - EatingProcess.FOOD_BASED_ATTR_DECAY
        self.assertEqual(value_after_tick, char.states["durability"])

    def test_death_of_starvation(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        db.session.add(rl)
        char = util.create_character("testing", rl, util.create_player("DEF"))
        char.states["hunger"] = 0.99  # very hungry

        process = EatingProcess(None)
        process.perform()

        # start getting damage, but be alive
        self.assertLess(0, char.damage)
        self.assertEqual({main.Modifiers.STARVATION: (GameDate.now() + GameDate.from_date(1, 0)).game_timestamp},
                         char.modifiers)
        self.assertEqual(main.Types.ALIVE_CHARACTER, char.type.name)

        # character die of starvation
        char.damage = 0.99
        process = EatingProcess(None)
        process.perform()

        self.assertEqual(main.Types.DEAD_CHARACTER, char.type.name)

    def test_calculation_of_activity_progress(self):
        self.assertAlmostEqual(12.24744, ActivityProgress.calculate_resultant_progress(10, 1.5), places=3)
        self.assertAlmostEqual(10, ActivityProgress.calculate_resultant_progress(10, 0.5))  # if q < 1 then q = 1
        self.assertAlmostEqual(1.5, ActivityProgress.calculate_resultant_progress(1, 2.25))


class SchedulerAnimalsProcessTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_animal_process_on_hen(self):
        self._set_up_hen_entity_and_type()

        hen_type = ItemType.by_name("hen")
        egg_type = ItemType.by_name("egg")
        rl = RootLocation.query.one()

        hen = Item(hen_type, rl)
        hen.states[main.States.HUNGER] = 0
        hen_animal_prop = EntityProperty(P.ANIMAL, {
            "resources": {
                egg_type.name: 2,
            }
        })
        hen.properties.append(hen_animal_prop)
        hen.properties.append(EntityProperty(P.DOMESTICATED, {
            "resources_increase": {
                "eggs_increase": 3,
            }
        }))
        db.session.add(hen)

        animals_process = AnimalsProcess(None)
        animals_process.perform()

        # should become more hungry
        self.assertAlmostEqual(0.1, hen.states[main.States.HUNGER])

        # increase amount of eggs by 3 and then drop them onto ground and reduce amount of eggs to 0
        self.assertAlmostEqual(0.0, hen_animal_prop.data["resources"][egg_type.name])

        dropped_eggs = Item.query.filter_by(type=egg_type).one()
        self.assertEqual(5, dropped_eggs.amount)

    def _set_up_hen_entity_and_type(self):
        rl = RootLocation(Point(1, 1), 100)
        egg_type = ItemType("egg", 10, stackable=True)
        hen_type = ItemType("hen", 100)

        hen_type.properties.append(EntityTypeProperty(P.ANIMAL, {
            "type_resources": {
                egg_type.name: {
                    "initial": 0,
                    "max": 5,
                }
            },
            "can_lay_eggs": True,
            "laid_types": [egg_type.name],
        }))
        hen_type.properties.append(EntityTypeProperty(P.DOMESTICATED, {
            "type_resources_increase": {
                "eggs_increase": {
                    "initial": 0,
                    "affected_resources": {
                        egg_type.name: 1,
                    },
                },
            }
        }))

        db.session.add_all([rl, egg_type, hen_type])


class SchedulerDecayTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_simple_item_decay(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        carrot_type = ItemType("carrot", 5, stackable=True)
        axe_type = ItemType("axe", 5)
        axe = Item(axe_type, rl)
        hammer_type = ItemType("hammer_to_ignore", 30)  # it won't have DEGRADABLE property
        hammer = Item(hammer_type, rl)
        fresh_pile_of_carrots = Item(carrot_type, rl, amount=1000)  # only damage will be increased

        carrot_type.properties.append(
            EntityTypeProperty(P.DEGRADABLE, {"lifetime": 30 * 24 * 3600}))

        axe_type.properties.append(
            EntityTypeProperty(P.DEGRADABLE, {"lifetime": 100 * 24 * 3600}))

        db.session.add_all([rl, carrot_type, fresh_pile_of_carrots, axe_type, axe, hammer_type, hammer])

        process = DecayProcess(None)
        process.perform()

        self.assertAlmostEqual(1 / 30, fresh_pile_of_carrots.damage)
        self.assertEqual(1000, fresh_pile_of_carrots.amount)

        self.assertAlmostEqual(1 / 100, axe.damage)

        self.assertEqual(0.0, hammer.damage)  # make sure items without DEGRADABLE property are not affected

        old_pile_of_carrots = Item(carrot_type, rl, amount=1000)
        old_pile_of_carrots.damage = 0.99  #

        axe.damage = 0.999  # it'll crumble

        db.session.add(old_pile_of_carrots)

        process = DecayProcess(None)
        process.perform()

        self.assertEqual(1, old_pile_of_carrots.damage)
        self.assertEqual(990, old_pile_of_carrots.amount)
        self.assertEqual(None, axe.being_in)
        self.assertTrue(sql.inspect(axe).deleted)

    def test_activity_decay(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        initiator = util.create_character("initiator", rl, util.create_player("abc"))
        axe_type = ItemType("axe", 5)
        axe = Item(axe_type, rl)

        hammer_type = ItemType("hammer", 30)
        hammer_type.properties.append(
            EntityTypeProperty(P.DEGRADABLE, {"lifetime": 2 * 24 * 3600}))

        wood_type = ItemType("wood", 40, stackable=True)
        wood_type.properties.append(
            EntityTypeProperty(P.DEGRADABLE, {"lifetime": 10 * 24 * 3600}))

        fuel_group = TypeGroup("group_fuel", stackable=True)
        fuel_group.add_to_group(wood_type)

        other_group = TypeGroup("group_other", stackable=True)
        other_group.add_to_group(wood_type, efficiency=2.0)

        input_req = {
            "group_fuel": {"left": 50, "needed": 200, "used_type": "wood"},
            "group_other": {"left": 0, "needed": 30000, "used_type": "wood"},
            "hammer": {"left": 0, "needed": 1, "used_type": "hammer"},
        }
        activity = Activity(axe, "chopping wood", {},
                            {"input": copy.deepcopy(input_req)}, 100, initiator)

        wood = Item(wood_type, activity, amount=20000, role_being_in=False)
        hammer = Item(hammer_type, activity, role_being_in=False)

        activity.ticks_left = 50
        activity.damage = 1.0  # it needs to be set in ActivitiesProgress

        db.session.add_all([rl, axe_type, axe, activity, wood_type, wood, hammer_type, hammer])

        process = DecayProcess(None)
        process.perform()

        self.assertEqual(50 + ActivityProgressProcess.DEFAULT_PROGRESS, activity.ticks_left)  # progress decreased
        self.assertEqual(input_req, activity.requirements["input"])  # input req shouldn't change, because progress > 0
        self.assertEqual(0.0, hammer.damage)  # input req shouldn't change, because progress > 0

        activity.ticks_left = activity.ticks_needed  # progress = 0, so items will decay

        process = DecayProcess(None)
        process.perform()

        self.assertEqual(activity.ticks_needed, activity.ticks_left)  # progress is 0.0
        self.assertEqual(0.1, wood.damage)  # item used for activity starts to decay
        self.assertEqual(0.5, hammer.damage)

        wood.damage = 1.0  # wood in activity will start to decay

        process = DecayProcess(None)
        process.perform()

        self.assertEqual(19800, wood.amount)
        self.assertEqual(0, Item.query.filter_by(type=hammer_type).count())

        input_req_after_decay = {
            "group_fuel": {"left": 200, "needed": 200},
            "group_other": {"left": 100, "needed": 30000, "used_type": "wood"},
            "hammer": {"left": 1, "needed": 1}
        }
        self.assertEqual(input_req_after_decay, activity.requirements["input"])
