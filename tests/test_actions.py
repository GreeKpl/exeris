from unittest.mock import patch
from flask.ext.testing import TestCase
from exeris.core import deferred
from exeris.core.actions import CreateItemAction, RemoveItemAction
from exeris.core.main import db
from exeris.core.general import GameDate
from exeris.core.models import ItemType, Activity, Item
from tests import util

__author__ = 'alek'


class ActionsTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_simple_create_item_action(self):
        item_type = ItemType("hammer")
        db.session.add(item_type)

        hammer_activity = Activity({}, {}, 100, 100)
        db.session.add(hammer_activity)

        action = CreateItemAction(item_type, hammer_activity, {"Edible": True})
        action.perform()

        items = Item.query.all()
        self.assertEqual(1, len(items))
        self.assertEqual(item_type, items[0].type)
        self.assertTrue(items[0].has_property("Edible"))

        with patch("exeris.core.general.GameDate._get_timestamp", new=lambda: 1100):  # stop the time!
            util.initialize_date()
            remove_action = RemoveItemAction(items[0], True)
            remove_action.perform()

            items = Item.query.all()
            self.assertEqual(1, len(items))
            self.assertEqual(None, items[0].being_in)
            self.assertEqual(GameDate.now().game_timestamp, items[0].removal_game_date.game_timestamp)

    def test_deferred_create_item_action(self):
        util.initialize_date()

        item_type = ItemType("hammer")
        db.session.add(item_type)

        hammer_activity = Activity({}, {}, 100, 100)
        db.session.add(hammer_activity)

        db.session.flush()
        d = deferred.dumps((CreateItemAction, (ItemType.by_id, item_type.id), (Activity.by_id, hammer_activity.id), {"Edible": True}))

        # dump it, then read and run the deferred function
        action = deferred.call(d)

        action.perform()

        # the same tests as in simple test
        items = Item.query.all()
        self.assertEqual(1, len(items))
        self.assertEqual(item_type, items[0].type)
        self.assertTrue(items[0].has_property("Edible"))

    tearDown = util.tear_down_rollback