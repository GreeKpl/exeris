from unittest.mock import patch

import sqlalchemy as sql
from flask_testing import TestCase
from shapely.geometry import Point, Polygon

from exeris.core import actions
from exeris.core import deferred
from exeris.core import main, models
from exeris.core import properties
from exeris.core.actions import CreateItemAction, RemoveItemAction, DropItemAction, AddEntityToActivityAction, \
    SayAloudAction, MoveToLocationAction, CreateLocationAction, EatAction, ToggleCloseableAction, CreateCharacterAction, \
    GiveItemAction, JoinActivityAction, SpeakToSomebodyAction, WhisperToSomebodyAction, \
    AbstractAction, Action, CharacterDeathAction, StartControllingMovementAction, \
    ChangeMovementDirectionAction, \
    CollectGatheredResourcesAction, BuryEntityAction, AnimalEatingAction, AnimalStateProgressAction, \
    CollectResourcesFromDomesticatedAnimalAction, LayEggsAction, StartTamingAnimalAction, ActivityProgress, \
    AnimalDeathAction, TakeItemAction, PutIntoStorageAction, CreateLockAndKeyAction, check_space_limitation
from exeris.core.deferred import convert
from exeris.core.general import GameDate
from exeris.core.main import db, Events, Types, States
from exeris.core.models import ItemType, Activity, Item, RootLocation, EntityProperty, TypeGroup, Event, Location, \
    LocationType, Passage, EntityTypeProperty, PassageType, Character, TerrainType, PropertyArea, TerrainArea, \
    Intent, BuriedContent, ResourceArea, UniqueIdentifier, EntityType
from exeris.core.properties import P
from tests import util


class ExampleAction(AbstractAction):
    pass


class ActionsSerializationTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_parameterless_serialization(self):
        action = ExampleAction()

        serialized = deferred.serialize(action)  # serialized into two-element list: [qualname, dict with args]

        self.assertEqual("tests.test_actions.ExampleAction", serialized[0])
        self.assertEqual({}, serialized[1])

    def test_entity_parameter_serialization(self):
        hammer_type = ItemType("hammer", 30)
        hammer = Item(hammer_type, None)
        db.session.add_all([hammer_type, hammer])
        db.session.flush()

        action = RemoveItemAction(hammer)

        serialized = deferred.serialize(action)  # serialized into two-element list: [qualname, dict with args]

        self.assertEqual("exeris.core.actions.RemoveItemAction", serialized[0])
        self.assertEqual({"item": hammer.id, "gracefully": True}, serialized[1])

    def test_nested_action_serialization(self):
        class GoAndPerformAction(Action):
            @convert(executor=Character, action=Action)
            def __init__(self, executor, direction, action):
                super().__init__(executor)
                self.direction = direction
                self.action = action

        rl = RootLocation(Point(1, 1), 35)
        character = util.create_character("abc", rl, util.create_player("AHA"))
        hammer_type = ItemType("hammer", 30)
        hammer = Item(hammer_type, character)
        db.session.add_all([hammer_type, hammer, rl])
        db.session.flush()

        action = GoAndPerformAction(character, 130, RemoveItemAction(hammer, False))

        serialized = deferred.serialize(action)  # serialized into two-element list: [qualname, dict with args]

        self.assertEqual(
            "tests.test_actions.ActionsSerializationTest.test_nested_action_serialization.<locals>.GoAndPerformAction",
            serialized[0])
        self.assertEqual({
            "executor": character.id,
            "direction": 130,
            "action": [
                "exeris.core.actions.RemoveItemAction",
                {"item": hammer.id, "gracefully": False}
            ]}, serialized[1])


class FinishActivityActionsTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_simple_create_item_action(self):
        hammer_type = ItemType("hammer", 200)
        schema_type = ItemType("schema", 0)
        rl = RootLocation(Point(1, 2), 123)
        db.session.add_all([hammer_type, schema_type, rl])

        container = Item(schema_type, rl, weight=111)
        db.session.add(container)

        initiator = util.create_character("ABC", rl, util.create_player("janko"))

        hammer_activity = Activity(container, "dummy_activity_name", {}, {"input": {"potatoes": {
            "needed": 10,
            "left": 0}
        }}, 100, initiator)
        db.session.add(hammer_activity)

        invalid_amount_action = CreateItemAction(item_type=hammer_type, properties={}, amount=0,
                                                 activity=hammer_activity, initiator=initiator, used_materials="all")
        self.assertRaises(ValueError, invalid_amount_action.perform)

        action = CreateItemAction(item_type=hammer_type, properties={"Edible": {"hunger": 5}},
                                  activity=hammer_activity, initiator=initiator, used_materials="all")
        action.perform()

        items = Item.query.filter_by(type=hammer_type).all()
        self.assertEqual(1, len(items))
        self.assertEqual(hammer_type, items[0].type)
        self.assertTrue(items[0].has_property("Edible"))

        with patch("exeris.core.general.GameDate._get_timestamp", new=lambda: 1100):  # stop the time!
            util.initialize_date()
            remove_action = RemoveItemAction(items[0], True)
            remove_action.perform()

            items_count = Item.query.filter_by(type=hammer_type).count()
            self.assertEqual(0, items_count)

    def test_deferred_create_item_action(self):
        util.initialize_date()

        item_type = ItemType("hammer", 200)
        schema_type = ItemType("schema", 0)
        rl = RootLocation(Point(1, 2), 123)
        db.session.add_all([item_type, schema_type, rl])

        container = Item(schema_type, rl, weight=111)
        db.session.add(container)

        initiator = util.create_character("ABC", rl, util.create_player("janko"))

        hammer_activity = Activity(rl, "dummy_activity_name", {}, {}, 100, initiator)
        db.session.add(hammer_activity)

        db.session.flush()
        d = ["exeris.core.actions.CreateItemAction",
             {"item_type": item_type.name, "properties": {"Edible": {"strength": 5.0}},
              "used_materials": "all"}]

        # dump it, then read and run the deferred function
        action = deferred.call(d, activity=hammer_activity, initiator=initiator)

        action.perform()

        # the same tests as in simple test
        items = Item.query.filter_by(type=item_type).all()
        self.assertEqual(1, len(items))
        self.assertEqual(item_type, items[0].type)
        self.assertTrue(items[0].has_property("Edible"))

    def test_create_item_action_considering_input_material_group(self):
        """
        Create a lock and a key in an activity made of iron (for lock) and hard metal group (for key - we use steel)
        For key 'steel' should be "main" in visible_material property
        :return:
        """
        util.initialize_date()

        iron_type = ItemType("iron", 4, stackable=True)
        hard_metal_group = TypeGroup("group_hard_metal", stackable=True)
        steel_type = ItemType("steel", 5, stackable=True)

        hard_metal_group.add_to_group(steel_type, efficiency=0.5)

        lock_type = ItemType("iron_lock", 200, portable=False)
        key_type = ItemType("key", 10)

        rl = RootLocation(Point(1, 1), 213)

        initiator = util.create_character("ABC", rl, util.create_player("janko"))

        db.session.add_all([iron_type, steel_type, hard_metal_group, lock_type, key_type, rl, initiator])
        db.session.flush()

        activity = Activity(rl, "dummy_activity_name", {}, {"input": {
            iron_type.name: {
                "needed": 50, "left": 0, "used_type": iron_type.name,
            },
            hard_metal_group.name: {
                "needed": 1, "left": 0, "used_type": steel_type.name,
            }}}, 1, initiator)
        create_lock_action_args = {"item_type": lock_type.name, "properties": {},
                                   "used_materials": {iron_type.name: 50}}
        create_lock_action = ["exeris.core.actions.CreateItemAction", create_lock_action_args]

        create_key_action_args = {"item_type": key_type.name, "properties": {},
                                  "used_materials": {hard_metal_group.name: 1},
                                  "visible_material": {"main": hard_metal_group.name}}
        create_key_action = ["exeris.core.actions.CreateItemAction", create_key_action_args]
        activity.result_actions = [create_lock_action, create_key_action]

        iron = Item(iron_type, activity, amount=50, role_being_in=False)
        steel = Item(steel_type, activity, amount=20, role_being_in=False)

        db.session.add_all([iron, steel])
        db.session.flush()

        for serialized_action in activity.result_actions:
            action = deferred.call(serialized_action, activity=activity, initiator=initiator)
            action.perform()

        new_lock = Item.query.filter_by(type=lock_type).one()
        used_iron = Item.query.filter(Item.is_used_for(new_lock)).one()
        self.assertEqual(50, used_iron.amount)
        self.assertEqual(200, used_iron.weight)

        iron_piles_left = Item.query.filter_by(type=iron_type).filter(Item.is_in(rl)).count()
        self.assertEqual(0, iron_piles_left)  # no pile of iron, everything was used

        new_key = Item.query.filter_by(type=key_type).one()
        used_steel = Item.query.filter(Item.is_used_for(new_key)).one()
        self.assertEqual(2, used_steel.amount)
        self.assertEqual(10, used_steel.weight)
        self.assertEqual(18, steel.amount)

        visible_material_prop = EntityProperty.query.filter_by(entity=new_key, name=P.VISIBLE_MATERIAL).one()
        self.assertEqual({"main": steel_type.name}, visible_material_prop.data)  # steel is visible

    def test_create_item_action_when_activity_in_location(self):
        hammer_type = ItemType("hammer", 200)
        building_type = LocationType("building", 1000)
        rl = RootLocation(Point(1, 2), 123)
        db.session.add_all([hammer_type, building_type, rl])

        building = Location(rl, building_type)
        db.session.add(building)

        initiator = util.create_character("ABC", rl, util.create_player("janko"))

        hammer_activity = Activity(building, "dummy_activity_name", {}, {"input": {"potatoes": 100}}, 100, initiator)
        db.session.add(hammer_activity)

        create_item_action = CreateItemAction(item_type=hammer_type, properties={}, amount=1,
                                              activity=hammer_activity, initiator=initiator, used_materials="all")

        self.assertEqual([rl, building], create_item_action.get_result_loc_candidates())

        create_item_action.perform()

        new_hammer = Item.query.filter_by(type=hammer_type).one()
        self.assertEqual(initiator, new_hammer.being_in)

    def test_create_location_action(self):
        rl = RootLocation(Point(1, 1), 33)
        building_type = LocationType("building", 500)
        scaffolding_type = ItemType("scaffolding", 200, portable=False)
        scaffolding = Item(scaffolding_type, rl)
        stone_type = ItemType("stone", 10, stackable=True)

        initiator = util.create_character("char", rl, util.create_player("Hyhy"))
        input_requirements = {stone_type.name: {"needed": 5, "left": 0, "used_type": stone_type.name}}
        activity = Activity(scaffolding, "building_building", {}, {"input": input_requirements}, 1, initiator)
        stone = Item(stone_type, activity, amount=20, role_being_in=False)

        db.session.add_all([building_type, scaffolding_type, scaffolding, rl, initiator, activity, stone_type, stone])

        action = CreateLocationAction(location_type=building_type, used_materials="all", properties={P.ENTERABLE: {}},
                                      visible_material={"main": stone_type.name}, activity=activity,
                                      initiator=initiator)
        action.perform()

        new_building = Location.query.filter_by(type=building_type).one()
        Passage.query.filter(Passage.between(rl, new_building)).one()
        self.assertTrue(new_building.has_property(P.ENTERABLE))
        self.assertTrue(new_building.has_property(P.VISIBLE_MATERIAL, main=stone_type.name))

        used_stone = Item.query.filter(Item.is_used_for(new_building)).one()
        self.assertEqual(20, used_stone.amount)

    def test_collect_gathered_resources_action(self):
        potato_type = ItemType("potato", 5, stackable=True)
        carrot_type = ItemType("carrot", 10, stackable=True)
        anvil_type = ItemType("anvil", 200, portable=False)
        rl = RootLocation(Point(1, 1), 134)
        initiator = util.create_character("test", rl, util.create_player("abc"))
        anvil = Item(anvil_type, rl)
        activity = Activity(anvil, "dummy_activity", {}, {}, 1, initiator)
        db.session.add_all([potato_type, anvil_type, rl, anvil, activity])

        collect_resources_action = CollectGatheredResourcesAction(resource_type=potato_type,
                                                                  activity=activity, initiator=initiator)
        collect_resources_action.perform()

        number_of_potato_piles = Item.query.filter_by(type=potato_type).count()  # no resources areas -> no potatoes
        self.assertEqual(0, number_of_potato_piles)

        first_resource_area = models.ResourceArea(potato_type, Point(0, 0), 3, 5, 7)
        db.session.add(first_resource_area)
        other_resource_area = models.ResourceArea(carrot_type, Point(0, 0), 5, 10, 20)
        db.session.add(other_resource_area)

        collect_resources_action = CollectGatheredResourcesAction(resource_type=potato_type,
                                                                  activity=activity, initiator=initiator)
        collect_resources_action.perform()

        result_potato_pile = Item.query.filter_by(type=potato_type).first()
        self.assertEqual(5, result_potato_pile.amount)

        # do it again, but just 2 potatoes left in the resource area
        collect_resources_action = CollectGatheredResourcesAction(resource_type=potato_type,
                                                                  activity=activity, initiator=initiator)
        collect_resources_action.perform()

        self.assertEqual(7, result_potato_pile.amount)

        # remove all old gathered resources
        items = Item.query.filter_by(type=potato_type).all()
        [item.remove() for item in items]

        # start from the beginning
        first_resource_area.amount = 7  # regenerate the first resource area
        second_resource_area = models.ResourceArea(potato_type, Point(0, 0), 3, 3, 2)
        db.session.add(second_resource_area)

        collect_resources_action = CollectGatheredResourcesAction(resource_type=potato_type,
                                                                  activity=activity, initiator=initiator)
        collect_resources_action.perform()

        pile_of_potatoes = Item.query.filter_by(type=potato_type).one()
        # 2.5 is from the first and 1.5 from the second (efficiency/number of areas)
        self.assertEqual(4, pile_of_potatoes.amount)
        self.assertEqual(4.5, first_resource_area.amount)
        self.assertEqual(0.5, second_resource_area.amount)

        collect_resources_action = CollectGatheredResourcesAction(resource_type=potato_type,
                                                                  activity=activity, initiator=initiator)
        collect_resources_action.perform()

        # added 2.5 from the first and 0.5 from the second, because only that is left
        self.assertEqual(4 + 3, pile_of_potatoes.amount)

        collect_resources_action = CollectGatheredResourcesAction(resource_type=potato_type, amount=0.5,
                                                                  activity=activity, initiator=initiator)
        collect_resources_action.perform()

        # added half of 2.5 from the first because amount is a time-based multiplier; 0 from the second
        # then 1.25 is floored to 1
        self.assertEqual(4 + 3 + 1, pile_of_potatoes.amount)

    def test_create_lock_and_key_action(self):
        rl = RootLocation(Point(1, 1), 30)
        initiator = util.create_character("test", rl, util.create_player("abc"))
        building_type = LocationType("building", 300)

        building = Location(rl, building_type, title="chatka")
        key_type = ItemType("key", 20)

        door_to_building = Passage.query.filter(Passage.between(rl, building)).one()
        build_lock_activity = Activity(door_to_building, "building_lock", {}, {}, 1, initiator)

        db.session.add_all([rl, building_type, building, key_type, build_lock_activity])

        door_type = PassageType.by_name(Types.DOOR)
        door_type.properties.append(EntityTypeProperty(P.LOCKABLE, {"lock_exists": False}))

        create_lock_and_key_action = CreateLockAndKeyAction(key_type=key_type,
                                                            activity=build_lock_activity, initiator=initiator)
        create_lock_and_key_action.perform()

        unique_id = UniqueIdentifier.query.one()
        self.assertEqual({
            "lock_exists": True,
            "lock_id": unique_id.value,
        }, door_to_building.get_property(P.LOCKABLE))

        key = Item.query.filter_by(type=key_type).one()
        self.assertEqual(initiator, key.being_in)


class CharacterActionsTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_drop_item_action_on_hammer(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)

        plr = util.create_player("aaa")
        doer = util.create_character("John", rl, plr)
        obs = util.create_character("obs", rl, plr)

        hammer_type = ItemType("stone_hammer", 200)
        hammer = Item(hammer_type, doer, weight=200)

        db.session.add_all([rl, hammer_type, hammer])
        db.session.flush()

        action = DropItemAction(doer, hammer)

        action.perform()

        self.assertEqual(rl, doer.being_in)
        self.assertEqual(rl, hammer.being_in)

        # test events
        event_drop_doer = Event.query.filter_by(type_name=Events.DROP_ITEM + "_doer").one()

        self.assertEqual(hammer.pyslatize(), event_drop_doer.params)
        event_drop_obs = Event.query.filter_by(type_name=Events.DROP_ITEM + "_observer").one()
        self.assertEqual(dict(hammer.pyslatize(), groups={"doer": doer.pyslatize()}), event_drop_obs.params)

    def test_drop_item_action_drop_stackable(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)

        plr = util.create_player("aaa")
        doer = util.create_character("John", rl, plr)
        obs = util.create_character("obs", rl, plr)

        potatoes_type = ItemType("potatoes", 1, stackable=True)
        potatoes = Item(potatoes_type, doer, amount=200)

        db.session.add_all([rl, potatoes_type, potatoes])

        amount = 50
        action = DropItemAction(doer, potatoes, amount)
        action.perform()

        # test events
        event_drop_doer = Event.query.filter_by(type_name=Events.DROP_ITEM + "_doer").one()
        self.assertEqual(potatoes.pyslatize(item_amount=amount), event_drop_doer.params)
        event_drop_obs = Event.query.filter_by(type_name=Events.DROP_ITEM + "_observer").one()
        self.assertEqual(dict(potatoes.pyslatize(item_amount=amount), groups={"doer": doer.pyslatize()}),
                         event_drop_obs.params)
        Event.query.delete()

        self.assertEqual(150, potatoes.weight)  # 50 of 200 was dropped
        potatoes_on_ground = Item.query.filter(Item.is_in(rl)).filter_by(type=potatoes_type).one()
        self.assertEqual(50, potatoes_on_ground.weight)

        action = DropItemAction(doer, potatoes, 150)
        action.perform()
        db.session.flush()  # to correctly check deletion

        self.assertIsNone(potatoes.being_in)  # check whether the object is deleted
        self.assertIsNone(potatoes.used_for)
        self.assertTrue(sql.inspect(potatoes).deleted)

        self.assertEqual(200, potatoes_on_ground.weight)

    def test_drop_item_action_on_stackable_with_parts(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        plr = util.create_player("aaa")
        doer = util.create_character("John", rl, plr)
        obs = util.create_character("obs", rl, plr)

        potatoes_type = ItemType("potatoes", 1, stackable=True)
        strawberries_type = ItemType("strawberries", 5, stackable=True)
        grapes_type = ItemType("grapes", 3, stackable=True)
        cake_type = ItemType("cake", 100, stackable=True)

        # check multipart resources
        cake_in_inv = Item(cake_type, doer, weight=300)
        cake_ground = Item(cake_type, rl, weight=300)
        other_cake_ground = Item(cake_type, rl, weight=300)

        db.session.add_all([rl, strawberries_type, grapes_type, cake_type, cake_in_inv, cake_ground, other_cake_ground])
        db.session.flush()

        cake_in_inv.visible_parts = [grapes_type.name, strawberries_type.name]
        cake_ground.visible_parts = [grapes_type.name, strawberries_type.name]

        other_cake_ground.visible_parts = [strawberries_type.name, potatoes_type.name]

        db.session.flush()

        action = DropItemAction(doer, cake_in_inv, 1)
        action.perform()

        self.assertEqual(200, cake_in_inv.weight)
        self.assertEqual(400, cake_ground.weight)
        self.assertEqual(300, other_cake_ground.weight)  # it isn't merged with different cake

        db.session.delete(cake_ground)  # remove cake with the same parts

        action = DropItemAction(doer, cake_in_inv, 1)
        action.perform()

        self.assertEqual(100, cake_in_inv.weight)
        self.assertEqual(300, other_cake_ground.weight)

        new_ground_cake = Item.query.filter(Item.is_in(rl)).filter_by(type=cake_type). \
            filter_by(visible_parts=[grapes_type.name, strawberries_type.name]).one()
        self.assertEqual(100, new_ground_cake.weight)
        self.assertEqual([grapes_type.name, strawberries_type.name], new_ground_cake.visible_parts)

    def test_drop_action_failure_not_in_inv(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        char = util.create_character("John", rl, util.create_player("aaa"))

        hammer_type = ItemType("stone_hammer", 200)

        # hammer is already on the ground
        hammer = Item(hammer_type, rl, weight=200)

        db.session.add_all([rl, hammer_type, hammer])

        action = DropItemAction(char, hammer)
        self.assertRaises(main.EntityNotInInventoryException, action.perform)

    def test_drop_action_failure_too_little_potatoes(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        char = util.create_character("John", rl, util.create_player("aaa"))

        # there are too little potatoes
        potatoes_type = ItemType("potatoes", 20, stackable=True)

        potatoes = Item(potatoes_type, char, amount=10)

        db.session.add_all([potatoes_type, potatoes])
        db.session.flush()

        action = DropItemAction(char, potatoes, 201)
        self.assertRaises(main.InvalidAmountException, action.perform)

    def test_add_item_to_activity_action(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        initiator = util.create_character("John", rl, util.create_player("aaa"))
        observer = util.create_character("obs", rl, util.create_player("abc"))

        anvil_type = ItemType("anvil", 400, portable=False)
        anvil = Item(anvil_type, rl)
        metal_group = TypeGroup("group_metal", stackable=True)
        iron_type = ItemType("iron", 10, stackable=True)
        metal_group.add_to_group(iron_type, efficiency=0.5)

        iron = Item(iron_type, initiator, amount=20)

        db.session.add_all([rl, initiator, anvil_type, anvil, metal_group, iron_type, iron])
        db.session.flush()

        activity = Activity(anvil, "dummy_activity_name", {}, {
            "input": {
                metal_group.name: {"needed": 10, "left": 10}
            }
        }, 1, initiator)

        action = AddEntityToActivityAction(initiator, iron, activity, 4)
        action.perform()

        self.assertEqual({metal_group.name: {"needed": 10, "left": 8, "used_type": iron_type.name}},
                         activity.requirements["input"])
        self.assertEqual(16, iron.amount)

        action = AddEntityToActivityAction(initiator, iron, activity, 16)
        action.perform()

        self.assertEqual({metal_group.name: {"needed": 10, "left": 0, "used_type": iron_type.name}},
                         activity.requirements["input"])
        self.assertIsNone(iron.parent_entity)
        self.assertTrue(sql.inspect(iron).deleted)
        Event.query.delete()

        # TEST TYPE MATCHING MULTIPLE REQUIREMENT GROUPS

        wood_group = TypeGroup("group_wood", stackable=True)
        fuel_group = TypeGroup("group_fuel", stackable=True)
        oak_type = ItemType("oak", 50, stackable=True)
        wood_group.add_to_group(oak_type)
        fuel_group.add_to_group(oak_type)

        oak = Item(oak_type, initiator, amount=20)
        db.session.add_all([wood_group, oak_type, fuel_group, oak])

        activity = Activity(anvil, "dummy_activity_name", {}, {
            "input": {
                metal_group.name: {"needed": 10, "left": 10},
                fuel_group.name: {"needed": 10, "left": 10},
                wood_group.name: {"needed": 10, "left": 10},
            }
        }, 1, initiator)
        db.session.add(activity)

        action = AddEntityToActivityAction(initiator, oak, activity, 20)  # added as the first material from the list
        action.perform()

        # in this case oak should be added as fuel, because material groups are sorted and applied alphabetically
        # always exactly one group can be fulfilled at once
        self.assertEqual({
            metal_group.name: {"needed": 10, "left": 10},
            fuel_group.name: {"needed": 10, "left": 0, "used_type": oak_type.name},
            wood_group.name: {"needed": 10, "left": 10},
        }, activity.requirements["input"])

        self.maxDiff = None
        event_add_doer = Event.query.filter_by(type_name=Events.ADD_TO_ACTIVITY + "_doer").one()
        self.assertEqual({"groups": {
            "item": oak.pyslatize(item_amount=10),
            "activity": activity.pyslatize(),
        }}, event_add_doer.params)

        event_add_obs = Event.query.filter_by(type_name=Events.ADD_TO_ACTIVITY + "_observer").one()
        self.assertEqual({
            "groups": {
                "item": oak.pyslatize(item_amount=10),
                "activity": activity.pyslatize(),
                "doer": initiator.pyslatize(),
            }
        }, event_add_obs.params)
        Event.query.delete()

        action = AddEntityToActivityAction(initiator, oak, activity, 10)
        action.perform()  # add materials to another group

        self.assertEqual({
            metal_group.name: {"needed": 10, "left": 10},
            fuel_group.name: {"needed": 10, "left": 0, "used_type": oak_type.name},
            wood_group.name: {"needed": 10, "left": 0, "used_type": oak_type.name},
        }, activity.requirements["input"])
        self.assertTrue(sql.inspect(oak).deleted)

    def test_add_nonstackable_item_to_activity(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 111)
        initiator = util.create_character("John", rl, util.create_player("aaa"))

        anvil_type = ItemType("anvil", 400, portable=False)
        anvil = Item(anvil_type, rl)
        tools_group = TypeGroup("group_tools", stackable=False)
        hammer_type = ItemType("hammer", 10, stackable=False)
        tools_group.add_to_group(hammer_type, efficiency=5.0)

        hammer = Item(hammer_type, initiator, quality=1.5)

        db.session.add_all([rl, initiator, anvil_type, anvil, tools_group, hammer_type, hammer])
        db.session.flush()

        activity = Activity(anvil, "dummy_activity_name", {}, {
            "input": {
                tools_group.name: {"needed": 10, "left": 10}
            }
        }, 1, initiator)

        action = AddEntityToActivityAction(initiator, hammer, activity, 1)
        action.perform()

        self.assertEqual({tools_group.name: {"needed": 10, "left": 9, "used_type": hammer_type.name, "quality": 0.75}},
                         activity.requirements["input"])
        self.assertEqual(activity, hammer.used_for)

    def test_take_from_storage_action(self):
        util.initialize_date()
        rl = RootLocation(Point(1, 1), 10)
        char = util.create_character("abda", rl, util.create_player("adqw"))
        building_type = LocationType("building", 1000)
        loc1 = Location(rl, building_type)
        basket_type = ItemType("basket", 100)
        basket_type.properties.append(EntityTypeProperty(P.STORAGE))
        hammer_type = ItemType("hammer", 50)

        basket_in_rl = Item(basket_type, rl)
        basket_in_loc1 = Item(basket_type, loc1)
        db.session.add_all([rl, building_type, basket_type, hammer_type, loc1, basket_in_rl, basket_in_loc1])

        # take hammer from the ground
        hammer = Item(hammer_type, rl)
        take_from_storage_action = TakeItemAction(char, hammer)
        take_from_storage_action.perform()
        self.assertEqual(char, hammer.being_in)

        # take hammer from the storage in the same location
        hammer.being_in = basket_in_rl
        take_from_storage_action = TakeItemAction(char, hammer)
        take_from_storage_action.perform()
        self.assertEqual(char, hammer.being_in)

        # take hammer from the neighbouring location
        hammer.being_in = loc1
        take_from_storage_action = TakeItemAction(char, hammer)
        take_from_storage_action.perform()
        self.assertEqual(char, hammer.being_in)

        # take hammer from the storage in the neighbouring location
        hammer.being_in = basket_in_loc1
        take_from_storage_action = TakeItemAction(char, hammer)
        take_from_storage_action.perform()
        self.assertEqual(char, hammer.being_in)

    def test_take_item_unsuccessful_when_limited_space_exceeded(self):
        util.initialize_date()
        rl = RootLocation(Point(1, 1), 10)
        building_type = LocationType("building", 2000)
        building_type.properties.append(EntityTypeProperty(P.LIMITED_SPACE, {
            "max_weight": models.ALIVE_CHARACTER_WEIGHT + 10
        }))
        building = Location(rl, building_type)
        char = util.create_character("abda", rl, util.create_player("adqw"))
        hammer_type = ItemType("hammer", 50)
        hammer = Item(hammer_type, rl)
        db.session.add_all([rl, hammer_type, hammer])

        char_limited_space_prop = EntityTypeProperty(P.LIMITED_SPACE, {"max_weight": 10})
        EntityType.by_name(Types.ALIVE_CHARACTER).properties.append(char_limited_space_prop)
        take_item_action = TakeItemAction(char, hammer)
        self.assertRaises(main.OwnInventoryCapacityExceededException, take_item_action.perform)

        hammer.being_in = rl
        char.being_in = building
        char_limited_space_prop.data["max_weight"] = 100

        self.assertRaises(main.EntityCapacityExceeded, take_item_action.perform)

    def test_put_into_storage_action(self):
        util.initialize_date()
        rl = RootLocation(Point(1, 1), 10)
        char = util.create_character("abda", rl, util.create_player("adqw"))
        building_type = LocationType("building", 1000)
        loc_storage_type = LocationType("loc_storage", 400)
        loc1 = Location(rl, building_type)
        loc2_storage = Location(rl, loc_storage_type)
        basket_type = ItemType("basket", 100)
        basket_type.properties.append(EntityTypeProperty(P.STORAGE, {"can_store": True}))
        hammer_type = ItemType("hammer", 50)

        basket_in_rl = Item(basket_type, rl)
        basket_in_inventory = Item(basket_type, char)
        basket_in_loc1 = Item(basket_type, loc1)
        hammer = Item(hammer_type, rl)
        db.session.add_all([rl, building_type, basket_type, hammer_type, loc1, basket_in_rl, basket_in_loc1,
                            loc_storage_type, loc2_storage, basket_in_inventory, hammer])

        # put hammer from the ground to the storage on the ground
        put_into_storage_action = PutIntoStorageAction(char, hammer, basket_in_rl)
        put_into_storage_action.perform()
        self.assertEqual(hammer.being_in, basket_in_rl)

        # put hammer from the inventory to the storage on the ground
        hammer.being_in = char
        put_into_storage_action = PutIntoStorageAction(char, hammer, basket_in_rl)
        put_into_storage_action.perform()
        self.assertEqual(hammer.being_in, basket_in_rl)

        # put hammer from the ground to the storage in the inventory
        hammer.being_in = rl
        put_into_storage_action = PutIntoStorageAction(char, hammer, basket_in_inventory)
        put_into_storage_action.perform()
        self.assertEqual(hammer.being_in, basket_in_inventory)

        # it's impossible to put hammer to the storage in the neighbouring location (event with an unlimited passage)
        hammer.being_in = rl
        put_into_storage_action = PutIntoStorageAction(char, hammer, basket_in_loc1)
        self.assertRaises(main.EntityTooFarAwayException, put_into_storage_action.perform)

    def test_say_aloud_action(self):
        util.initialize_date()

        grass_type = TerrainType("grassland")
        TypeGroup.by_name(main.Types.LAND_TERRAIN).add_to_group(grass_type)
        grass_poly = Polygon([(0, 0), (0, 30), (30, 30), (30, 0)])
        grass_terrain = TerrainArea(grass_poly, grass_type)
        grass_visibility_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, grass_poly, grass_terrain)

        db.session.add_all([grass_type, grass_terrain, grass_visibility_area])

        rl1 = RootLocation(Point(0, 0), 123)
        rl2 = RootLocation(Point(0, 11), 123)
        rl3 = RootLocation(Point(0, 21), 123)
        building_type = LocationType("building", 200)
        building = Location(rl1, building_type)
        plr = util.create_player("eee")
        doer = util.create_character("doer", building, plr)
        obs_same_loc = util.create_character("obs_same_loc", building, plr)
        obs_near_loc = util.create_character("obs_near_loc", rl2, plr)

        door_to_building = Passage.query.filter(Passage.between(rl1, building)).one()
        closeable_property = EntityProperty(P.CLOSEABLE, {"closed": True})
        door_to_building.properties.append(closeable_property)

        db.session.add_all([rl1, rl2, rl3, building_type, building, doer])

        # no window in building -> nobody but obs_same_loc can hear it
        message_text = "Hello!"
        action = SayAloudAction(doer, message_text)
        action.perform()

        event_say_doer = Event.query.filter_by(type_name=Events.SAY_ALOUD + "_doer").one()
        self.assertEqual({"message": message_text}, event_say_doer.params)
        self.assertCountEqual([doer], event_say_doer.observers)

        event_say_observer = Event.query.filter_by(type_name=Events.SAY_ALOUD + "_observer").one()
        self.assertEqual({"groups": {"doer": doer.pyslatize()}, "message": message_text}, event_say_observer.params)
        self.assertCountEqual([obs_same_loc], event_say_observer.observers)

        closeable_property.data = {"closed": False}

        # now there will be open connection between rl1 and building

        # clean up the events
        Event.query.delete()

        action = SayAloudAction(doer, message_text)
        action.perform()

        event_say_doer = Event.query.filter_by(type_name=Events.SAY_ALOUD + "_doer").one()
        self.assertEqual({"message": message_text}, event_say_doer.params)
        self.assertCountEqual([doer], event_say_doer.observers)

        event_say_observer = Event.query.filter_by(type_name=Events.SAY_ALOUD + "_observer").one()
        self.assertEqual({"groups": {"doer": doer.pyslatize()}, "message": message_text}, event_say_observer.params)
        self.assertCountEqual([obs_same_loc, obs_near_loc], event_say_observer.observers)

    def test_speak_to_somebody_action(self):
        util.initialize_date()

        rl = RootLocation(Point(13, 15), 123)

        doer = util.create_character("doer", rl, util.create_player("eee1"))
        listener = util.create_character("listener", rl, util.create_player("eee2"))
        observer = util.create_character("obs_same_loc", rl, util.create_player("eee3"))
        db.session.add(rl)

        speak_to_somebody = SpeakToSomebodyAction(doer, listener, "ABC")
        speak_to_somebody.perform()

        event_doer = Event.query.filter_by(type_name=Events.SPEAK_TO_SOMEBODY + "_doer").one()
        event_observer = Event.query.filter_by(type_name=Events.SPEAK_TO_SOMEBODY + "_observer").one()

        self.assertEqual({"message": "ABC", "groups": {"target": listener.pyslatize()}}, event_doer.params)
        self.assertEqual({"message": "ABC", "groups": {"doer": doer.pyslatize(), "target": listener.pyslatize()}},
                         event_observer.params)

    def test_whisper_to_somebody_action(self):
        util.initialize_date()

        rl = RootLocation(Point(13, 15), 123)

        doer = util.create_character("doer", rl, util.create_player("eee1"))
        listener = util.create_character("listener", rl, util.create_player("eee2"))
        observer = util.create_character("obs_same_loc", rl, util.create_player("eee3"))
        db.session.add(rl)
        db.session.flush()

        whisper_to_somebody = WhisperToSomebodyAction(doer, listener, "ABC")
        whisper_to_somebody.perform()

        event_doer = Event.query.filter_by(type_name=Events.WHISPER + "_doer").one()
        event_observer = Event.query.filter_by(type_name=Events.WHISPER + "_observer").one()

        self.assertEqual({"message": "ABC", "groups": {"target": listener.pyslatize()}}, event_doer.params)
        self.assertEqual({"message": "ABC", "groups": {"doer": doer.pyslatize(), "target": listener.pyslatize()}},
                         event_observer.params)

    def test_enter_building_there_and_back_again_success(self):
        util.initialize_date()

        building_type = LocationType("building", 200)
        rl = RootLocation(Point(1, 1), 222)
        building = Location(rl, building_type, title="Small hut")
        building_type.properties.append(EntityTypeProperty(P.ENTERABLE))

        char = util.create_character("John", rl, util.create_player("Eddy"))

        db.session.add_all([rl, building_type, building])

        passage = Passage.query.filter(Passage.between(rl, building)).one()
        enter_loc_action = MoveToLocationAction(char, passage)
        enter_loc_action.perform()

        self.assertEqual(building, char.being_in)

        enter_loc_action = MoveToLocationAction(char, passage)
        enter_loc_action.perform()
        self.assertEqual(rl, char.being_in)

    def test_eat_action_success(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 222)
        char = util.create_character("John", rl, util.create_player("Eddy"))

        potatoes_type = ItemType("potatoes", 10, stackable=True)
        potatoes = Item(potatoes_type, char, amount=30)

        potatoes_type.properties.append(
            EntityTypeProperty(P.EDIBLE, data={
                "states": {"satiation": 0.01, "hunger": 0.2, "strength": 0.3}
            }))

        db.session.add_all([rl, potatoes_type, potatoes])

        action = EatAction(char, potatoes, 3)
        action.perform()

        self.assertAlmostEqual(0.03, char.states["satiation"])
        self.assertAlmostEqual(0.6, char.eating_queue["hunger"])
        self.assertAlmostEqual(0.9, char.eating_queue["strength"])

    def test_find_and_eat_animal_food_action(self):
        self._set_up_entities_for_animal_eating()
        grass_type = ItemType.by_name("grass")
        rl = RootLocation.query.one()
        cow_type = LocationType.by_name("cow")
        cow = Location.query.filter_by(type=cow_type).one()

        grass_area = ResourceArea(grass_type, Point(1, 1), 5, 3, 8)
        db.session.add(grass_area)

        cow.states[States.HUNGER] = 0.15
        # try to eat grass from the resource area
        find_and_eat_animal_food = AnimalEatingAction(cow)
        find_and_eat_animal_food.perform()

        self.assertEqual(0, cow.states[States.HUNGER])
        self.assertEqual(5, grass_area.amount)

        # try again, but with less amount left
        cow.states[States.HUNGER] = 0.35
        find_and_eat_animal_food.perform()

        # only 3 pieces of food eaten, because amount is capped by efficiency
        self.assertAlmostEqual(0.15, cow.states[States.HUNGER])
        self.assertEqual(2, grass_area.amount)

        basket_type = ItemType("basket", 100)
        basket_type.properties.append(EntityTypeProperty(P.STORAGE))
        basket = Item(basket_type, rl)
        grass_in_basket = Item(grass_type, basket, amount=20)
        db.session.add_all([basket_type, basket, grass_in_basket])

        # eat first from resource area and then from basket
        cow.states[States.HUNGER] = 0.2
        find_and_eat_animal_food.perform()

        self.assertAlmostEqual(0, cow.states[States.HUNGER])
        self.assertEqual(0, grass_area.amount)

        # 19 would be better, but 18 is because of precision of floating point arithmetics
        self.assertIn(grass_in_basket.amount, [18, 19])

    def _set_up_entities_for_animal_eating(self):
        rl = RootLocation(Point(1, 1), 100)
        cow_type = LocationType("cow", 100)
        cow_type.properties.append(EntityTypeProperty(P.ANIMAL))
        cow_type.properties.append(EntityTypeProperty(P.STATES, {
            States.HUNGER: {"initial": 0},
        }))

        cow = Location(rl, cow_type, PassageType.by_name(Types.INVISIBLE_PASSAGE))

        grass_type = ItemType("grass", 10, stackable=True)
        grass_type.properties.append(
            EntityTypeProperty(P.EDIBLE_BY_ANIMAL, {
                "states": {
                    States.HUNGER: -0.1
                },
                "eater_types": ["herbivore"],
            }))
        herbivore_group = TypeGroup("herbivore")
        herbivore_group.add_to_group(cow_type)

        db.session.add_all([rl, cow_type, cow, grass_type, herbivore_group])

    def test_animal_states_progress_action(self):
        rl = RootLocation(Point(1, 1), 100)
        milk_type = ItemType("milk", 10, stackable=True)
        cow_type = LocationType("cow", 100)
        cow_type.properties.append(EntityTypeProperty(P.ANIMAL, {
            "type_resources": {
                milk_type.name: {
                    "initial": 0,
                    "max": 100,
                },
            },
        }))
        cow_type.properties.append(EntityTypeProperty(P.DOMESTICATED, {
            "type_resources_increase": {
                "milkiness": {
                    "initial": 0.1,
                    "affected_resources": {
                        milk_type.name: 10,
                    },
                },
            }
        }))

        cow = Location(rl, cow_type, PassageType.by_name(Types.INVISIBLE_PASSAGE))
        cow_animal_prop = EntityProperty(P.ANIMAL, {
            "resources": {
                milk_type.name: 0,
            }
        })
        cow.properties.append(cow_animal_prop)
        cow_domesticated_prop = EntityProperty(P.DOMESTICATED, {
            "resources_increase": {
                "milkiness": 0.1,
            }
        })
        cow.properties.append(cow_domesticated_prop)
        db.session.add_all([rl, cow_type, cow, milk_type])

        animal_state_progress_action = AnimalStateProgressAction(cow)
        animal_state_progress_action.perform()
        self.assertEqual(1, cow_animal_prop.data["resources"][milk_type.name])

        # non-default milkiness
        cow_domesticated_prop.data["resources_increase"]["milkiness"] = 0.5
        animal_state_progress_action = AnimalStateProgressAction(cow)
        animal_state_progress_action.perform()
        self.assertEqual(1 + 5, cow_animal_prop.data["resources"][milk_type.name])

        cow_animal_prop.data["resources"][milk_type.name] = 98
        animal_state_progress_action = AnimalStateProgressAction(cow)
        animal_state_progress_action.perform()
        self.assertEqual(100, cow_animal_prop.data["resources"][milk_type.name])

    def test_collect_resources_from_domesticated_animal_action(self):
        rl = RootLocation(Point(1, 1), 100)
        milk_type = ItemType("milk", 10, stackable=True)
        cow_type = LocationType("cow", 100)
        cow_type.properties.append(EntityTypeProperty(P.ANIMAL, {
            "type_resources": {
                milk_type.name: {
                    "initial": 0,
                    "max": 100,
                },
            },
        }))

        cow_type.properties.append(EntityTypeProperty(P.DOMESTICATED, {
            "type_resources_increase": {
                "milkiness": {
                    "initial": 1,
                    "affected_resources": {
                        milk_type.name: 1,
                    },
                },
            }
        }))

        char = util.create_character("abc", rl, util.create_player("def"))
        cow = Location(rl, cow_type, PassageType.by_name(Types.INVISIBLE_PASSAGE))
        cow_animal_prop = EntityProperty(P.ANIMAL, {
            "resources": {
                milk_type.name: 0,
            }
        })
        cow.properties.append(EntityProperty(P.DOMESTICATED, {
            "resources_increase": {
                "milkiness": 1,
            }
        }))
        cow.properties.append(cow_animal_prop)
        activity = Activity(cow, "milking_cow", {}, {}, 1, char)
        db.session.add_all([rl, cow_type, cow, milk_type, activity])
        cow_animal_prop.data["resources"][milk_type.name] = 17
        collect_resources_from_animal = CollectResourcesFromDomesticatedAnimalAction(resource_type=milk_type,
                                                                                     activity=activity, initiator=char)
        collect_resources_from_animal.perform()

        self.assertEqual(0, cow_animal_prop.data["resources"][milk_type.name])
        milk_in_inventory = Item.query.filter_by(type=milk_type).one()
        self.assertEqual(17, milk_in_inventory.amount)

    def test_animal_laying_eggs_action(self):
        rl = RootLocation(Point(1, 1), 100)
        egg_type = ItemType("eggs", 10, stackable=True)
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

        hen = Item(hen_type, rl)
        hen_animal_prop = EntityProperty(P.ANIMAL, {
            "resources": {
                egg_type.name: 0,
            }
        })
        hen.properties.append(hen_animal_prop)
        hen.properties.append(EntityProperty(P.DOMESTICATED, {
            "resources_increase": {
                "eggs_increase": 1,
            }
        }))
        db.session.add_all([rl, egg_type, hen_type, hen])

        hen_animal_prop.data["resources"][egg_type.name] = 4
        lay_eggs_action = LayEggsAction(hen)
        lay_eggs_action.perform()
        # nothing should happen, because level of eggs is not equal to maximum allowed
        self.assertEqual(0, Item.query.filter_by(type=egg_type).count())

        hen_animal_prop.data["resources"][egg_type.name] = 5
        lay_eggs_action = LayEggsAction(hen)
        lay_eggs_action.perform()
        # should create eggs on the ground
        eggs_on_ground = Item.query.filter_by(type=egg_type).filter(Item.is_in(rl)).one()
        self.assertEqual(5, eggs_on_ground.amount)

        eggs_on_ground.remove()
        nest_type = ItemType("nest", 100, portable=False)
        nest_type.properties.append(EntityTypeProperty(P.BIRD_NEST))
        nest = Item(nest_type, rl)
        db.session.add_all([nest_type, nest])

        # lay eggs again, but now they should land in the nest
        hen_animal_prop.data["resources"][egg_type.name] = 5
        lay_eggs_action = LayEggsAction(hen)
        lay_eggs_action.perform()

        eggs_in_nest = Item.query.filter_by(type=egg_type).filter(Item.is_in(nest)).one()
        self.assertEqual(5, eggs_in_nest.amount)

    def test_animal_death_action(self):
        rl = RootLocation(Point(1, 1), 100)

        beef_type = ItemType("beef", 20, stackable=True)
        cow_head_type = ItemType("cow_head", 50, stackable=True)

        dead_cow_type = LocationType("dead_cow", 100)
        cow_type = LocationType("cow", 100)
        cow_type.properties.append(EntityTypeProperty(P.ANIMAL, {
            "type_resources": {
                beef_type.name: {
                    "initial": 0,
                    "max": 100,
                },
                cow_head_type.name: {
                    "initial": 1,
                    "max": 1,
                }
            },
            "dead_type": dead_cow_type.name,
        }))

        cow = Location(rl, cow_type, PassageType.by_name(Types.INVISIBLE_PASSAGE))
        cow.properties.append(EntityProperty(P.ANIMAL, {
            "resources": {
                beef_type.name: 100,
                cow_head_type.name: 1,
            }
        }))

        db.session.add_all([rl, cow_type, beef_type, cow_head_type, cow, dead_cow_type])
        db.session.flush()

        animal_death_action = AnimalDeathAction(cow)
        animal_death_action.perform()

        self.assertEqual(dead_cow_type, cow.type)
        self.assertFalse(cow.has_property(P.ANIMAL))
        self.assertFalse(cow.has_property(P.DOMESTICATED))

        # amount of resources inside
        cow_heads_pile = Item.query.filter_by(type=cow_head_type).filter(Item.is_in(cow)).one()
        self.assertEqual(1, cow_heads_pile.amount)
        beef_pile = Item.query.filter_by(type=beef_type).filter(Item.is_in(cow)).one()
        self.assertEqual(100, beef_pile.amount)

    def test_taming_animal_action(self):
        util.initialize_date()
        stallion_type = LocationType("stallion", 400)
        stallion_type.properties.append(EntityTypeProperty(P.ANIMAL))
        stallion_type.properties.append(EntityTypeProperty(P.DOMESTICATED))
        stallion_type.properties.append(EntityTypeProperty(P.TAMABLE))

        wild_stallion_type = LocationType("wild_stallion", 400)
        wild_stallion_type.properties.append(EntityTypeProperty(P.ANIMAL))
        wild_stallion_type.properties.append(EntityTypeProperty(P.TAMABLE, {
            "domesticated_type": stallion_type.name
        }))

        rl = RootLocation(Point(1, 1), 300)
        first_owner = util.create_character("first_owner", rl, util.create_player("aldw"))
        invisible_passage = PassageType.by_name(Types.INVISIBLE_PASSAGE)
        wild_stallion = Location(rl, wild_stallion_type, passage_type=invisible_passage)
        db.session.add_all([stallion_type, wild_stallion_type, rl, wild_stallion])

        start_taming_animal_action = StartTamingAnimalAction(first_owner, wild_stallion)
        start_taming_animal_action.perform()

        taming_activity = Activity.query.one()
        self.assertEqual("exeris.core.actions.TurnIntoDomesticatedSpecies", taming_activity.result_actions[0][0])
        self.assertEqual("exeris.core.actions.MakeAnimalTrustInitiator", taming_activity.result_actions[1][0])

        ActivityProgress.finish_activity(taming_activity)

        # activity succeeds, the wild animal is now a domesticated one which trusts the first_owner
        stallion = Location.query.filter_by(type=stallion_type).one()
        self.assertTrue(stallion.has_property(P.DOMESTICATED))
        self.assertEqual({str(first_owner.id): 1.0}, stallion.get_property(P.DOMESTICATED)["trusted"])

        db.session.delete(taming_activity)

        other_char = util.create_character("other_char", rl, util.create_player("kodw"))
        start_taming_animal_action = StartTamingAnimalAction(other_char, stallion)
        start_taming_animal_action.perform()

        new_taming_activity = Activity.query.one()

        self.assertEqual(other_char, new_taming_activity.initiator)
        ActivityProgress.finish_activity(new_taming_activity)

        self.assertEqual({str(first_owner.id): 0.9, str(other_char.id): 1.0},
                         stallion.get_property(P.DOMESTICATED)["trusted"])

    def test_create_open_then_close_then_open_action(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 222)
        strange_passage_type = PassageType("strange_passage", False)
        building_type = LocationType("building", 100)
        building = Location(rl, building_type, passage_type=strange_passage_type)
        char = util.create_character("John", rl, util.create_player("Eddy"))

        closeable_passage = Passage.query.filter(Passage.between(rl, building)).one()

        # it's open by default
        strange_passage_type.properties.append(EntityTypeProperty(P.CLOSEABLE, {"closed": False}))

        db.session.add_all([rl, strange_passage_type, building_type, building])

        self.assertEqual(True, closeable_passage.is_open())

        closeable_action = ToggleCloseableAction(char, closeable_passage)  # toggle to closed
        closeable_action.perform()

        self.assertEqual(False, closeable_passage.is_open())

        closeable_action = ToggleCloseableAction(char, closeable_passage)  # toggle to open
        closeable_action.perform()

        self.assertEqual(True, closeable_passage.is_open())

    def test_give_stackable_item_action_give_6_and_then_try_to_give_too_much(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)

        plr = util.create_player("ala123")
        giver = util.create_character("postac", rl, plr)
        receiver = util.create_character("postac", rl, plr)
        potatoes_type = ItemType("potatoes", 5, stackable=True)
        potatoes = Item(potatoes_type, giver, amount=10)

        db.session.add_all([rl, potatoes_type, potatoes])

        give_action = GiveItemAction(giver, potatoes, receiver, amount=4)
        give_action.perform()

        potatoes_of_giver = Item.query.filter_by(type=potatoes_type).filter(Item.is_in(giver)).one()
        potatoes_of_receiver = Item.query.filter_by(type=potatoes_type).filter(Item.is_in(receiver)).one()

        self.assertEqual(6, potatoes_of_giver.amount)
        self.assertEqual(4, potatoes_of_receiver.amount)

        give_action = GiveItemAction(giver, potatoes, receiver, amount=8)
        self.assertRaises(main.InvalidAmountException, give_action.perform)

    def test_give_stackable_exceeding_limited_space(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)

        plr = util.create_player("ala123")
        giver = util.create_character("postac", rl, plr)
        receiver = util.create_character("druga_postac", rl, plr)
        potatoes_type = ItemType("potatoes", 5, stackable=True)
        potatoes = Item(potatoes_type, giver, amount=10)
        EntityType.by_name(Types.ALIVE_CHARACTER).properties \
            .append(EntityTypeProperty(P.LIMITED_SPACE, {"max_weight": 10}))
        db.session.add_all([rl, potatoes_type, potatoes])

        give_item_action = GiveItemAction(giver, potatoes, receiver, amount=10)
        self.assertRaises(main.TargetInventoryCapacityExceededException, give_item_action.perform)

        potatoes = Item.query.filter_by(type=potatoes_type).filter(Item.is_in(receiver)).one()
        potatoes.being_in = giver
        # successful
        give_item_action = GiveItemAction(giver, potatoes, receiver, amount=2)
        give_item_action.perform()

    def test_join_activity_action_try_join_too_far_away_and_then_success(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)
        worker = util.create_character("postac", rl, util.create_player("ala123"))
        anvil_type = ItemType("anvil", 300, portable=False)
        anvil = Item(anvil_type, rl)
        activity = Activity(None, "activity", {"data": True}, {}, 11, worker)

        db.session.add_all([rl, anvil_type, anvil, activity])

        join_activity_action = JoinActivityAction(worker, activity)
        self.assertRaises(main.TooFarFromActivityException, join_activity_action.perform)

        activity.being_in = anvil

        join_activity_action = JoinActivityAction(worker, activity)
        join_activity_action.perform()

    def test_death_action(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)
        char = util.create_character("postac", rl, util.create_player("ala123"))

        db.session.add(rl)

        action = CharacterDeathAction(char)
        action.perform()

        self.assertEqual(main.Types.DEAD_CHARACTER, char.type.name)
        self.assertAlmostEqual(GameDate.now().game_timestamp, char.get_property(P.DEATH_INFO)["date"], delta=3)
        self.assertAlmostEqual(GameDate.now().game_timestamp, char.get_property(P.DEATH_INFO)["date"], delta=3)

    def test_burying_entity(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)
        coffin_type = ItemType("coffin", 100, portable=True)
        coffin_type.properties.append(EntityTypeProperty(P.BURYABLE))

        coffin = Item(coffin_type, rl)
        db.session.add_all([rl, coffin_type, coffin])

        bury_entity_action = BuryEntityAction(coffin)
        bury_entity_action.perform()

        buried_content = BuriedContent.query.one()
        self.assertEqual(Point(1, 1), buried_content.position)

        self.assertEqual(buried_content, coffin.being_in)


class IntentTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_perform_deferrable_action(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)
        rl_very_far_away = RootLocation(Point(200, 200), 11)
        char = util.create_character("postac", rl, util.create_player("ala123"))

        hammer_type = ItemType("stone_hammer", 200)

        # hammer is already on the ground
        hammer = Item(hammer_type, rl_very_far_away)
        db.session.add_all([rl, rl_very_far_away, hammer_type, hammer])

        take_action = TakeItemAction(char, hammer)
        deferred.perform_or_turn_into_intent(char, take_action)

        # check if intent parameters were correctly guessed
        self.assertEqual(1, Intent.query.count())

        self.assertEqual(
            ["exeris.core.actions.ControlMovementAction", {"executor": char.id,
                                                           "moving_entity": char.id,
                                                           "travel_action": ["exeris.core.actions.TravelToEntityAction",
                                                                             {"entity": hammer.id,
                                                                              "executor": char.id}],
                                                           "target_action": [
                                                               deferred.get_qualified_class_name(TakeItemAction),
                                                               {"executor": char.id,
                                                                "item": hammer.id, "amount": 1}]
                                                           }],
            Intent.query.one().serialized_action)
        self.assertEqual(main.Intents.WORK, Intent.query.one().type)

        hammer.being_in = rl
        take_action = TakeItemAction(char, hammer, amount=-1)

        # InvalidAmountException cannot be turned into intent
        self.assertRaises(main.InvalidAmountException,
                          lambda: deferred.perform_or_turn_into_intent(char, take_action))

    def test_start_controlling_vehicle_movement_and_change_direction(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)
        vehicle_type = LocationType("cart", 500)
        vehicle_type.properties.append(EntityTypeProperty(P.MOBILE, {"speed": 10}))
        vehicle = Location(rl, vehicle_type)

        steering_room_type = LocationType("steering_room", 400)
        steering_room = Location(vehicle, steering_room_type)
        db.session.add_all([rl, vehicle_type, vehicle, steering_room_type, steering_room])
        db.session.flush()
        steering_room.properties.append(EntityProperty(P.CONTROLLING_MOVEMENT, data={"moving_entity_id": vehicle.id}))
        # create a single-location vehicle

        char = util.create_character("postac", steering_room, util.create_player("ala123"))

        start_controlling_movement_action = StartControllingMovementAction(char)
        start_controlling_movement_action.perform()

        controlling_movement_intent = Intent.query.one()
        self.assertEqual(char, controlling_movement_intent.executor)
        self.assertEqual(vehicle, controlling_movement_intent.target)
        action = controlling_movement_intent.serialized_action
        self.assertEqual("exeris.core.actions.ControlMovementAction", action[0])
        self.assertIsNone(action[1]["travel_action"])

        change_direction_action = ChangeMovementDirectionAction(char, 30)
        change_direction_action.perform()

        controlling_movement_intent = Intent.query.one()
        action = controlling_movement_intent.serialized_action

        self.assertEqual("exeris.core.actions.ControlMovementAction", action[0])
        self.assertEqual(30, action[1]["travel_action"][1]["direction"])

        lazy_char = util.create_character("postac2", steering_room, util.create_player("ala1234"))

        change_direction_action = ChangeMovementDirectionAction(lazy_char, 70)
        self.assertRaises(main.VehicleAlreadyControlledException, change_direction_action.perform)

    def test_start_walking_and_change_direction(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 11)

        db.session.add(rl)

        char = util.create_character("postac", rl, util.create_player("ala123"))
        db.session.flush()

        start_controlling_movmeent_action = StartControllingMovementAction(char)
        start_controlling_movmeent_action.perform()

        control_movement_intent = Intent.query.one()
        control_movement_action = control_movement_intent.serialized_action
        self.assertEqual("exeris.core.actions.ControlMovementAction", control_movement_action[0])
        self.assertIsNone(control_movement_action[1]["travel_action"])

        change_direction_action = ChangeMovementDirectionAction(char, 30)
        change_direction_action.perform()

        control_movement_intent = Intent.query.one()
        control_movement_action = control_movement_intent.serialized_action
        self.assertEqual(30, control_movement_action[1]["travel_action"][1]["direction"])


class PlayerActionsTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_create_character_action(self):
        util.initialize_date()
        rl = RootLocation(Point(2, 3), 112)
        plr = util.create_player("ala123")

        db.session.add(rl)

        create_character1_action = CreateCharacterAction(plr, "postac", Character.SEX_MALE, "en")
        create_character1_action.perform()

        create_character2_action = CreateCharacterAction(plr, "postacka", Character.SEX_FEMALE, "en")
        create_character2_action.perform()

        char1 = Character.query.filter_by(sex=Character.SEX_MALE).one()
        char2 = Character.query.filter_by(sex=Character.SEX_FEMALE).one()
        self.assertCountEqual([char1, char2], plr.alive_characters)


class UtilFunctionsTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_check_space_limitation_simple(self):
        rl = RootLocation(Point(1, 1), 11)
        building_type = LocationType("building", 400)
        building_type.properties.append(EntityTypeProperty(P.LIMITED_SPACE, {"max_weight": 100}))
        building = Location(rl, building_type)

        hammer_type = ItemType("hammer", 100)
        hammer = Item(hammer_type, building)
        db.session.add_all([rl, building_type, building, hammer_type, hammer])

        check_space_limitation(building)  # nothing happens

        hammer2 = Item(hammer_type, building)
        db.session.add(hammer2)

        self.assertRaises(actions.EntitySpaceLimitExceeded, lambda: check_space_limitation(building))

        # works recursively for all the parents between the entity and the location
        self.assertRaises(actions.EntitySpaceLimitExceeded, lambda: check_space_limitation(hammer))

    def test_check_space_limitation_with_increased_space(self):
        rl = RootLocation(Point(1, 1), 11)
        building_type = LocationType("building", 400)
        building_type.properties.append(EntityTypeProperty(P.LIMITED_SPACE, {"max_weight": 100,
                                                                             "can_be_modified": True}))
        building = Location(rl, building_type)

        hammer_type = ItemType("hammer", 200)
        hammer = Item(hammer_type, building)
        db.session.add_all([rl, building_type, building, hammer_type, hammer])

        # not enough space
        self.assertRaises(actions.EntitySpaceLimitExceeded, lambda: check_space_limitation(building))

        magic_portal_type = ItemType("magic_portal", 100)
        # 100 net gain of free space
        magic_portal_type.properties.append(EntityTypeProperty(P.INCREASE_SPACE, {"increase_value": 200}))
        magic_portal = Item(magic_portal_type, building)
        db.session.add_all([magic_portal_type, magic_portal])

        # there is enough space for a hammer
        check_space_limitation(building)

    def test_check_space_limitation_with_increased_space_by_equipment(self):
        rl = RootLocation(Point(1, 1), 11)
        alive_character = EntityType.by_name(Types.ALIVE_CHARACTER)
        alive_character.properties.append(EntityTypeProperty(P.LIMITED_SPACE, {"max_weight": 100,
                                                                               "can_be_modified_by_equipment": True}))
        test_char = util.create_character("dobromir", rl, util.create_player("random1"))

        hammer_type = ItemType("hammer", 200)
        hammer = Item(hammer_type, test_char)
        db.session.add_all([rl, alive_character, hammer_type, hammer])

        # not enough space
        self.assertRaises(actions.EntitySpaceLimitExceeded, lambda: check_space_limitation(test_char))

        backpack_type = ItemType("backpack", 100)
        # 100 net gain of free space
        backpack_type.properties.append(EntityTypeProperty(P.INCREASE_SPACE_WHEN_EQUIPPED, {"increase_value": 200}))
        backpack_type.properties.append(EntityTypeProperty(P.EQUIPPABLE, {"eq_part": "back"}))
        backpack = Item(backpack_type, test_char)
        db.session.add_all([backpack_type, backpack])

        # backpack doesn't work, because it's not equipped
        self.assertRaises(actions.EntitySpaceLimitExceeded, lambda: check_space_limitation(test_char))

        optional_pref_eq_property = properties.OptionalPreferredEquipmentProperty(test_char)
        optional_pref_eq_property.set_preferred_equipment_part(backpack)

        # there is enough space for a hammer
        check_space_limitation(test_char)
