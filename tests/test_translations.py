from flask.ext.testing import TestCase
from shapely.geometry import Point
from exeris.core.i18n import create_pyslate
from exeris.core.main import db
from exeris.core.models import Item, ItemType, RootLocation
from pyslate.pyslate import Pyslate
from tests import util

__author__ = 'alek'

data = {
    "entity_sword": {
        "en": "sword",
        "pl": ["miecz", "m"],
    },
    "entity_axe": {
        "en": "axe",
    },
    "entity_carrot": {
        "en": "carrot",
        "pl": "marchewka",
    },
    "entity_carrot#b": {
        "pl": "marchewką",
    },
    "entity_apple": {
        "en": "apple",
        "pl": "jabłko",
    },
    "entity_apple#b": {
        "pl": "jabłkiem",
    },
    "entity_berries": {
        "en": "berries",
        "pl": "jagody",
    },
    "entity_berries#b": {
        "pl": "jagodami",
    },
    "entity_cake": {
        "en": "cake",
        "pl": "ciasto",
    },
    "tp_item_with_parts": {
        "en": "%{item_name} with ${_parts}",
        "pl": "%{item_name} z ${_parts}",
    },
    "tp_parts": {
        "en": "%{last}",
    },
    "tp_parts#y": {
        "en": "%{most} and %{last}",
        "pl": "%{most} i %{last}",
    },
    "tp_item_damaged": {
        "en": "damaged %{item_name}",
        "pl": "zniszczon%{item_form:m?y|f?a|n?e} %{item_name}",
    },
    "any": {
        "en": "%{contents}",
    },
}


class TranslationTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_simple_translation(self):
        pyslate = create_pyslate("en", data=data)

        self.assertEqual("a sword", pyslate.t("entity_sword@article"))

    def test_item_translation(self):

        pyslate = create_pyslate("en", data=data)

        rl = RootLocation(Point(1,1), True, 111)
        sword_type = ItemType("sword", 100)
        sword = Item(sword_type, rl)

        db.session.add_all([rl, sword_type, sword])
        db.session.flush()
        self.assertEqual("axe", pyslate.t("item_info", item_name="axe"))

        # accessible both by specifying item or its id
        self.assertEqual("sword", pyslate.t("item_info", item=sword))
        self.assertEqual("sword", pyslate.t("item_info", item_id=sword.id))

    def test_item_visible_parts_en_pl(self):

        pyslate = create_pyslate("en", data=data)

        rl = RootLocation(Point(1,1), True, 111)
        carrot_type = ItemType("carrot", 100, stackable=False)
        apple_type = ItemType("apple", 100, stackable=False)
        berries_type = ItemType("berries", 3, stackable=False)
        cake_type = ItemType("cake", 100, stackable=False)  # intentionally set to false to test only parts
        cake = Item(cake_type, rl)

        db.session.add_all([rl, carrot_type, apple_type, cake_type, berries_type, cake])
        db.session.flush()

        cake.visible_parts = [carrot_type, apple_type, berries_type]

        # test visible parts
        self.assertEqual("cake with carrot, apple and berries", pyslate.t("item_info", item=cake))

        # test visible parts in Polish
        pyslate = create_pyslate("pl", data=data)
        self.assertEqual("ciasto z marchewką, jabłkiem i jagodami", pyslate.t("item_info", item=cake))

    def test_damaged_item(self):

        pyslate = create_pyslate("en", data=data)

        rl = RootLocation(Point(1,1), True, 111)
        sword_type = ItemType("sword", 100)
        sword = Item(sword_type, rl)
        sword.damage = 0.8

        db.session.add_all([rl, sword_type, sword])
        db.session.flush()

        self.assertEqual("damaged sword", pyslate.t("item_info", item=sword))

        pyslate = create_pyslate("pl", data=data)
        self.assertEqual("zniszczony miecz", pyslate.t("item_info", item=sword))

    tearDown = util.tear_down_rollback

