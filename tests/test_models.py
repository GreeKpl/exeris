import sqlalchemy
from exeris.core import actions, properties_base, main
from exeris.core import recipes
from exeris.core.general import GameDate
from exeris.core.main import db, Types
from exeris.core.map_data import MAP_HEIGHT, MAP_WIDTH
from exeris.core.models import RootLocation, Location, Item, EntityProperty, EntityTypeProperty, \
    ItemType, Passage, TypeGroup, TypeGroupElement, EntityRecipe, BuildMenuCategory, LocationType, Character, \
    Entity, Activity, SkillType, PassageType
from exeris.core.properties_base import EntityPropertyException, P
from exeris.core.recipes import ActivityFactory, RecipeListProducer
from exeris.extra import hooks
from flask_testing import TestCase
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from tests import util


class LocationTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_insert_basic(self):
        pos = Point(10, 20)
        root_loc = RootLocation(pos, 100)  # the simplest
        db.session.add(root_loc)

        root_loc2 = RootLocation(pos, 370)  # normalize direction
        self.assertEqual(10, root_loc2.direction)
        db.session.add(root_loc2)
        self.assertEqual(10, root_loc2.direction)

    def test_insert_validate_position(self):
        pos = Point(MAP_WIDTH + 20, 30)
        root_loc = RootLocation(pos, 30)  # normalize position
        db.session.add(root_loc)

        self.assertAlmostEqual(20, root_loc.position.x, places=6)
        self.assertAlmostEqual(30, root_loc.position.y, places=6)

        pos2 = Point(20, MAP_HEIGHT + 30)
        root_loc2 = RootLocation(pos2, 30)  # normalize position
        db.session.add(root_loc2)

        self.assertAlmostEqual(MAP_WIDTH / 2 + 20, root_loc2.position.x, places=6)
        self.assertAlmostEqual(MAP_HEIGHT - 30, root_loc2.position.y, places=6)

    def test_find_position_by_query(self):
        pos = Point(10, 20)
        root_loc = RootLocation(pos, 100)  # the simplest
        db.session.add(root_loc)

        good_query_results = db.session.query(RootLocation).filter_by(position=from_shape(Point(10, 20))).all()
        bad_query_results = db.session.query(RootLocation).filter_by(position=from_shape(Point(20, 20))).all()

        self.assertEqual(1, len(good_query_results))
        self.assertEqual(0, len(bad_query_results))

    def test_find_root(self):
        pos = Point(10, 20)
        root_loc = RootLocation(pos, 100)  # the simplest

        building_type = LocationType("building", 2000)
        farmyard_type = LocationType("farmyard", 0)

        db.session.add_all([root_loc, building_type, farmyard_type])

        farmyard = Location(root_loc, farmyard_type)
        db.session.add(farmyard)

        building = Location(farmyard, building_type)
        db.session.add(building)

        room = Location(building, building_type)
        db.session.add(room)

        self.assertEqual(root_loc, room.get_root())

    def test_methods_get_items_characters_inside(self):
        root_loc = RootLocation(Point(20, 20), 100)
        building_type = LocationType("building", 2000)
        loc = Location(root_loc, building_type)

        db.session.add_all([building_type, root_loc, loc])

        # items
        type1 = ItemType("sword", 1000)
        db.session.add(type1)

        item1 = Item(type1, loc, weight=200)
        item2 = Item(type1, loc, weight=300)

        db.session.add_all([item1, item2])

        self.assertCountEqual([item1, item2], loc.get_items_inside())

        plr = util.create_player("Player1")

        # characters
        ch1 = util.create_character("Janusz", loc, plr)

        db.session.add(plr)
        db.session.add(ch1)

        self.assertCountEqual([ch1], loc.get_characters_inside())

    def _loc_is_in_loc(self, moved_loc, parent_loc):
        # there's an exactly one passage
        Passage.query.filter(sqlalchemy.sql.expression.or_(Passage.left_location == moved_loc,
                                                           Passage.right_location == moved_loc)).one()
        # and it's the passage between `moved_loc` and `parent_loc`
        Passage.query.filter(Passage.between(moved_loc, parent_loc)).one()
        self.assertEqual(parent_loc, moved_loc.being_in)

    def test_moving_location_between_locations(self):
        building_type = LocationType("building", 200)
        rl = RootLocation(Point(10, 20), 213)

        mobile_loc_type = LocationType("mobile_type", 20)
        mobile_loc_type.properties.append(EntityTypeProperty(P.MOBILE, {}))

        mobile_location = Location(rl, mobile_loc_type)

        loc1 = Location(rl, building_type)
        loc2 = Location(rl, building_type)

        db.session.add_all([building_type, rl, mobile_loc_type, mobile_location, loc1, loc2])
        db.session.flush()

        actions.move_entity_between_entities(mobile_location, rl, loc1)
        self._loc_is_in_loc(mobile_location, loc1)

        actions.move_entity_between_entities(mobile_location, loc1, loc2)
        self._loc_is_in_loc(mobile_location, loc2)

        self.assertRaises(ValueError, lambda: actions.move_entity_between_entities(loc2, rl, loc1))

        # check passage and loc.parent_entity


class EntityTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_property_call_by_property(self):
        @properties_base.property_class
        class HappyPropertyType(properties_base.PropertyType):
            __property__ = "Happy"

            def be_happy(self):
                pass

        item_type = ItemType("sickle", 500)

        item = Item(item_type, None, weight=100)
        prop = EntityProperty("Happy", entity=item)
        db.session.add(prop)

        item.be_happy()  # item has property enabling the method, so it should be possible to call it

        item2 = Item(item_type, None, weight=200)
        type_prop = EntityTypeProperty(name="Happy", type=item_type)
        db.session.add(type_prop)

        item2.be_happy()  # item type has property enabling the method, so it should be possible to call it

        db.session.delete(type_prop)

        self.assertRaises(EntityPropertyException, item2.be_happy)

    def test_has_property(self):
        @properties_base.property_class
        class SadPropertyType(properties_base.PropertyType):
            __property__ = "Sad"

            def be_sad(self):
                pass

        item_type = ItemType("potato", 1, stackable=True)

        item = Item(item_type, None, weight=100)
        item.type.properties.append(EntityTypeProperty("Sad", {"very": False, "cookies": 0}))
        item.properties.append(EntityProperty("Sad", {"very": True, "feel": "blue"}))

        db.session.add_all([item_type, item])

        self.assertDictEqual({"very": True, "feel": "blue", "cookies": 0}, item.get_property("Sad"))

    def test_has_property_used_in_query(self):
        rl = RootLocation(Point(1, 2), 31)
        item_type = ItemType("hammer", 1)
        item = Item(item_type, rl, weight=100)
        item_without_properties = Item(item_type, rl, weight=100)

        char = util.create_character("abc", rl, util.create_player("dkwe"))
        activity = Activity(char, "hehe", {}, {}, 1, char)  # stuff used in activities should be ignored in this test
        item_in_activity = Item(item_type, activity, role_being_in=False)

        item.type.properties.append(EntityTypeProperty("Sad", {"very": False, "cookies": 0}))
        item.properties.append(EntityProperty("Happy", {"very": True, "feel": "blue"}))
        item.properties.append(EntityProperty("Sad", {"value": 0.0}))

        db.session.add_all([item_type, item, item_without_properties, rl, activity, item_in_activity])

        Item.query.filter(Item.has_property("Happy")).filter(Item.role == Entity.ROLE_BEING_IN).one()
        self.assertEqual(2,
                         Item.query.filter(Item.has_property("Sad")).filter(Item.role == Entity.ROLE_BEING_IN).count())

        Item.query.filter(Item.has_property("Happy", feel="blue")).filter(Item.role == Entity.ROLE_BEING_IN).one()
        Item.query.filter(Item.has_property("Sad", value=0.0)).filter(Item.role == Entity.ROLE_BEING_IN).one()

    def test_entity_and_entity_type_has_property_expression(self):
        rl = RootLocation(Point(1, 2), 31)
        item_type = ItemType("hammer", 1)

        item = Item(item_type, rl, weight=100)

        db.session.add_all([rl, item_type, item])

        item_type.properties.append(EntityTypeProperty(P.SKILLS, {"crafting": 5}))

        ItemType.query.filter(ItemType.has_property(P.SKILLS)).one()
        self.assertEqual(0, ItemType.query.filter(ItemType.has_property(P.CLOSEABLE)).count())

        Item.query.filter(Item.has_property(P.SKILLS)).one()  # there should be exactly one item
        self.assertEqual(0, Item.query.filter(Item.has_property(P.CLOSEABLE)).count())

        ItemType.query.filter(ItemType.has_property(P.SKILLS, crafting=5)).one()
        self.assertEqual(0, ItemType.query.filter(ItemType.has_property(P.CLOSEABLE, crafting=1)).count())
        self.assertEqual(0, ItemType.query.filter(ItemType.has_property(P.SKILLS, crafting=1)).count())

        Item.query.filter(Item.has_property(P.SKILLS, crafting=5)).one()  # there should be exactly one item
        self.assertEqual(0, Item.query.filter(Item.has_property(P.CLOSEABLE, crafting=1)).count())
        self.assertEqual(0, Item.query.filter(Item.has_property(P.SKILLS, crafting=1)).count())

        propertyless_item = Item(item_type, rl, weight=150)  # a test item that should never be selected
        item.properties.append(EntityProperty(P.EDIBLE, {"yummy": True}))
        db.session.add(propertyless_item)

        Item.query.filter(Item.has_property(P.EDIBLE)).one()  # there should be exactly one item
        self.assertEqual(0, Item.query.filter(Item.has_property(P.CLOSEABLE)).count())

        item_type.properties.append(EntityTypeProperty(P.EDIBLE, {"yummy": False}))

        Item.query.filter(Item.has_property(P.EDIBLE, yummy=True)).one()  # there should be exactly one item
        self.assertEqual(0, Item.query.filter(Item.has_property(P.CLOSEABLE, yummy=False)).count())

        self.assertEqual(propertyless_item, Item.query.filter(Item.has_property(P.EDIBLE, yummy=False)).one())

        item_edible_property = EntityProperty.query.filter_by(entity=item, name=P.EDIBLE).one()
        item_edible_property.data = {"yummy": True, "level": 5, "help": "me"}

        Item.query.filter(
            Item.has_property(P.EDIBLE, yummy=True, level=5, help="me")).one()  # there should be exactly one item
        self.assertEqual(0, Item.query.filter(Item.has_property(P.EDIBLE, yummy=False, level=5, help="me")).count())

        item_edible_property.data = {"level": 5, "help": "me"}

        # yummy is from type, level and help are from entity
        Item.query.filter(
            Item.has_property(P.EDIBLE, yummy=False, level=5, help="me")).one()  # there should be exactly one item
        self.assertEqual(0, Item.query.filter(Item.has_property(P.EDIBLE, yummy=True, level=5, help="me")).count())

        Item.query.filter(
            Item.has_property(P.EDIBLE, level=5)).one()  # there should be exactly one item
        Item.query.filter(
            Item.has_property(P.EDIBLE, level=5, help="me")).one()  # there should be exactly one item

    def test_change_character_name(self):
        util.initialize_date()

        plr = util.create_player("jdiajw")
        rl = RootLocation(Point(1, 1), 123)

        char = Character("John", Character.SEX_MALE, plr, "en", GameDate(120), Point(1, 1), rl)
        self.assertEqual("John", char.name)

        char.name = "Eddy"
        self.assertEqual("Eddy", char.name)

        db.session.flush()

        char.name = "James"
        self.assertEqual("James", char.name)

    def test_removal_of_entity_with_activity(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), 123)
        char = util.create_character("abc", rl, util.create_player("abc"))

        item_type = ItemType("sickle", 500)
        item = Item(item_type, rl)

        activity = Activity(item, "sharpening sickle", {}, {}, 1, char)

        db.session.add_all([item_type, item, activity])
        db.session.flush()

        item.remove()

        self.assertIsNone(item.parent_entity)
        self.assertIsNone(activity.parent_entity)

        activity.remove()

    def test_persistence_of_normalized_states(self):
        """
        Test two normalized states: tiredness and damage (because it can be accessed through a hybrid property)
        """
        rl = RootLocation(Point(1, 1), 10)
        test_char = util.create_character("jan", rl, util.create_player("ala123"))

        self.assertEqual(0, test_char.damage)  # hard-coded default value
        self.assertEqual(0, test_char.states["tiredness"])  # default value stored in EntityTypeProperty

        test_char.states["damage"] += 0.1
        self.assertEqual(0.1, test_char.damage)

        test_char.states["tiredness"] = 2
        self.assertEqual(1, test_char.states["tiredness"])

        test_char.states["tiredness"] -= 0.5
        self.assertEqual(0.5, test_char.states["tiredness"])


class RootLocationTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_is_permanent_for_temporary_locations(self):
        root_location = RootLocation(Point(30, 30), 23)
        db.session.add_all([root_location])

        # empty
        self.assertFalse(root_location.is_permanent())

        cart_type = LocationType("cart", 100)
        cart_type.properties.append(EntityTypeProperty(P.MOBILE, {True: True}))
        hammer_type = ItemType("hammer", 200)
        hammer = Item(hammer_type, root_location)

        cart = Location(root_location, cart_type)
        db.session.add_all([hammer_type, hammer, cart_type, cart])

        self.assertFalse(root_location.is_permanent())

    def test_is_permanent_for_permanent_locations(self):
        root_location = RootLocation(Point(30, 30), 23)
        db.session.add(root_location)

        # fixed item
        landmark_type = ItemType("landmark", 200, portable=False)
        landmark = Item(landmark_type, root_location)
        db.session.add_all([landmark_type, landmark])

        self.assertTrue(root_location.is_permanent())

        root_location = RootLocation(Point(30, 30), 23)
        db.session.add(root_location)

        # not mobile building
        building_type = LocationType("building", 100)
        building = Location(root_location, building_type)
        db.session.add_all([building_type, building])

        self.assertTrue(root_location.is_permanent())

    def _prepare_center(self, x=30, y=30):
        center = RootLocation(Point(x, y), 23)
        center.title = "center"
        db.session.add(center)
        return center

    def test_can_be_permanent_true(self):
        center = self._prepare_center()

        # fixed item
        landmark_type = ItemType("landmark", 200, portable=False)
        hammer_type = ItemType("hammer", 200)

        loc_being_too_far_away = RootLocation(Point(19, 30), 23)
        loc_being_too_far_away.title = "too_far_away"
        landmark = Item(landmark_type, loc_being_too_far_away)

        loc_without_fixed_item = RootLocation(Point(20, 30), 23)
        loc_without_fixed_item.title = "without_fixed_item"

        hammer = Item(hammer_type, loc_without_fixed_item)

        db.session.add_all([landmark_type, landmark, loc_being_too_far_away,
                            loc_without_fixed_item, hammer_type, hammer])

        self.assertTrue(center.can_be_permanent())

        # center being parmanent doesn't affect can_be_permanent() state
        building_type = LocationType("building", 100)
        building = Location(center, building_type)
        db.session.add_all([building_type, building])

        self.assertTrue(center.can_be_permanent())

    def test_can_be_permanent_false(self):
        center = self._prepare_center()

        # fixed item
        landmark_type = ItemType("landmark", 200, portable=False)

        loc_with_fixed_item = RootLocation(Point(27, 30), 23)
        loc_with_fixed_item.title = "with_fixed_item"
        landmark = Item(landmark_type, loc_with_fixed_item)

        db.session.add_all([landmark_type, landmark, loc_with_fixed_item])

        self.assertFalse(center.can_be_permanent())

        center = self._prepare_center(40, 50)
        loc_with_immobile_location = RootLocation(Point(42, 50), 23)
        loc_with_immobile_location.title = "with_immobile_location"

        building_type = LocationType("building", 100)
        building = Location(loc_with_immobile_location, building_type)
        db.session.add_all([building_type, building])

        self.assertFalse(center.can_be_permanent())

    def test_root_location_removed_when_empty(self):
        root_location = RootLocation(Point(1, 1), 23)
        root_location_near = RootLocation(Point(1, 2), 23)
        hammer_type = ItemType("hammer", 20)
        hammer = Item(hammer_type, root_location)

        taker_char = util.create_character("taker", root_location, util.create_player("abc"))

        db.session.add_all([root_location, hammer_type, hammer])
        actions.move_entity_between_entities(hammer, root_location, taker_char, 1)  # item taken by character

        self.assertEqual(Point(1, 1), root_location.position)  # root location not removed

        # move character away and hammer back on ground
        hammer.being_in = root_location
        taker_char.being_in = root_location_near

        actions.move_entity_between_entities(hammer, root_location, taker_char, 1)  # item taken by character
        self.assertIn(root_location, db.session.deleted)  # RootLocation was empty, so it got deleted


class PassageTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_accessibility(self):
        building_type = LocationType("building", 200)
        rl = RootLocation(Point(10, 20), 213)
        loc1 = Location(rl, building_type)
        loc2 = Location(rl, building_type)

        db.session.add_all([rl, building_type, loc1, loc2])
        passage1 = Passage.query.filter(Passage.between(rl, loc1)).first()
        passage2 = Passage.query.filter(Passage.between(rl, loc2)).first()

        passage1.properties.append(EntityProperty(P.CLOSEABLE, {"closed": False}))
        passage2.properties.append(EntityProperty(P.CLOSEABLE, {"closed": True}))

        self.assertTrue(passage1.is_accessible())
        self.assertFalse(passage2.is_accessible())


class GroupTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_group_direct_modification(self):
        self._setup_hammers()

        hammers = TypeGroup("group_hammers", stackable=False)

        hammers._children_junction.append(TypeGroupElement(self.stone_hammer))
        hammers._children_junction.append(TypeGroupElement(self.iron_hammer))
        hammers._children_junction.append(TypeGroupElement(self.marble_hammer))

        db.session.add(hammers)

        self.assertCountEqual([self.stone_hammer, self.iron_hammer, self.marble_hammer], hammers.children)

    def test_group_modification(self):
        self._setup_hammers()

        tools = TypeGroup("group_tools", stackable=False)
        hammers = TypeGroup("group_hammers", stackable=False)

        hammers.add_to_group(self.stone_hammer)
        hammers.add_to_group(self.iron_hammer)
        hammers.add_to_group(self.marble_hammer)

        tools.add_to_group(hammers)

        db.session.add_all([hammers, tools])

        self.assertCountEqual([self.stone_hammer, self.iron_hammer, self.marble_hammer], hammers.children)

        self.assertEqual([hammers], self.stone_hammer.parent_groups)
        self.assertEqual([tools], hammers.parent_groups)

    def test_groups_conclusion(self):
        useful = TypeGroup("group_useful", stackable=False)
        tools = TypeGroup("group_tools", stackable=False)
        hammers = TypeGroup("group_hammers", stackable=False)
        swords = TypeGroup("group_swords", stackable=False)

        useful.add_to_group(tools)
        tools.add_to_group(hammers)

        db.session.add_all([useful, tools, hammers, swords])

        self.assertTrue(tools.contains(hammers))
        self.assertTrue(useful.contains(hammers))
        self.assertFalse(tools.contains(swords))
        self.assertFalse(hammers.contains(tools))

        self.assertEqual([useful, tools, hammers], useful.get_group_path(hammers))

    def test_groups_quantity_efficiency(self):
        fuel = TypeGroup("group_fuel", stackable=True)
        wood = TypeGroup("group_wood", stackable=True)
        pine_wood = TypeGroup("group_pine_wood", stackable=True)
        old_pine_wood = ItemType("old_pine_wood", 50, stackable=True)
        fine_oak_wood = ItemType("fine_oak_wood", 70, stackable=True)

        fuel.add_to_group(wood, efficiency=0.5)
        wood.add_to_group(pine_wood, efficiency=1.5)
        pine_wood.add_to_group(old_pine_wood, efficiency=0.75)
        wood.add_to_group(fine_oak_wood)

        db.session.add_all([fuel, wood, pine_wood, old_pine_wood, fine_oak_wood])

        self.assertEqual(0.5, fuel.quantity_efficiency(fine_oak_wood))
        self.assertEqual(0.5625, fuel.quantity_efficiency(old_pine_wood))

    def test_groups_quality_and_quantity_efficiency(self):
        tools = TypeGroup("group_tools", stackable=False)
        hammers = TypeGroup("group_hammers", stackable=False)
        fruits = TypeGroup("group_fruits", stackable=True)
        apple = ItemType("apple", 30, stackable=True)

        tools.add_to_group(hammers, efficiency=2.0)
        fruits.add_to_group(apple, efficiency=5.0)

        db.session.add_all([tools, hammers, fruits, apple])

        self.assertEqual(2.0, tools.quality_efficiency(hammers))
        self.assertEqual(1.0, tools.quantity_efficiency(hammers))

        self.assertEqual(1.0, fruits.quality_efficiency(apple))
        self.assertEqual(5.0, fruits.quantity_efficiency(apple))

    def test_group_get_descending_types(self):
        tools = TypeGroup("group_tools", stackable=False)
        hammers = TypeGroup("group_hammer", stackable=False)
        axes = TypeGroup("group_axes", stackable=False)

        stone_axe = ItemType("stone_axe", 100)
        bone_axe = ItemType("bone_axe", 200)
        copper_hammer = ItemType("copper_hammer", 300)

        db.session.add_all([tools, hammers, axes, stone_axe, bone_axe, copper_hammer])

        tools.add_to_group(hammers)
        tools.add_to_group(axes, efficiency=2.0)

        axes.add_to_group(stone_axe, efficiency=2.0)
        axes.add_to_group(bone_axe, efficiency=0.5)
        hammers.add_to_group(copper_hammer, efficiency=10.0)

        self.assertCountEqual([(stone_axe, 4.0), (bone_axe, 1.0), (copper_hammer, 10.0)], tools.get_descending_types())

    def _setup_hammers(self):
        self.stone_hammer = ItemType("stone_hammer", 200)
        self.iron_hammer = ItemType("iron_hammer", 300)
        self.marble_hammer = ItemType("marble_hammer", 500)

        db.session.add_all([self.stone_hammer, self.iron_hammer, self.marble_hammer])

    def test_create_activity_from_recipe(self):
        stone_type = ItemType("stone", 50, stackable=True)
        hammer_type = ItemType("hammer", 100)

        tools_category = BuildMenuCategory("tools")
        rl = RootLocation(Point(1, 1), 32)
        db.session.add_all([rl, hammer_type, stone_type, tools_category])
        db.session.flush()

        recipe = EntityRecipe("project_manufacturing", {"item_name": "hammer"}, {"input": {stone_type.name: 20.0}}, 11,
                              tools_category, result_entity=hammer_type)
        db.session.add(recipe)

        initiator = util.create_character("John", rl, util.create_player("AAA"))

        factory = ActivityFactory()
        activity = factory.create_from_recipe(recipe, rl, initiator, user_input={"item_name": "mloteczek", "amount": 3})

        self.assertCountEqual({"input": {stone_type.name: 60.0}}, activity.requirements)
        self.assertEqual(33, activity.ticks_left)

        portable_item_in_constr = ItemType("portable_item_in_constr", 1, portable=True)
        db.session.add(portable_item_in_constr)
        recipe.activity_container = "entity_specific_item"
        activity = factory.create_from_recipe(recipe, rl, initiator, user_input={"amount": 3})
        self.assertEqual(ItemType.by_name(Types.PORTABLE_ITEM_IN_CONSTRUCTION), activity.being_in.type)

        anvil_type = ItemType("anvil", 100, portable=False)
        anvil = Item(anvil_type, rl)
        db.session.add_all([anvil_type, anvil])
        recipe.activity_container = "selected_machine"

        activity = factory.create_from_recipe(recipe, anvil, initiator, user_input={"amount": 3})
        self.assertEqual(anvil, activity.being_in)

        recipe.result_entity = None
        recipe.result = [["exeris.core.actions.CreateItemAction", dict(item_type=hammer_type.name, properties={},
                                                                       used_materials="all")]]

        self.assertEqual(hammer_type.name, factory.get_first_entity_creation_action(recipe))

    def test_create_activity_in_location_being_machine_for_recipe(self):
        mare_type = LocationType("mare", 400)
        rl = RootLocation(Point(1, 1), 100)
        milk_type = ItemType("milk", 20, stackable=True)
        invisible_passage = PassageType.query.filter_by(name=Types.INVISIBLE_PASSAGE).one()
        mare = Location(rl, mare_type, passage_type=invisible_passage)
        char = util.create_character("heheszki", rl, util.create_player("123"))

        build_menu_category = BuildMenuCategory("domestication")
        milking_result = ["exeris.core.actions.CollectResourcesFromDomesticatedAnimalAction", {"resource_type": "milk"}]
        recipe = EntityRecipe("milking_animal", {"milk": "yes"}, {"mandatory_machines": ["mare"]}, 10,
                              build_menu_category, result=[milking_result], activity_container="selected_machine")
        db.session.add_all([mare_type, rl, invisible_passage, mare, recipe, milk_type])

        factory = ActivityFactory()
        activity = factory.create_from_recipe(recipe, mare, char)
        self.assertEqual("milking_animal", activity.name_tag)
        self.assertEqual({"milk": "yes"}, activity.name_params)

        self.assertEqual(mare, activity.being_in)
        self.assertEqual("exeris.core.actions.CollectResourcesFromDomesticatedAnimalAction",
                         activity.result_actions[0][0])
        self.assertEqual({"resource_type": "milk"},
                         activity.result_actions[0][1])

    def test_create_activity_in_passage_being_machine_for_recipe(self):
        rl = RootLocation(Point(1, 1), 100)
        building_type = LocationType("building", 100)
        building = Location(rl, building_type)

        char = util.create_character("heheszki", rl, util.create_player("123"))

        build_menu_category = BuildMenuCategory("locks")
        recipe = EntityRecipe("building_lock", {"abc": 1}, {"mandatory_machines": [Types.DOOR]}, 10,
                              build_menu_category, result=[], activity_container="selected_machine")
        db.session.add_all([building_type, rl, building, build_menu_category, recipe])

        factory = ActivityFactory()
        passage = Passage.query.filter(Passage.between(rl, building)).one()
        activity = factory.create_from_recipe(recipe, passage, char)
        self.assertEqual("building_lock", activity.name_tag)
        self.assertEqual({"abc": 1}, activity.name_params)

        self.assertEqual(passage, activity.being_in)

    def test_available_user_inputs_for_recipe(self):
        stone_type = ItemType("stone", 50, stackable=True)
        hammer_type = ItemType("hammer", 100)

        tools_category = BuildMenuCategory("tools")
        rl = RootLocation(Point(1, 1), 32)
        db.session.add_all([rl, hammer_type, stone_type, tools_category])
        db.session.flush()

        recipe = EntityRecipe("project_manufacturing", {"item_name": "hammer"},
                              {"input": {stone_type.name: 20.0}, "mandatory_machines": ["anvil"]}, 11,
                              tools_category, result_entity=hammer_type, activity_container="selected_machine")
        db.session.add(recipe)

        initiator = util.create_character("John", rl, util.create_player("AAA"))
        factory = ActivityFactory()

        user_inputs = factory.get_user_inputs_for_recipe(recipe)
        self.assertEqual(["amount"], list(user_inputs.keys()))
        self.assertEqual("exeris.core.actions.CreateItemAction", user_inputs["amount"].action_name)
        self.assertEqual({"item_type": hammer_type.name, "properties": {}, "used_materials": "all"},
                         user_inputs["amount"].action_args)

        anvil_type = ItemType("anvil", 100, portable=False)
        anvil1 = Item(anvil_type, rl)
        anvil2 = Item(anvil_type, rl)
        db.session.add_all([anvil_type, anvil1, anvil2])

        selectable_machines = factory.get_selectable_machines(recipe, initiator)
        self.assertCountEqual([anvil1, anvil2], selectable_machines)

    def test_get_recipes_list(self):
        rl = RootLocation(Point(1, 1), 32)
        initiator = util.create_character("John", rl, util.create_player("AAA"))

        stone_type = ItemType("stone", 50, stackable=True)
        hammer_type = ItemType("hammer", 100)
        anvil_type = ItemType("anvil", 100)

        tools_category = BuildMenuCategory("tools")
        rl = RootLocation(Point(1, 1), 32)
        db.session.add_all([rl, hammer_type, stone_type, anvil_type, tools_category])
        db.session.flush()

        unavailable_recipe = EntityRecipe("project_manufacturing", {"item_name": "hammer"},
                                          {"input": {stone_type.name: 20.0}, "mandatory_machines": ["anvil"]}, 11,
                                          tools_category, result_entity=hammer_type,
                                          activity_container="selected_machine")
        available_recipe = EntityRecipe("project_manufacturing", {"item_name": "hammer"},
                                        {"input": {stone_type.name: 20.0}, "optional_machines": {"anvil": 1}}, 11,
                                        tools_category, result_entity=hammer_type,
                                        activity_container="selected_machine")
        db.session.add_all([unavailable_recipe, available_recipe])

        recipe_list_producer = RecipeListProducer(initiator)

        self.assertEqual([available_recipe], recipe_list_producer.get_recipe_list())

    def test_perform_error_check_for_activity_from_recipe_creation(self):
        hammer_type = ItemType("hammer", 100)

        rl = RootLocation(Point(1, 1), 32)
        building_type = LocationType("building", 1000)
        initiator = util.create_character("John", rl, util.create_player("AAA"))
        initiator.properties.append(EntityProperty(P.SKILLS, {}))
        baking_skill_type = SkillType("smithing", "crafting")

        tools_category = BuildMenuCategory("tools")
        recipe = EntityRecipe("project_manufacturing", {"item_name": "hammer"}, {"location_types": ["building"],
                                                                                 "skills": {"smithing": 0.2}}, 11,
                              tools_category, result_entity=hammer_type)

        db.session.add_all([hammer_type, rl, building_type, baking_skill_type, tools_category, recipe])

        activity_factory = ActivityFactory()
        self.assertCountEqual([main.InvalidLocationTypeException, main.TooLowSkillException],
                              [o.__class__ for o in activity_factory.get_list_of_errors(recipe, initiator)])

    def test_build_menu_categories(self):
        buildings = BuildMenuCategory("buildings")
        wooden_buildings = BuildMenuCategory("wooden_buildings", buildings)
        stone_buildings = BuildMenuCategory("stone_buildings", buildings)
        tools = BuildMenuCategory("tools")
        steel_tools = BuildMenuCategory("steel_tools", tools)
        bone_tools = BuildMenuCategory("bone_tools", tools)

        db.session.add_all([buildings, wooden_buildings, stone_buildings, tools, steel_tools, bone_tools])

        steel_hammer = EntityRecipe("project_manu", {"name": "steel_hammer"}, {}, 11, steel_tools)
        steel_needle = EntityRecipe("project_manu", {"name": "steel_needle"}, {}, 5, steel_tools)
        stone_hut = EntityRecipe("project_build", {"name": "stone_hut"}, {}, 11, stone_buildings)

        db.session.add_all([steel_hammer, steel_needle, stone_hut])

        # buildings build menu structure
        self.assertCountEqual([stone_buildings, wooden_buildings], buildings.child_categories)
        self.assertCountEqual([stone_hut], stone_buildings.get_recipes())

        # tools build menu structure
        self.assertCountEqual([steel_tools, bone_tools], tools.child_categories)
        self.assertCountEqual([steel_hammer, steel_needle], steel_tools.get_recipes())


class ListenersTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_listeners_for_entities(self):
        test_item_type = ItemType("test_item", 100)
        rl = RootLocation(Point(1, 1), 100)
        test_item = Item(test_item_type, rl)
        db.session.add_all([test_item_type, rl, test_item])
        db.session.flush()

        # test whether listener in __init__ worked fine
        test_item.states[main.States.HUNGER] = 0.5
        self.assertEqual(0.5, test_item.states[main.States.HUNGER])
        test_item.states[main.States.HUNGER] = 1.5
        self.assertEqual(1.0, test_item.states[main.States.HUNGER])
        test_item.states[main.States.HUNGER] = -1
        self.assertEqual(0, test_item.states[main.States.HUNGER])

        test_item, test_entity = None, None

        test_item = Item.query.one()
        test_item.states[main.States.HUNGER] = -1
        self.assertEqual(0, test_item.states[main.States.HUNGER])

        test_item = Item.query.one()
        test_item.states[main.States.HUNGER] = 1.3
        self.assertEqual(1, test_item.states[main.States.HUNGER])
