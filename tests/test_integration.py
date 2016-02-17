from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core.actions import SingleActivityProgressProcess
from exeris.core.main import db
from exeris.core.models import Item, RootLocation, ItemType, EntityRecipe, BuildMenuCategory
from exeris.core.recipes import ActivityFactory
from tests import util


class ProductionIntegrationTest(TestCase):
    create_app = util.set_up_app_with_database

    # kind of integration test
    def test_activity_process_for_axe_production(self):
        rt = RootLocation(Point(1, 1), False, 134)

        anvil_type = ItemType("anvil", 300)
        axe_type = ItemType("axe", 100)
        db.session.add_all([anvil_type, axe_type, rt])

        worker = util.create_character("John", rt, util.create_player("ABC"))
        tools_category = BuildMenuCategory("category_tools")

        anvil = Item(anvil_type, rt, weight=100)
        db.session.add(anvil)

        add_name_action = ["exeris.core.actions.AddNameToEntityAction", {
            "entity_name": "mloteczek"}]  # explicitly setting argument that otherwise would require user_input

        # setup recipe
        recipe = EntityRecipe("Producing an axe", {}, {}, 1, tools_category, result_entity=axe_type,
                              result=[add_name_action],
                              activity_container="selected_machine")
        db.session.add(recipe)

        factory = ActivityFactory()
        activity = factory.create_from_recipe(recipe, anvil, worker, user_input={"amount": 1})

        worker.activity = activity
        db.session.flush()

        process = SingleActivityProgressProcess(activity)
        process.perform()

        new_axe = Item.query.filter_by(type=axe_type).one()
        self.assertEqual(worker, new_axe.being_in)
        self.assertEqual("mloteczek", new_axe.title)

    tearDown = util.tear_down_rollback
