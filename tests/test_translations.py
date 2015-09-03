from flask.ext.testing import TestCase
from shapely import geometry
from shapely.geometry import Point

from exeris.core.i18n import create_pyslate
from exeris.core.main import db
from exeris.core.models import Item, ItemType, RootLocation, EntityProperty, Character, ObservedName, Location, \
    LocationType, TerrainArea, TerrainType, Passage, Activity
from exeris.core.properties import P
from pyslate.backends import json_backend
from tests import util

__author__ = 'alek'

data = {
    "entity_sword": {
        "en": "sword",
        "pl": ["miecz%{tag_v:x?|g?a}", "m"],
    },
    "entity_axe": {
        "en": "axe",
    },
    "entity_book": {
        "en": "book",
        "pl": "książka",
    },
    "entity_building": {
        "en": "building",
    },
    "entity_carrot": {
        "en": "carrot",
        "pl": "marchewka",
    },
    "entity_carrot#p": {
        "en": "carrots",
        "pl": "marchewek",
    },
    "entity_carrot#w": {
        "pl": "marchewki",
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
    "entity_door": {
        "en": "door",
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
    "tp_detailed_item_info": {
        "en": "%{amount}%{damage}%{main_material}%{item_name}%{title}%{states}%{parts}",
    },
    "tp_item_info": {
        "en": "%{main_material}%{item_name}%{parts}",
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
    "entity_outside": {
        "en": "outside",
        "pl": "na zewnątrz",
    },
    "terrain_sea": {
        "en": "sea",
        "pl": "morze",
    },
    "terrain_grassland": {
        "en": "grassland",
        "pl": "łąka",
    },
    "activity_manufacturing": {
        "en": "manufacturing ${result:entity_info@article}",
        "pl": "produkcja ${result:entity_info#g}",
    },
}


class ItemTranslationTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_simple_translation(self):
        backend = json_backend.JsonBackend(json_data=data)
        pyslate = create_pyslate("en", backend=backend)

        self.assertEqual("a sword", pyslate.t("entity_sword@article"))

    def test_item_translation(self):
        backend = json_backend.JsonBackend(json_data=data)
        pyslate = create_pyslate("en", backend=backend)

        rl = RootLocation(Point(1,1), True, 111)
        sword_type = ItemType("sword", 100)
        sword = Item(sword_type, rl)

        db.session.add_all([rl, sword_type, sword])
        db.session.flush()
        self.assertEqual("axe", pyslate.t("item_info", item_name="axe"))

        self.assertEqual("sword", pyslate.t("item_info", **sword.pyslatize(detailed=True)))

    def test_item_visible_parts_en_pl(self):
        backend = json_backend.JsonBackend(json_data=data)
        pyslate = create_pyslate("en", backend=backend)

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
        pyslate = create_pyslate("pl", backend=backend)
        self.assertEqual("ciasto z jabłkami, jagodami i marchewkami", pyslate.t("item_info", **cake.pyslatize()))

    def test_damaged_item(self):
        backend = json_backend.JsonBackend(json_data=data)
        pyslate = create_pyslate("en", backend=backend)

        rl = RootLocation(Point(1,1), True, 111)
        sword_type = ItemType("sword", 100)
        sword = Item(sword_type, rl)
        sword.damage = 0.8

        db.session.add_all([rl, sword_type, sword])
        db.session.flush()

        self.assertEqual("damaged sword", pyslate.t("item_info", **sword.pyslatize(detailed=True)))

        pyslate = create_pyslate("pl", backend=backend)
        self.assertEqual("uszkodzony miecz", pyslate.t("item_info", **sword.pyslatize(detailed=True)))

    def test_title(self):
        rl = RootLocation(Point(1,1), True, 111)
        book_type = ItemType("book", 100)
        book = Item(book_type, rl)
        book.title = "How to make a good translation system"
        db.session.add_all([rl, book_type, book])
        db.session.flush()

        backend = json_backend.JsonBackend(json_data=data)

        pyslate_en = create_pyslate("en", backend=backend)
        self.assertEqual("book 'How to make a good translation system'", pyslate_en.t("item_info", **book.pyslatize(detailed=True)))

        pyslate_pl = create_pyslate("pl", backend=backend)
        self.assertEqual("książka „How to make a good translation system”", pyslate_pl.t("item_info", **book.pyslatize(detailed=True)))

    def test_main_material(self):
        backend = json_backend.JsonBackend(json_data=data)
        pyslate = create_pyslate("en", backend=backend)

        rl = RootLocation(Point(1, 1), True, 111)
        shirt_type = ItemType("shirt", 100)
        hemp_cloth_type = ItemType("hemp_cloth", 5, stackable=True)
        shirt = Item(shirt_type, rl)
        shirt.damage = 0.8

        db.session.add_all([rl, shirt_type, shirt, hemp_cloth_type])
        db.session.flush()

        shirt.properties.append(EntityProperty(P.VISIBLE_MATERIAL, {"main": hemp_cloth_type.name}))

        db.session.flush()

        self.assertEqual("damaged hemp shirt", pyslate.t("item_info", **shirt.pyslatize(detailed=True)))

        pyslate = create_pyslate("pl", backend=backend)
        self.assertEqual("uszkodzona konopna koszula", pyslate.t("item_info", **shirt.pyslatize(detailed=True)))

    def test_stackable(self):
        backend = json_backend.JsonBackend(json_data=data)
        pyslate_en = create_pyslate("en", backend=backend)
        pyslate_pl = create_pyslate("pl", backend=backend)

        rl = RootLocation(Point(1, 1), True, 111)
        hemp_cloth_type = ItemType("hemp_cloth", 5, stackable=True)
        hemp_cloth = Item(hemp_cloth_type, rl, amount=1)

        db.session.add_all([rl, hemp_cloth_type, hemp_cloth])
        db.session.flush()

        self.assertEqual("1 bale of hemp cloth", pyslate_en.t("item_info", **hemp_cloth.pyslatize(detailed=True)))
        self.assertEqual("1 bela tkaniny konopnej", pyslate_pl.t("item_info", **hemp_cloth.pyslatize(detailed=True)))

        hemp_cloth.amount = 3
        self.assertEqual("3 bales of hemp cloth", pyslate_en.t("item_info", **hemp_cloth.pyslatize(detailed=True)))
        self.assertEqual("3 bele tkaniny konopnej", pyslate_pl.t("item_info", **hemp_cloth.pyslatize(detailed=True)))

        hemp_cloth.amount = 6
        self.assertEqual("6 bales of hemp cloth", pyslate_en.t("item_info", **hemp_cloth.pyslatize(detailed=True)))
        self.assertEqual("6 bel tkaniny konopnej", pyslate_pl.t("item_info", **hemp_cloth.pyslatize(detailed=True)))

        # check if entity_info gives the same
        self.assertEqual("6 bales of hemp cloth", pyslate_en.t("entity_info", **hemp_cloth.pyslatize(detailed=True)))
        self.assertEqual("6 bel tkaniny konopnej", pyslate_pl.t("entity_info", **hemp_cloth.pyslatize(detailed=True)))

        # check non-detailed text
        self.assertEqual("hemp cloth", pyslate_en.t("entity_info", **hemp_cloth.pyslatize()))
        self.assertEqual("tkanina konopna", pyslate_pl.t("entity_info", **hemp_cloth.pyslatize()))

        carrot_type = ItemType("carrot", 30, stackable=True)
        carrots = Item(carrot_type, rl, amount=11)
        db.session.add_all([carrot_type, carrots])
        db.session.flush()

        self.assertEqual("carrots", pyslate_en.t("entity_info", **carrots.pyslatize()))
        self.assertEqual("marchewki", pyslate_pl.t("entity_info", **carrots.pyslatize()))

        self.assertEqual("11 carrots", pyslate_en.t("entity_info", **carrots.pyslatize(detailed=True)))
        self.assertEqual("11 marchewek", pyslate_pl.t("entity_info", **carrots.pyslatize(detailed=True)))

        # embedded in HTML tag
        translated_html_text = pyslate_pl.t("entity_info", **carrots.pyslatize(detailed=True, html=True))
        self.assertEqual("""<span class="entity item id_{}">11 marchewek</span>""".format(carrots.id), translated_html_text)

    tearDown = util.tear_down_rollback


class CharacterAndLocationTranslationTest(TestCase):

    create_app = util.set_up_app_with_database

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

        backend = json_backend.JsonBackend(json_data=data)

        pyslate_en = create_pyslate("en", backend=backend, context={"observer": obs1})
        self.assertEqual("woman", pyslate_en.t("character_info", **woman.pyslatize()))
        self.assertEqual("man", pyslate_en.t("character_info", **man.pyslatize()))

        pyslate_pl = create_pyslate("pl", backend=backend, context={"observer": obs1})
        self.assertEqual("kobieta", pyslate_pl.t("character_info", **woman.pyslatize()))
        self.assertEqual("mężczyzna", pyslate_pl.t("character_info", **man.pyslatize()))

        pyslate_en = create_pyslate("en", backend=backend, context={"observer": obs2})
        self.assertEqual("Judith", pyslate_en.t("character_info", **woman.pyslatize()))
        self.assertEqual("John", pyslate_en.t("character_info", **man.pyslatize()))

        translated_html_text = pyslate_en.t("character_info", **man.pyslatize(html=True))
        self.assertEqual("""<span class="entity character id_{}">John</span>""".format(man.id), translated_html_text)

    def test_location_name(self):

        rl = RootLocation(Point(1, 1), True, 213)
        plr = util.create_player("dawdasdawdasw")
        obs = util.create_character("obs1", rl, plr)

        building_type = LocationType("building", 200)
        loc = Location(rl, building_type)

        db.session.add_all([rl, building_type, loc])
        backend = json_backend.JsonBackend(json_data=data)

        pyslate_en = create_pyslate("en", backend=backend, context={"observer": obs})
        self.assertEqual("building", pyslate_en.t("location_info", **loc.pyslatize()))

        loc.title = "Workshop"
        self.assertEqual("'Workshop'", pyslate_en.t("location_info", **loc.pyslatize()))

        # test embedding in HTML tag
        translated_html_text = pyslate_en.t("location_info", **loc.pyslatize(html=True))
        self.assertEqual("""<span class="entity location id_{}">'Workshop'</span>""".format(loc.id), translated_html_text)

    def test_root_location_name(self):

        rl = RootLocation(Point(1, 1), True, 213)
        plr = util.create_player("dawdasdawdasw")
        obs = util.create_character("obs1", rl, plr)

        backend = json_backend.JsonBackend(json_data=data)
        pyslate_en = create_pyslate("en", backend=backend, context={"observer": obs})
        self.assertEqual("sea", pyslate_en.t("location_info", **rl.pyslatize()))  # no TerrainArea for this pos, so sea

        grassland_type = TerrainType("grassland")
        big_area = geometry.Polygon([[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]])
        grassland_area = TerrainArea(big_area, grassland_type)  # TerrainArea says rl is now grassland
        db.session.add_all([rl, grassland_type, grassland_area])

        self.assertEqual("grassland", pyslate_en.t("location_info", **rl.pyslatize()))

        rl_observed_name = ObservedName(obs, rl, "Wonderland")
        db.session.add(rl_observed_name)
        self.assertEqual("Wonderland", pyslate_en.t("location_info", **rl.pyslatize()))

    def test_passage_translation(self):

        rl = RootLocation(Point(1, 1), True, 213)

        building_type = LocationType("building", 200)
        loc = Location(rl, building_type)

        passage = Passage.query.filter(Passage.between(loc, rl)).one()

        backend = json_backend.JsonBackend(json_data=data)
        pyslate_en = create_pyslate("en", backend=backend)
        self.assertEqual("door", pyslate_en.t("passage_info", **passage.pyslatize()))

    def test_activity_translation(self):

        rl = RootLocation(Point(1, 1), True, 213)
        initiator = util.create_character("initiator", rl, util.create_player("abc"))

        sword_type = ItemType("sword", 100, portable=True)
        sword = Item(sword_type, rl)
        db.session.add_all([rl, sword_type, sword])
        db.session.flush()

        activity = Activity(sword, "manufacturing", {"groups": {"result": sword.pyslatize()}}, {}, 1, initiator)

        backend = json_backend.JsonBackend(json_data=data)
        pyslate_en = create_pyslate("en", backend=backend)
        self.assertEqual("manufacturing a sword", pyslate_en.t("activity_" + activity.name_tag, **activity.name_params))
        self.assertEqual("manufacturing a sword", pyslate_en.t("activity_info", **activity.pyslatize()))

        pyslate_pl = create_pyslate("pl", backend=backend)
        self.assertEqual("produkcja miecza", pyslate_pl.t("activity_" + activity.name_tag, **activity.name_params))
        self.assertEqual("produkcja miecza", pyslate_pl.t("activity_info", **activity.pyslatize()))

    tearDown = util.tear_down_rollback
