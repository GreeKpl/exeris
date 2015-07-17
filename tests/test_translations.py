from flask.ext.testing import TestCase
from shapely.geometry import Point
from exeris.core.i18n import create_pyslate
from exeris.core.main import db
from exeris.core.models import Item, ItemType, RootLocation, EntityProperty
from exeris.core.properties import P
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
    "entity_shirt": {
        "en": "shirt",
        "pl": ["koszula", "f"],
    },
    "entity_hemp_cloth": {
        "en": "hemp cloth",
        "pl": "tkanina konopna",
    },
    "entity_hemp_cloth_adj": {
        "en": "hemp",
        "pl": "konopn%{tag_v:m?y|f?a|n?e}",
    },
    "entity_berries#b": {
        "pl": "jagodami",
    },
    "entity_cake": {
        "en": "cake",
        "pl": "ciasto",
    },
    "tp_item_info": {
        "en": "%{damage}%{main_material}%{item_name}%{parts}",
    },
    "tp_item_parts": {
        "en": "with ${_parts}",
        "pl": "z ${_parts}",
    },
    "tp_item_main_material": {
        "en": "${entity_%{material_name}_adj#%{item_form}}",
    },
    "tp_parts": {
        "en": "%{last}",
    },
    "tp_parts#y": {
        "en": "%{most} and %{last}",
        "pl": "%{most} i %{last}",
    },
    "tp_item_damaged": {
        "en": "damaged",
        "pl": "uszkodzon%{item_form:m?y|f?a|n?e}",
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
        self.assertEqual("uszkodzony miecz", pyslate.t("item_info", item=sword))

    def test_main_material(self):

        pyslate = create_pyslate("en", data=data)

        rl = RootLocation(Point(1, 1), True, 111)
        shirt_type = ItemType("shirt", 100)
        hemp_cloth_type = ItemType("hemp_cloth", 5, stackable=True)
        shirt = Item(shirt_type, rl)
        shirt.damage = 0.8

        db.session.add_all([rl, shirt_type, shirt, hemp_cloth_type])
        db.session.flush()

        main_material_prop = EntityProperty(shirt, P.VISIBLE_MATERIAL, data={"main": hemp_cloth_type.id})
        db.session.add(main_material_prop)
        db.session.flush()

        self.assertEqual("damaged hemp shirt", pyslate.t("item_info", item=shirt))

        pyslate = create_pyslate("pl", data=data)
        self.assertEqual("uszkodzona konopna koszula", pyslate.t("item_info", item=shirt))

    tearDown = util.tear_down_rollback

