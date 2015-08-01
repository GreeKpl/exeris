from unittest.mock import patch

from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core import deferred
from exeris.core.actions import CreateItemAction, RemoveItemAction, DropItemAction, AddItemToActivityAction, \
    SayAloudAction
from exeris.core.main import db, Events
from exeris.core.general import GameDate
from exeris.core.models import ItemType, Activity, Item, RootLocation, EntityProperty, TypeGroup, Event, Location, \
    LocationType, Passage
from exeris.core.properties import P
from tests import util


__author__ = 'alek'


class ActionsTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_simple_create_item_action(self):
        item_type = ItemType("hammer", 200)
        schema_type = ItemType("schema", 0)
        rl = RootLocation(Point(1, 2), False, 123)
        db.session.add_all([item_type, schema_type, rl])

        container = Item(schema_type, rl, weight=111)
        db.session.add(container)

        initiator = util.create_character("ABC", rl, util.create_player("janko"))

        hammer_activity = Activity(container, "dummy_activity_name", {}, {"input": "potatoes"}, 100, initiator)
        db.session.add(hammer_activity)

        action = CreateItemAction(item_type=item_type, properties={"Edible": True},
                                  activity=hammer_activity, initiator=initiator, used_materials="all")
        action.perform()

        items = Item.query.filter_by(type=item_type).all()
        self.assertEqual(1, len(items))
        self.assertEqual(item_type, items[0].type)
        self.assertTrue(items[0].has_property("Edible"))

        with patch("exeris.core.general.GameDate._get_timestamp", new=lambda: 1100):  # stop the time!
            util.initialize_date()
            remove_action = RemoveItemAction(items[0], True)
            remove_action.perform()

            items = Item.query.filter_by(type=item_type).all()
            self.assertEqual(1, len(items))
            self.assertEqual(None, items[0].being_in)
            self.assertEqual(GameDate.now().game_timestamp, items[0].removal_game_date.game_timestamp)

    def test_deferred_create_item_action(self):
        util.initialize_date()

        item_type = ItemType("hammer", 200)
        schema_type = ItemType("schema", 0)
        rl = RootLocation(Point(1, 2), False, 123)
        db.session.add_all([item_type, schema_type, rl])

        container = Item(schema_type, rl, weight=111)
        db.session.add(container)

        initiator = util.create_character("ABC", rl, util.create_player("janko"))

        hammer_activity = Activity(rl, "dummy_activity_name", {}, {}, 100, initiator)
        db.session.add(hammer_activity)

        db.session.flush()
        d = ["exeris.core.actions.CreateItemAction", {"item_type": item_type.name, "properties": {"Edible": True},
                                                      "used_materials": "all"}]

        # dump it, then read and run the deferred function
        action = deferred.call(d, activity=hammer_activity, initiator=initiator)

        action.perform()

        # the same tests as in simple test
        items = Item.query.filter_by(type=item_type).all()
        self.assertEqual(1, len(items))
        self.assertEqual(item_type, items[0].type)
        self.assertTrue(items[0].has_property("Edible"))

    def test_complicated_create_item_action(self):
        """
        Create a lock and a key in an activity made of iron (for lock) and hard metal group (for key - we use steel)
        For key 'steel' should be "main" in visible_material property
        :return:
        """
        util.initialize_date()

        iron_type = ItemType("iron", 4, stackable=True)
        hard_metal_group = TypeGroup("group_hard_metal")
        steel_type = ItemType("steel", 5, stackable=True)

        hard_metal_group.add_to_group(steel_type, efficiency=0.5)

        lock_type = ItemType("iron_lock", 200, portable=False)
        key_type = ItemType("key", 10)

        rl = RootLocation(Point(1, 1), False, 213)

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
                                  "used_materials": {hard_metal_group.name: 1}, "visible_material": {"main": hard_metal_group.name}}
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








    def test_drop_item_action(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), False, 111)

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
        Event.query.delete()

        potatoes_type = ItemType("potatoes", 1, stackable=True)
        potatoes = Item(potatoes_type, doer, weight=200)

        db.session.add_all([potatoes_type, potatoes])

        amount = 50
        action = DropItemAction(doer, potatoes, amount)
        action.perform()

        # test events
        event_drop_doer = Event.query.filter_by(type_name=Events.DROP_ITEM + "_doer").one()
        self.assertEqual(potatoes.pyslatize(item_amount=amount), event_drop_doer.params)
        event_drop_obs = Event.query.filter_by(type_name=Events.DROP_ITEM + "_observer").one()
        self.assertEqual(dict(potatoes.pyslatize(item_amount=amount), groups={"doer": doer.pyslatize()}), event_drop_obs.params)
        Event.query.delete()

        self.assertEqual(150, potatoes.weight)  # 50 was dropped
        potatoes_on_ground = Item.query.filter(Item.is_in(rl)).filter_by(type=potatoes_type).one()
        self.assertEqual(50, potatoes_on_ground.weight)

        action = DropItemAction(doer, potatoes, 150)
        action.perform()

        db.session.flush()  # to correctly check deletion
        self.assertIsNone(potatoes.being_in)  # check whether the object is deleted
        self.assertIsNone(potatoes.used_for)
        self.assertIsNotNone(potatoes.removal_game_date)

        self.assertEqual(200, potatoes_on_ground.weight)

        strawberries_type = ItemType("strawberries", 5, stackable=True)
        grapes_type = ItemType("grapes", 3, stackable=True)
        cake_type = ItemType("cake", 100, stackable=True)

        # check multipart resources
        cake = Item(cake_type, doer, weight=300)
        cake_ground = Item(cake_type, rl, weight=300)
        other_cake_ground = Item(cake_type, rl, weight=300)

        db.session.add_all([strawberries_type, grapes_type, cake_type, cake, cake_ground, other_cake_ground])
        db.session.flush()

        cake.visible_parts = [grapes_type.name, strawberries_type.name]
        cake_ground.visible_parts = [grapes_type.name, strawberries_type.name]

        other_cake_ground.visible_parts = [strawberries_type.name, potatoes_type.name]

        db.session.flush()

        action = DropItemAction(doer, cake, 1)
        action.perform()

        self.assertEqual(200, cake.weight)
        self.assertEqual(400, cake_ground.weight)
        self.assertEqual(300, other_cake_ground.weight)

        db.session.delete(cake_ground)  # remove it!

        action = DropItemAction(doer, cake, 1)
        action.perform()

        self.assertEqual(100, cake.weight)
        self.assertEqual(300, other_cake_ground.weight)

        new_ground_cake = Item.query.filter(Item.is_in(rl)).filter_by(type=cake_type).\
            filter_by(visible_parts=[grapes_type.name, strawberries_type.name]).one()
        self.assertEqual(100, new_ground_cake.weight)
        self.assertEqual([grapes_type.name, strawberries_type.name], new_ground_cake.visible_parts)

    def test_drop_action_failure(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), False, 111)
        char = util.create_character("John", rl, util.create_player("aaa"))

        hammer_type = ItemType("stone_hammer", 200)

        # hammer is already on the ground
        hammer = Item(hammer_type, rl, weight=200)

        db.session.add_all([rl, hammer_type, hammer])

        action = DropItemAction(char, hammer)
        self.assertRaises(Exception, action.perform)  # TODO

        # there are too little potatoes
        potatoes_type = ItemType("potatoes", 20, stackable=True)

        potatoes = Item(potatoes_type, char, amount=10)

        db.session.add_all([potatoes_type, potatoes])
        db.session.flush()

        action = DropItemAction(char, potatoes, 201)
        self.assertRaises(Exception, action.perform)  # TODO

    def test_add_item_to_activity_action(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), False, 111)
        initiator = util.create_character("John", rl, util.create_player("aaa"))
        observer = util.create_character("obs", rl, util.create_player("abc"))

        anvil_type = ItemType("anvil", 400, portable=False)
        anvil = Item(anvil_type, rl)
        metal_group = TypeGroup("group_metal")
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

        action = AddItemToActivityAction(initiator, iron, activity, 4)
        action.perform()

        self.assertEqual({metal_group.name: {"needed": 10, "left": 8, "used_type": iron_type.name}}, activity.requirements["input"])
        self.assertEqual(16, iron.amount)

        action = AddItemToActivityAction(initiator, iron, activity, 16)
        action.perform()

        self.assertEqual({metal_group.name: {"needed": 10, "left": 0, "used_type": iron_type.name}}, activity.requirements["input"])
        self.assertIsNone(iron.parent_entity)
        self.assertIsNotNone(iron.removal_game_date)
        Event.query.delete()

        # TEST TYPE MATCHING MULTIPLE REQUIREMENT GROUPS

        wood_group = TypeGroup("group_wood")
        fuel_group = TypeGroup("group_fuel")
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

        action = AddItemToActivityAction(initiator, oak, activity, 20)  # added as the first material from the list
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

        action = AddItemToActivityAction(initiator, oak, activity, 10)
        action.perform()  # add materials to another group

        self.assertEqual({
            metal_group.name: {"needed": 10, "left": 10},
            fuel_group.name: {"needed": 10, "left": 0, "used_type": oak_type.name},
            wood_group.name: {"needed": 10, "left": 0, "used_type": oak_type.name},
        }, activity.requirements["input"])
        self.assertIsNotNone(oak.removal_game_date)

    def test_say_aloud_action(self):
        util.initialize_date()

        rl1 = RootLocation(Point(0, 0), False, 123)
        rl2 = RootLocation(Point(0, 11), False, 123)
        rl3 = RootLocation(Point(0, 21), False, 123)
        building_type = LocationType("building", 200)
        building = Location(rl1, building_type)
        plr = util.create_player("eee")
        doer = util.create_character("doer", building, plr)
        obs_same_loc = util.create_character("obs_same_loc", building, plr)
        obs_near_loc = util.create_character("obs_near_loc", rl2, plr)
        obs_far_loc = util.create_character("obs_far_loc", rl3, plr)
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

        door_to_building = Passage.query.filter(Passage.between(rl1, building)).one()

        db.session.add(EntityProperty(door_to_building, P.WINDOW, {"open": True}))

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

    tearDown = util.tear_down_rollback

