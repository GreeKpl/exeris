from exeris.core import main
from flask_testing import TestCase
from shapely.geometry import Point

from exeris.core.actions import ActivityProgressProcess
from exeris.core.main import db
from exeris.core.models import Item, RootLocation, ItemType, EntityRecipe, BuildMenuCategory, Intent, EntityProperty
from exeris.core.properties_base import P
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

        add_name_action = ["exeris.core.actions.AddTitleToEntityAction", {
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

    def test_activity_process_for_coin_production(self):
        rl = RootLocation(Point(1, 1), 134)

        coin_press_type = ItemType("coin_press", 300)
        coin_type = ItemType("coin", 2, stackable=True)
        db.session.add_all([coin_press_type, coin_type, rl])

        worker = util.create_character("John", rl, util.create_player("ABC"))
        tools_category = BuildMenuCategory("category_tools")

        coin_press = Item(coin_press_type, rl, weight=100)
        coin_press.title = "Imperial"
        coin_press.properties.append(EntityProperty(P.SIGNATURE, {"value": "DEFA"}))
        db.session.add(coin_press)

        create_item_with_title_and_signature_action = ["exeris.core.actions.CreateItemWithTitleAndSignatureFromParent",
                                                       {"item_type": coin_type.name, "properties": {},
                                                        "used_materials": "all"}]

        # setup recipe
        recipe = EntityRecipe("Producing coins", {}, {}, 1, tools_category,
                              result=[create_item_with_title_and_signature_action],
                              activity_container=["selected_entity", {"types": ["coin_press"]}])
        db.session.add(recipe)

        factory = ActivityFactory()
        activity = factory.create_from_recipe(recipe, coin_press, worker, user_input={"amount": 3})

        self.assertEqual(coin_press, activity.being_in)

        work_intent = Intent(worker, main.Intents.WORK, 1, activity,
                             ["exeris.core.actions.WorkOnActivityAction",
                              {"executor": worker.id, "activity": activity.id}])
        db.session.add(work_intent)
        db.session.flush()

        process = ActivityProgressProcess(activity, [worker])
        process.perform()

        coin = Item.query.filter_by(type=coin_type).one()
        self.assertEqual(worker, coin.being_in)
        self.assertEqual(3, coin.amount)
        self.assertEqual("Imperial (DEFA)", coin.title)
