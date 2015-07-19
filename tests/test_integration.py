from flask.ext.testing import TestCase
from shapely.geometry import Point
from exeris.core.main import db
from exeris.core.models import Activity, Item, RootLocation, ItemType, EntityRecipe, BuildMenuCategory
from exeris.core.recipes import ActivityFactory
from exeris.core.scheduler import ActivityProcess
from tests import util

__author__ = 'alek'


class ProductionIntegrationTest(TestCase):

    create_app = util.set_up_app_with_database


    # kind of integration test
    def test_activity_process(self):

        rt = RootLocation(Point(1, 1), False, 134)

        anvil_type = ItemType("anvil", 300)
        axe_type = ItemType("axe", 100)
        db.session.add_all([anvil_type, axe_type, rt])

        worker = util.create_character("John", rt, util.create_player("ABC"))
        tools_category = BuildMenuCategory("category_tools")

        anvil = Item(anvil_type, rt, weight=100)
        db.session.add(anvil)

        db.session.flush()

        # setup recipe

        recipe = EntityRecipe("Producing an axe", {}, {"carrots": 3}, 2, tools_category, result_entity=axe_type)
        db.session.add(recipe)

        factory = ActivityFactory()
        activity = factory.create_from_recipe(recipe, anvil, worker)

        worker.activity = activity

        db.session.add(activity)

        process = ActivityProcess()
        process.run()
        process.run()

        new_axe = Item.query.filter_by(type=axe_type).one()
        self.assertEqual(worker, new_axe.being_in)


    tearDown = util.tear_down_rollback

