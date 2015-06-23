from unittest.mock import patch
from flask.ext.testing import TestCase
from shapely.geometry import Point
from exeris.core import deferred
from exeris.core.actions import CreateItemAction, RemoveItemAction, DropItemAction
from exeris.core.main import db
from exeris.core.general import GameDate
from exeris.core.models import ItemType, Activity, Item, RootLocation, EventType, sqlalchemy
from tests import util
import sqlalchemy as sql
import sqlalchemy.orm as orm

__author__ = 'alek'


class ActionsTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_simple_create_item_action(self):
        item_type = ItemType("hammer", 200)
        db.session.add(item_type)

        schema_type = ItemType("schema", 0)
        db.session.add(schema_type)

        rl = RootLocation(Point(1, 2), False, 123)
        db.session.add(rl)

        container = Item(schema_type, rl, 111)
        db.session.add(container)

        hammer_activity = Activity(container, {"input": "potatoes"}, 100)
        db.session.add(hammer_activity)

        action = CreateItemAction(item_type, hammer_activity, {"Edible": True})
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
        db.session.add(item_type)

        schema_type = ItemType("schema", 0)
        db.session.add(schema_type)

        rl = RootLocation(Point(1, 2), False, 123)
        db.session.add(rl)

        container = Item(schema_type, rl, 111)
        db.session.add(container)

        hammer_activity = Activity(rl, {}, 100)
        db.session.add(hammer_activity)

        db.session.flush()
        d = deferred.dumps(CreateItemAction, item_type.id, hammer_activity.id, {"Edible": True})

        # dump it, then read and run the deferred function
        action = deferred.call(d)

        action.perform()

        # the same tests as in simple test
        items = Item.query.filter_by(type=item_type).all()
        self.assertEqual(1, len(items))
        self.assertEqual(item_type, items[0].type)
        self.assertTrue(items[0].has_property("Edible"))

    def test_drop_action(self):
        util.initialize_date()

        rl = RootLocation(Point(1,1), False, 111)

        plr = util.create_player("aaa")
        char = util.create_character("John", rl, plr)

        hammer_type = ItemType("stone_hammer", 200)
        hammer = Item(hammer_type, char, 200)

        db.session.add_all([rl, hammer_type, hammer])

        action = DropItemAction(char, hammer)

        action.perform()

        self.assertEqual(rl, char.being_in)
        self.assertEqual(rl, hammer.being_in)

        potatoes_type = ItemType("potatoes", 1, stackable=True)
        potatoes = Item(potatoes_type, char, 200)

        db.session.add_all([potatoes_type, potatoes])

        action = DropItemAction(char, potatoes, 50)
        action.perform()

        self.assertEqual(150, potatoes.weight)  # 50 was dropped
        potatoes_on_ground = Item.query.filter(Item.is_in(rl)).filter_by(type=potatoes_type).one()
        self.assertEqual(50, potatoes_on_ground.weight)

        action = DropItemAction(char, potatoes, 150)
        action.perform()

        db.session.flush()  # to correctly check deletion
        self.assertTrue(sql.inspect(potatoes).deleted)  # check whether the object is deleted
        self.assertEqual(200, potatoes_on_ground.weight)

        strawberries_type = ItemType("strawberries", 5, stackable=True)
        grapes_type = ItemType("grapes", 3, stackable=True)
        cake_type = ItemType("cake", 100, stackable=True)

        # check multipart resources
        cake = Item(cake_type, char, 300)
        cake_ground = Item(cake_type, rl, 300)
        other_cake_ground = Item(cake_type, rl, 300)

        db.session.add_all([strawberries_type, grapes_type, cake_type, cake, cake_ground, other_cake_ground])
        db.session.flush()

        cake.visible_parts = [strawberries_type.id, grapes_type.id]
        cake_ground.visible_parts = [strawberries_type.id, grapes_type.id]

        other_cake_ground.visible_parts = [strawberries_type.id, potatoes_type.id]

        db.session.flush()

        action = DropItemAction(char, cake, 1)
        action.perform()

        self.assertEqual(200, cake.weight)
        self.assertEqual(400, cake_ground.weight)
        self.assertEqual(300, other_cake_ground.weight)

        db.session.delete(cake_ground)  # remove it!

        action = DropItemAction(char, cake, 1)
        action.perform()

        self.assertEqual(100, cake.weight)
        self.assertEqual(300, other_cake_ground.weight)

        new_ground_cake = Item.query.filter(Item.is_in(rl)).filter_by(type=cake_type).\
            filter_by(visible_parts=[strawberries_type.id, grapes_type.id]).one()
        self.assertEqual(100, new_ground_cake.weight)
        self.assertEqual([strawberries_type.id, grapes_type.id], new_ground_cake.visible_parts)

    def test_drop_action_failure(self):
        util.initialize_date()

        rl = RootLocation(Point(1,1), False, 111)
        plr = util.create_player("aaa")
        char = util.create_character("John", rl, plr)

        hammer_type = ItemType("stone_hammer", 200)

        # hammer is already on the ground
        hammer = Item(hammer_type, rl, 200)

        db.session.add_all([rl, hammer_type, hammer])

        action = DropItemAction(char, hammer)
        self.assertRaises(Exception, action.perform)  # TODO

        # there are too little potatoes
        potatoes_type = ItemType("potatoes", 20, stackable=True)

        potatoes = Item(potatoes_type, char, 200)

        db.session.add_all([potatoes_type, potatoes])
        db.session.flush()

        action = DropItemAction(char, potatoes, 201)
        self.assertRaises(Exception, action.perform)  # TODO



    tearDown = util.tear_down_rollback