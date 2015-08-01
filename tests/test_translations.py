from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core.i18n import create_pyslate
from exeris.core.main import db
from exeris.core.models import Item, ItemType, RootLocation, EntityProperty, Character, ObservedName
from exeris.core.properties import P
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
    "entity_book": {
        "en": "book",
        "pl": "książka",
    },
    "entity_carrot": {
        "en": "carrot",
        "pl": "marchewka",
    },
    "entity_carrot#b": {
        "pl": "marchewką",
    },
    "entity_carrot#u": {
        "en": "carrots",
        "pl": "marchewki",
    },
    "entity_carrot#ub": {
        "pl": "marchewkami",
    },
    "entity_apple": {
        "en": "apple",
        "pl": "jabłko",
    },
    "entity_apple#u": {
        "en": "apples",
        "pl": "jabłkami",
    },
    "entity_apple#ub": {
        "pl": "jabłkami",
    },
    "entity_berries": {
        "en": "handful of berries",
        "pl": "garść jagód",
    },
    "entity_berries#p": {
        "en": "handfuls of berries",
        "pl": "garści jagód",
    },
    "entity_berries#u": {
        "en": "berries",
        "pl": "jagody",
    },
    "entity_berries#ub": {
        "pl": "jagodami",
    },
    "entity_shirt": {
        "en": "shirt",
        "pl": ["koszula", "f"],
    },
    "entity_hemp_cloth": {
        "en": "bale of hemp cloth",
        "pl": "bela tkaniny konopnej",
    },
    "entity_hemp_cloth#w": {
        "pl": "bele tkaniny konopnej",
    },
    "entity_hemp_cloth#p": {
        "en": "bales of hemp cloth",
        "pl": "bel tkaniny konopnej",
    },
    "entity_hemp_cloth#u": {
        "en": "hemp cloth",
        "pl": "tkanina konopna",
    },
    "entity_hemp_cloth#ub": {
        "pl": "tkaniną konopną",
    },
    "entity_hemp_cloth_adj": {
        "en": "hemp",
        "pl": "konopn%{tag_v:m?y|f?a|n?e}",
    },
    "entity_cake": {
        "en": "cake",
        "pl": "ciasto",
    },
    "entity_cake#p": {
        "en": "cakes",
        "pl": "ciasta",
    },
    "entity_cake#u": {
        "pl": "ciasto",
    },
    "entity_cake#ub": {
        "pl": "ciastami",
    },
    "tp_item_info": {
        "en": "%{amount}%{damage}%{main_material}%{item_name}%{title}%{states}%{parts}",
    },
    "tp_item_parts": {
        "en": "with ${_parts}",
        "pl": "z ${_parts}",
    },
    "tp_item_main_material": {
        "en": "${entity_%{material_name}_adj#%{item_form}}",
    },
    "tp_item_title": {
        "en": "'%{title}'",
        "pl": "„%{title}”",
    },
    "tp_location_title": {
        "en": "'%{title}'",
        "pl": "„%{title}”",
    },
    "tp_parts": {
        "en": "%{last}",
    },
    "tp_parts#p": {
        "en": "%{most} and %{last}",
        "pl": "%{most} i %{last}",
    },
    "tp_item_damaged": {
        "en": "damaged",
        "pl": "uszkodzon%{item_form:m?y|f?a|n?e}",
    },
    "entity_character": {
        "en": "human",
        "pl": "człowiek",
    },
    "entity_character#m": {
        "en": "man",
        "pl": "mężczyzna",
    },
    "entity_character#f": {
        "en": "woman",
        "pl": "kobieta",
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
        self.assertEqual("sword", pyslate.t("item_info", **sword.pyslatize()))
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
        self.assertEqual("cake with apples, berries and carrots", pyslate.t("item_info", **cake.pyslatize()))

        # test visible parts in Polish
        pyslate = create_pyslate("pl", data=data)
        self.assertEqual("ciasto z jabłkami, jagodami i marchewkami", pyslate.t("item_info", **cake.pyslatize()))

    def test_damaged_item(self):

        pyslate = create_pyslate("en", data=data)

        rl = RootLocation(Point(1,1), True, 111)
        sword_type = ItemType("sword", 100)
        sword = Item(sword_type, rl)
        sword.damage = 0.8

        db.session.add_all([rl, sword_type, sword])
        db.session.flush()

        self.assertEqual("damaged sword", pyslate.t("item_info", **sword.pyslatize()))

        pyslate = create_pyslate("pl", data=data)
        self.assertEqual("uszkodzony miecz", pyslate.t("item_info", **sword.pyslatize()))

    def test_title(self):
        rl = RootLocation(Point(1,1), True, 111)
        book_type = ItemType("book", 100)
        book = Item(book_type, rl)
        book.title = "How to make a good translation system"
        db.session.add_all([rl, book_type, book])
        db.session.flush()

        pyslate_en = create_pyslate("en", data=data)
        self.assertEquals("book 'How to make a good translation system'", pyslate_en.t("item_info", **book.pyslatize()))

        pyslate_pl = create_pyslate("pl", data=data)
        self.assertEquals("książka „How to make a good translation system”", pyslate_pl.t("item_info", **book.pyslatize()))

    def test_character_name(self):
        util.initialize_date()

        rl = RootLocation(Point(1,1), True, 111)

        plr = util.create_player("adwdas")
        man = util.create_character("A MAN", rl, plr, sex=Character.SEX_MALE)
        woman = util.create_character("A WOMAN", rl, plr, sex=Character.SEX_FEMALE)
        obs1 = util.create_character("obs1", rl, plr)  # obs1 doesn't know anybody
        obs2 = util.create_character("obs2", rl, plr)  # obs2 knows both man and woman

        # not testing property DynamicNamable, just translation system
        man_obs2_name = ObservedName(obs2, man, "John")
        woman_obs2_name = ObservedName(obs2, woman, "Judith")

        db.session.add_all([man_obs2_name, woman_obs2_name, rl])
        db.session.flush()

        pyslate_en = create_pyslate("en", data=data, context={"observer": obs1})
        self.assertEquals("woman", pyslate_en.t("character_info", **woman.pyslatize()))
        self.assertEquals("man", pyslate_en.t("character_info", **man.pyslatize()))

        pyslate_pl = create_pyslate("pl", data=data, context={"observer": obs1})
        self.assertEquals("kobieta", pyslate_pl.t("character_info", **woman.pyslatize()))
        self.assertEquals("mężczyzna", pyslate_pl.t("character_info", **man.pyslatize()))

        pyslate_en = create_pyslate("en", data=data, context={"observer": obs2})
        self.assertEquals("Judith", pyslate_en.t("character_info", **woman.pyslatize()))
        self.assertEquals("John", pyslate_en.t("character_info", **man.pyslatize()))

    def test_main_material(self):

        pyslate = create_pyslate("en", data=data)

        rl = RootLocation(Point(1, 1), True, 111)
        shirt_type = ItemType("shirt", 100)
        hemp_cloth_type = ItemType("hemp_cloth", 5, stackable=True)
        shirt = Item(shirt_type, rl)
        shirt.damage = 0.8

        db.session.add_all([rl, shirt_type, shirt, hemp_cloth_type])
        db.session.flush()

        main_material_prop = EntityProperty(shirt, P.VISIBLE_MATERIAL, data={"main": hemp_cloth_type.name})
        db.session.add(main_material_prop)
        db.session.flush()

        self.assertEqual("damaged hemp shirt", pyslate.t("item_info", **shirt.pyslatize()))

        pyslate = create_pyslate("pl", data=data)
        self.assertEqual("uszkodzona konopna koszula", pyslate.t("item_info", **shirt.pyslatize()))

    def test_stackable(self):
        pyslate_en = create_pyslate("en", data=data)
        pyslate_pl = create_pyslate("pl", data=data)

        rl = RootLocation(Point(1, 1), True, 111)
        hemp_cloth_type = ItemType("hemp_cloth", 5, stackable=True)
        hemp_cloth = Item(hemp_cloth_type, rl, amount=1)

        db.session.add_all([rl, hemp_cloth_type, hemp_cloth])
        db.session.flush()

        self.assertEqual("1 bale of hemp cloth", pyslate_en.t("item_info", **hemp_cloth.pyslatize()))
        self.assertEqual("1 bela tkaniny konopnej", pyslate_pl.t("item_info", **hemp_cloth.pyslatize()))

        hemp_cloth.amount = 3
        self.assertEqual("3 bales of hemp cloth", pyslate_en.t("item_info", **hemp_cloth.pyslatize()))
        self.assertEqual("3 bele tkaniny konopnej", pyslate_pl.t("item_info", **hemp_cloth.pyslatize()))

        hemp_cloth.amount = 6
        self.assertEqual("6 bales of hemp cloth", pyslate_en.t("item_info", **hemp_cloth.pyslatize()))
        self.assertEqual("6 bel tkaniny konopnej", pyslate_pl.t("item_info", **hemp_cloth.pyslatize()))

        # check if entity_info gives the same
        self.assertEqual("6 bales of hemp cloth", pyslate_en.t("entity_info", **hemp_cloth.pyslatize()))
        self.assertEqual("6 bel tkaniny konopnej", pyslate_pl.t("entity_info", **hemp_cloth.pyslatize()))




    tearDown = util.tear_down_rollback

