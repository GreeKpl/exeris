from exeris.core import main
from flask_testing import TestCase
from shapely.geometry import Point

from exeris.core.actions import ActivityProgressProcess
from exeris.core.main import db
from exeris.core.models import Item, RootLocation, ItemType, EntityRecipe, BuildMenuCategory, Intent
from exeris.core.recipes import ActivityFactory
from tests import util


class ProductionIntegrationTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    # kind of integration test
    def test_activity_process_for_axe_production(self):
        rt = RootLocation(Point(1, 1), 134)

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
                              activity_container=["selected_entity", {"types": ["anvil"]}])
        db.session.add(recipe)

        factory = ActivityFactory()
        activity = factory.create_from_recipe(recipe, anvil, worker, user_input={"amount": 1})

        self.assertEqual(anvil, activity.being_in)

        work_intent = Intent(worker, main.Intents.WORK, 1, activity,
                             ["exeris.core.actions.WorkOnActivityAction",
                              {"executor": worker.id, "activity": activity.id}])
        db.session.add(work_intent)
        db.session.flush()

        process = ActivityProgressProcess(activity, [worker])
        process.perform()

        new_axe = Item.query.filter_by(type=axe_type).one()
        self.assertEqual(worker, new_axe.being_in)
        self.assertEqual("mloteczek", new_axe.title)
