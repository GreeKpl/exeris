import datetime
import logging
import traceback

import flask_socketio as client_socket
import os
import psycopg2
import redis
from exeris.core import models, main, general
from exeris.core.i18n import create_pyslate
from exeris.core.main import create_app, db, Types
from exeris.core.properties_base import P
from flask import g, request
from flask_bootstrap import Bootstrap
from flask_bower import Bower
from flask_login import current_user
from flask_oauthlib.provider import OAuth2Provider
from flask_redis import FlaskRedis
from flask_security import SQLAlchemyUserDatastore, Security, RegisterForm
from flask_security.forms import Required
from flask_socketio import SocketIO
from functools import wraps
from flask_wtf import RecaptchaField
from wtforms import validators
from geoalchemy2.shape import from_shape
from pyslate.backends import postgres_backend
from shapely.geometry import Point, Polygon
from wtforms import StringField, SelectField
from flask_mail import Mail

# noinspection PyUnresolvedReferences
from exeris.core import achievements

logger = logging.getLogger(__name__)

exeris_config_path = os.environ.get("EXERIS_CONFIG_PATH", "")
app = create_app(own_config_file_path=exeris_config_path)

Bootstrap(app)
socketio = SocketIO(app, message_queue=app.config["SOCKETIO_REDIS_DATABASE_URI"])
Bower(app)

mail = Mail(app)

redis_db = FlaskRedis.from_custom_provider(redis.StrictRedis, app)

oauth = OAuth2Provider(app)


class ExtendedRegisterForm(RegisterForm):
    id = StringField('Username', [Required(),
                                  validators.Regexp(r'^[a-zA-Z0-9][a-zA-Z0-9_\-]+$',
                                                    message='Identifiers can contain only alphanumerics, ' +
                                                            '"_" and "-". It must start with an alphanumeric character'),
                                  validators.Length(min=3, max=20)])
    language = SelectField('Language', [Required()], choices=[("en", "English")])


if app.config["USE_RECAPTCHA_IN_FORMS"]:
    ExtendedRegisterForm.recaptcha = RecaptchaField("Recaptcha")

user_datastore = SQLAlchemyUserDatastore(db, models.Player, models.Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm,
                    confirm_register_form=ExtendedRegisterForm)


def socketio_outer_event(*args, **kwargs):
    socketio_handler = socketio.on(*args, **kwargs)

    def dec(f):
        @wraps(f)
        def fg(*a, **k):
            g.language = request.args.get("language")
            conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
            g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"))
            result = f(*a, **k)  # argument list (the first and only positional arg) is expanded
            return (True,) + (result if result else ())

        return socketio_handler(fg)

    return dec


def socketio_player_event(*args, **kwargs):
    socketio_handler = socketio.on(*args, **kwargs)

    def dec(f):
        @wraps(f)
        def fg(*a, **k):
            if not current_user.is_authenticated:
                logger.warn("Disconnected unwanted user", request.access_route)
                client_socket.disconnect()

            character_id = request.args.get("character_id", 0)
            g.player = current_user
            g.language = g.player.language
            if character_id:
                g.character = models.Character.by_id(character_id)
                g.language = g.character.language

            conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
            g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"))
            result = f(*a, **k)  # argument list (the first and only positional arg) is expanded
            return (True,) + (result if result else ())

        return socketio_handler(fg)

    return dec


def socketio_character_event(*args, **kwargs):
    socketio_handler = socketio.on(*args, **kwargs)

    def dec(f):
        @wraps(f)
        def fg(*a, **k):
            if not current_user.is_authenticated:
                logger.warn("Disconnected unwanted user", request.access_route)
                client_socket.disconnect()
            character_id = request.args.get("character_id")
            g.player = current_user
            g.character = models.Character.by_id(character_id)
            g.language = g.character.language
            conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
            g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"),
                                       character=g.character)

            if not g.character.is_alive:
                raise main.CharacterDeadException(character=g.character)

            result = f(*a, **k)  # argument list (the first and only positional arg) is expanded
            return (True,) + (result if result else ())

        return socketio_handler(fg)

    return dec


app.encode = main.encode
app.decode = main.decode

from exeris.outer import outer_bp
from exeris.player import player_bp
from exeris.character import character_bp, character_static


@app.before_first_request
def create_database():
    db.create_all()

    models.init_database_contents()

    if not models.GameDateCheckpoint.query.count():
        new_root = models.RootLocation(Point(1, 1), 123)
        db.session.add(new_root)

        ch_pt = models.GameDateCheckpoint(game_date=0, real_date=datetime.datetime.now().timestamp())
        db.session.add(ch_pt)

        character_type = models.EntityType.by_name(Types.ALIVE_CHARACTER)

        character_type.properties.append(models.EntityTypeProperty(P.DYNAMIC_NAMEABLE))

        dead_character_type = models.EntityType.by_name(Types.DEAD_CHARACTER)
        dead_character_type.properties.append(models.EntityTypeProperty(P.DYNAMIC_NAMEABLE))

        hammer_type = models.ItemType("hammer", 200)
        hammer = models.Item(hammer_type, models.RootLocation.query.one())

        potatoes_type = models.ItemType("potatoes", 20, stackable=True)
        potatoes = models.Item(potatoes_type, models.RootLocation.query.one(), amount=5000)
        signpost_type = models.ItemType("signpost", 500, portable=False)
        db.session.add_all([potatoes_type, potatoes, signpost_type, hammer])

        potatoes_type = models.EntityType.query.filter_by(name="potatoes").one()
        potatoes_type.properties.append(
            models.EntityTypeProperty(P.EDIBLE, {"states": {main.States.HUNGER: -0.1, main.States.SATIATION: 0.05}}))

        gathering_build_menu_category = models.BuildMenuCategory("gathering")
        oak_type = models.ItemType("oak", 50, stackable=True)
        oak_tree_type = models.ItemType("oak_tree", 50, portable=False)
        oak_area = models.ResourceArea(oak_type, Point(5, 5), 3, 20, 500)
        chopping_result = [["exeris.core.actions.CollectGatheredResourcesAction", {"resource_type": "oak"}]]
        chopping_oak_recipe = models.EntityRecipe("chopping_oak", {},
                                                  {"required_resources": ["oak"], "terrain_types": ["forest"],
                                                   "location_types": ["outside"]},
                                                  6, gathering_build_menu_category,
                                                  result=chopping_result, activity_container="oak_tree")
        db.session.add_all([gathering_build_menu_category, oak_type, oak_tree_type, oak_area, chopping_oak_recipe])

        item_in_construction_type = models.ItemType("portable_item_in_constr", 1, portable=True)
        db.session.add(item_in_construction_type)

        item_in_construction_type = models.ItemType("fixed_item_in_constr", 1, portable=False)
        db.session.add(item_in_construction_type)

        build_menu_category = models.BuildMenuCategory("structures")
        signpost_recipe = models.EntityRecipe("building_signpost", {}, {"location_types": Types.OUTSIDE}, 10,
                                              build_menu_category, result_entity=models.ItemType.by_name("signpost"))
        db.session.add_all([build_menu_category, signpost_recipe])

        build_menu_category = models.BuildMenuCategory.query.filter_by(name="structures").one()
        hut_type = models.LocationType("hut", 500)
        hut_type.properties.append(models.EntityTypeProperty(P.ENTERABLE))
        hut_recipe = models.EntityRecipe("building_hut", {}, {"input": {"group_stone": 5}, "permanence": True}, 3,
                                         build_menu_category,
                                         result=[["exeris.core.actions.CreateLocationAction",
                                                  {"location_type": hut_type.name, "properties": {},
                                                   "used_materials": "all",
                                                   "visible_material": {"main": "group_stone"}}],
                                                 ["exeris.core.actions.AddNameToEntityAction", {}]],
                                         activity_container="fixed_item")
        db.session.add_all([hut_type, hut_recipe])

        grass_terrain = models.TerrainType("grassland")
        forest_terrain = models.TerrainType("forest")
        deep_water_terrain = models.TerrainType("deep_water")
        road_terrain = models.TerrainType("road")
        db.session.add_all([grass_terrain, deep_water_terrain])
        land_terrain_type = models.TypeGroup.by_name(Types.LAND_TERRAIN)
        land_terrain_type.add_to_group(grass_terrain)
        land_terrain_type.add_to_group(forest_terrain)
        land_terrain_type.add_to_group(road_terrain)
        water_terrain_type = models.TypeGroup.by_name(Types.WATER_TERRAIN)
        water_terrain_type.add_to_group(deep_water_terrain)

        poly_grass = Polygon([(0.1, 0.1), (0.1, 2), (1, 2), (3, 1)])
        poly_water = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
        poly_grass2 = Polygon([(1, 1), (5, 1), (5, 3), (3, 5), (1, 1)])
        poly_road = Polygon([(1, 1), (0.9, 1.1), (3.9, 4.1), (4, 4), (1, 1)])
        poly_forest = Polygon([(5, 2), (7, 3), (8, 5), (7, 7), (5, 8), (3, 7), (2, 5), (3, 3)])

        grass = models.TerrainArea(poly_grass, grass_terrain)
        water = models.TerrainArea(poly_water, deep_water_terrain, priority=0)
        grass2 = models.TerrainArea(poly_grass2, grass_terrain)
        road = models.TerrainArea(poly_road, road_terrain, priority=3)
        forest = models.TerrainArea(poly_forest, forest_terrain, priority=2)

        land_trav1 = models.PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, poly_grass, grass)
        land_trav2 = models.PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, poly_grass2, grass2)
        land_trav3 = models.PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, poly_forest, forest)

        poly_road_trav = Polygon([(1.2, 0.8), (0.7, 1.3), (3.7, 4.3), (4.2, 3.8)])
        land_trav_road = models.PropertyArea(models.AREA_KIND_TRAVERSABILITY, 2, 2, poly_road_trav, road)

        visibility_poly = Polygon([(0, 0), (0, 50), (50, 50), (50, 0)])
        world_visibility = models.PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, visibility_poly, water)

        db.session.add_all(
            [grass_terrain, deep_water_terrain, road_terrain, grass, water, grass2, road, forest,
             land_trav1, land_trav2, land_trav3, land_trav_road, world_visibility])

        build_menu_category = models.BuildMenuCategory.query.filter_by(name="structures").one()
        tablet_type = models.ItemType("tablet", 100, portable=True)
        tablet_type.properties.append(models.EntityTypeProperty(P.READABLE,
                                                                data={"max_length": 300, "allowed_formats": [
                                                                    models.TextContent.FORMAT_MD]}))

        tablet_production_result = [["exeris.core.actions.CreateItemAction",
                                     {"item_type": tablet_type.name,
                                      "properties": {P.VISIBLE_MATERIAL: {"main": "clay"}},
                                      "used_materials": "all"}]]
        tablet_recipe = models.EntityRecipe("carving_tablet", {}, {}, 2,
                                            build_menu_category, result=tablet_production_result,
                                            activity_container="portable_item")

        anvil_type = models.ItemType("anvil", 100, portable=False)
        anvil_recipe = models.EntityRecipe("making_anvil", {}, {"permanence": True}, 2,
                                           build_menu_category, result_entity=anvil_type,
                                           activity_container="entity_specific_item")

        longsword_type = models.ItemType("longsword", 100, portable=True)
        longsword_recipe = models.EntityRecipe("forging_longsword", {}, {"mandatory_machines": ["anvil"]}, 2,
                                               build_menu_category, result_entity=longsword_type,
                                               activity_container="selected_machine")

        db.session.add_all([tablet_type, tablet_recipe, anvil_type, anvil_recipe, longsword_type, longsword_recipe])

        outside = models.LocationType.by_name(Types.OUTSIDE)
        if not models.EntityTypeProperty.query.filter_by(type=outside, name=P.DYNAMIC_NAMEABLE).count():
            outside.properties.append(models.EntityTypeProperty(P.DYNAMIC_NAMEABLE))

        dead_animal_group = models.TypeGroup(Types.DEAD_ANIMAL)

        pork_type = models.ItemType("pork", 30, stackable=True)
        dead_pig_type = models.LocationType("dead_pig", 30000)
        dead_animal_group.add_to_group(dead_pig_type)
        pig_type = models.LocationType("pig", 30000)
        pig_type.properties.append(models.EntityTypeProperty(P.STATES, {
            main.States.HUNGER: {"initial": 0},
        }))
        pig_type.properties.append(models.EntityTypeProperty(P.ANIMAL, {
            "dead_type": dead_pig_type.name,
            "type_resources": {
                pork_type.name: {
                    "initial": 30,
                    "max": 60,
                },
            }
        }))
        pig_type.properties.append(models.EntityTypeProperty(P.DOMESTICATED, {
            "type_resources_increase": {
                "fatness": {
                    "initial": 5,
                    "affected_resources": {
                        pork_type.name: 0.4,
                    },
                },
            }
        }))
        pig_type.properties.append(models.EntityTypeProperty(P.TAMABLE))

        horsemeat_type = models.ItemType("horse_meat", 30, stackable=True)
        dead_mare_type = models.LocationType("dead_mare", 200000)
        dead_animal_group.add_to_group(dead_mare_type)
        mare_type = models.LocationType("mare", 200000)
        mare_type.properties.append(models.EntityTypeProperty(P.STATES, {
            main.States.HUNGER: {"initial": 0},
        }))
        mare_type.properties.append(models.EntityTypeProperty(P.ENTERABLE))
        mare_type.properties.append(models.EntityTypeProperty(P.ANIMAL, {
            "dead_type": dead_mare_type.name,
            "type_resources": {
                horsemeat_type.name: {
                    "initial": 20,
                    "max": 40,
                },
            }
        }))
        mare_type.properties.append(models.EntityTypeProperty(P.DOMESTICATED, {
            "type_resources_increase": {
                "fatness": {
                    "initial": 5,
                    "affected_resources": {
                        horsemeat_type.name: 0.1,
                    },
                },
            },
        }))
        mare_type.properties.append(models.EntityTypeProperty(P.TAMABLE))

        impassable_to_animal = models.PassageType("impassable_to_animal", True)
        invisible_to_animal = models.PassageType("invisible_to_animal", True)
        invisible_to_animal.properties.append(models.EntityTypeProperty(P.INVISIBLE_PASSAGE))
        impassable_to_animal.properties.append(models.EntityTypeProperty(P.INVISIBLE_PASSAGE))

        mare_type.properties.append(models.EntityTypeProperty(P.MOBILE, {"speed": 20}))
        mare_type.properties.append(models.EntityTypeProperty(P.CONTROLLING_MOVEMENT))

        db.session.add_all([pork_type, horsemeat_type, pig_type, mare_type,
                            impassable_to_animal, invisible_to_animal, dead_animal_group])

        rl = models.RootLocation.query.filter_by(position=from_shape(Point(1, 1))).first()
        impassable_to_animal = models.PassageType.by_name("impassable_to_animal")
        invisible_to_animal = models.PassageType.by_name("invisible_to_animal")
        pig = models.Location(rl, pig_type, passage_type=impassable_to_animal)
        pig.properties.append(models.EntityProperty(P.ANIMAL, {
            "resources": {
                pork_type.name: 30,
            },
        }))
        pig.properties.append(models.EntityProperty(P.DOMESTICATED, {
            "trusted": {},
            "resources_increase": {
                "fatness": 5,
            }
        }))
        mare = models.Location(rl, mare_type, passage_type=invisible_to_animal)
        mare.properties.append(models.EntityProperty(P.ANIMAL, {
            "resources": {
                horsemeat_type.name: 20
            }
        }))
        mare.properties.append(models.EntityProperty(P.DOMESTICATED, {
            "trusted": {},
            "resources_increase": {
                "fatness": 5,
            }
        }))

        db.session.add_all([pig, mare])

        stone_group = models.TypeGroup("group_stone", stackable=True)
        granite_type = models.ItemType("granite", 20, stackable=True)
        sandstone_type = models.ItemType("sandstone", 10, stackable=True)
        marble_type = models.ItemType("marble", 30, stackable=True)
        stone_group.add_to_group(granite_type, efficiency=1.5)
        stone_group.add_to_group(sandstone_type, efficiency=1.0)
        stone_group.add_to_group(marble_type, efficiency=2.0)

        rl = models.RootLocation.query.one()
        granite_pile = models.Item(granite_type, rl, amount=1000)
        sandstone_pile = models.Item(sandstone_type, rl, amount=1000)
        marble_pile = models.Item(marble_type, rl, amount=1000)

        db.session.add_all(
            [stone_group, granite_type, sandstone_type, marble_type, granite_pile, sandstone_pile, marble_pile])

        dead_body_type = models.EntityType.by_name(Types.DEAD_CHARACTER)
        dead_body_type.properties.append(models.EntityTypeProperty(P.BURYABLE))

        milk_type = models.ItemType("milk", 20, stackable=True)
        cow_skull_type = models.ItemType("cow_skull", 50, stackable=True)
        beef_type = models.ItemType("beef", 40, stackable=True)
        dead_cow_type = models.LocationType("dead_cow", 3000)
        dead_animal_group.add_to_group(dead_cow_type)
        cow_type = models.LocationType("cow", 3000)
        cow_type.properties.append(models.EntityTypeProperty(P.STATES, {
            main.States.HUNGER: {"initial": 0},
        }))
        cow_type.properties.append(models.EntityTypeProperty(P.ANIMAL, {
            "dead_type": dead_cow_type.name,
            "type_resources": {
                milk_type.name: {
                    "initial": 0,
                    "max": 30,
                },
                beef_type.name: {
                    "initial": 40,
                    "max": 80,
                },
                cow_skull_type.name: {
                    "initial": 1,
                    "max": 1,
                },
            }
        }))
        cow_type.properties.append(models.EntityTypeProperty(P.DOMESTICATED, {
            "type_resources_increase": {
                "milkiness": {
                    "initial": 0,
                    "affected_resources": {
                        "milk": 0.1,
                    },
                },
                "fatness": {
                    "initial": 0,
                    "affected_resources": {
                        "beef": 0.1,
                    },
                }
            }
        }))
        cow_type.properties.append(models.EntityTypeProperty(P.TAMABLE))

        grass_type = models.ItemType("grass", 100, stackable=True)
        grass_type.properties.append(models.EntityTypeProperty(P.EDIBLE_BY_ANIMAL, {
            "eater_types": ["herbivore"],
            "terrain_types": ["grassland"],
            "states": {
                main.States.HUNGER: -0.5,
            },
        }))

        grass_meadow = models.ItemType("grass_meadow", 0, portable=False)
        grass_area = models.ResourceArea(grass_type, Point(5, 5), 8, 20, 500)
        cutting_grass_result = [["exeris.core.actions.CollectGatheredResourcesAction", {"resource_type": "grass"}]]
        cutting_grass_recipe = models.EntityRecipe("cutting_grass", {},
                                                   {"required_resources": ["grass"], "terrain_types": ["grassland"],
                                                    "location_types": ["outside"]},
                                                   6, gathering_build_menu_category,
                                                   result=cutting_grass_result, activity_container="grass_meadow")

        herbivore_group = models.TypeGroup("herbivore")
        herbivore_group.add_to_group(cow_type)
        milkable_group = models.TypeGroup("milkable_animal")
        milkable_group.add_to_group(cow_type)
        rl = models.RootLocation.query.filter_by(position=from_shape(Point(1, 1))).one()
        impassable_to_animal = models.PassageType.by_name("impassable_to_animal")
        cow = models.Location(rl, cow_type, passage_type=impassable_to_animal)
        cow.properties.append(models.EntityProperty(P.ANIMAL, {
            "resources": {
                "milk": 0,
                "beef": 40,
                "cow_skull": 1,
            }
        }))
        cow.properties.append(models.EntityProperty(P.DOMESTICATED, {
            "trusted": {},
            "resources_increase": {
                "milkiness": 5,
                "fatness": 1,
            },
        }))

        domestication_build_menu_category = models.BuildMenuCategory("domestication")
        milking_cow_result = [["exeris.core.actions.CollectResourcesFromDomesticatedAnimalAction",
                               {"state_name": "milk"}]]
        milking_cow_recipe = models.EntityRecipe("milking_animal", {},
                                                 {"mandatory_machines": ["milkable_animal"]},
                                                 10, domestication_build_menu_category,
                                                 result=milking_cow_result, activity_container="selected_machine")

        db.session.add_all(
            [milk_type, cow_skull_type, beef_type, dead_cow_type, cow_type, milkable_group, rl,
             cow, milking_cow_recipe, grass_type, herbivore_group, grass_area, grass_meadow, cutting_grass_recipe])

        dead_aurochs_type = models.LocationType("dead_aurochs", 3000)
        dead_animal_group.add_to_group(dead_aurochs_type)
        female_aurochs_type = models.LocationType("female_aurochs", 3000)
        female_aurochs_type.properties.append(models.EntityTypeProperty(P.ANIMAL, {
            "dead_type": dead_aurochs_type.name,
            "type_resources": {
                beef_type.name: {
                    "initial": 40,
                    "max": 40,
                },
                cow_skull_type.name: {
                    "initial": 1,
                    "max": 1,
                },
            }
        }))
        female_aurochs_type.properties.append(models.EntityTypeProperty(P.TAMABLE, {
            "domesticated_type": cow_type.name,
        }))

        female_aurochs1 = models.Location(rl, female_aurochs_type, passage_type=impassable_to_animal)
        female_aurochs1.properties.append(models.EntityProperty(P.ANIMAL, {
            "resources": {
                beef_type.name: 40,
                cow_skull_type.name: 1,
            }
        }))
        female_aurochs2 = models.Location(rl, female_aurochs_type, passage_type=impassable_to_animal)
        female_aurochs2.properties.append(models.EntityProperty(P.ANIMAL, {
            "resources": {
                beef_type.name: 40,
                cow_skull_type.name: 1,
            }
        }))
        female_aurochs3 = models.Location(rl, female_aurochs_type, passage_type=impassable_to_animal)
        female_aurochs3.properties.append(models.EntityProperty(P.ANIMAL, {
            "resources": {
                beef_type.name: 40,
                cow_skull_type.name: 1,
            }
        }))

        db.session.add_all([dead_aurochs_type, female_aurochs_type, female_aurochs1, female_aurochs2, female_aurochs3])

        chest_type = models.ItemType("oak_chest", 300, portable=False)
        chest_recipe = models.EntityRecipe("building_chest", {}, {"input": {"oak": 5}}, 2,
                                           build_menu_category, result_entity=chest_type,
                                           activity_container="fixed_item")
        chest_type.properties.append(models.EntityTypeProperty(P.STORAGE, {"can_store": True}))
        db.session.add_all([chest_type, chest_recipe])

        butchering_recipe = models.EntityRecipe("butchering_animal", {},
                                                {"mandatory_machines": ["dead_animal"]}, 5,
                                                build_menu_category,
                                                result=[["exeris.core.actions.ButcherAnimalAction", {}
                                                         ]],
                                                activity_container="selected_machine")
        db.session.add(butchering_recipe)

        door_type = models.PassageType.by_name(Types.DOOR)
        door_type.properties.append(models.EntityTypeProperty(P.LOCKABLE, {"lock_exists": False}))
        key_type = models.ItemType("key", 20)

        building_lock_recipe = models.EntityRecipe("building_lock", {},
                                                   {"mandatory_machines": [Types.DOOR]}, 5,
                                                   build_menu_category,
                                                   result=[["exeris.core.actions.CreateLockAndKeyAction",
                                                            {"key_type": key_type.name,
                                                             "visible_material_of_key": {}}
                                                            ]],
                                                   activity_container="selected_machine")
        db.session.add_all([key_type, building_lock_recipe])

    if app.config["DEBUG"] and not models.Player.query.count():
        new_plr = models.Player("jan", "jan@gmail.com", "en", "test")
        db.session.add(new_plr)

        character = models.Character("test", models.Character.SEX_MALE, models.Player.query.get("jan"), "en",
                                     general.GameDate(0), Point(1, 1), models.RootLocation.query.one())
        db.session.add(character)

    from exeris.translations import data
    for tag_key in data:
        for language in data[tag_key]:
            db.session.merge(models.TranslatedText(tag_key, language, data[tag_key][language]))
    db.session.commit()


@outer_bp.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('language', "en")


@outer_bp.url_value_preprocessor
def outer_preprocessor(endpoint, values):
    g.language = values.pop('language', "en")
    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"))


@player_bp.before_request
def player_before_request():
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    g.player = current_user
    g.language = g.player.language
    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"))


@character_bp.url_value_preprocessor
def character_preprocessor(endpoint, values):
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    character_id = values.pop('character_id')
    g.player = current_user
    g.character = models.Character.by_id(character_id)
    g.language = g.character.language
    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"),
                               character=g.character)


class SocketioUsers:
    def __init__(self):
        # redis_db.flushdb()
        pass

    def get_all_by_player_id(self, player_id):
        result_from_redis = redis_db.smembers("sid_by_player_id:" + str(player_id))
        return [result.decode('utf-8') for result in result_from_redis]

    def get_all_by_character_id(self, character_id):
        result_from_redis = redis_db.smembers("sid_by_character_id:" + str(character_id))

        return [result.decode('utf-8') for result in result_from_redis]

    def add_for_player_id(self, sid, player_id):
        redis_db.sadd("sid_by_player_id:" + str(player_id), sid)

    def add_for_character_id(self, sid, character_id):
        redis_db.sadd("sid_by_character_id:" + str(character_id), sid)

    def remove_sid(self, sid):
        player_id_sets = redis_db.keys("sid_by_player_id:*")
        for player_id_set_name in player_id_sets:
            redis_db.srem(player_id_set_name, sid)

        character_id_sets = redis_db.keys("sid_by_character_id:*")
        for character_id_set_name in character_id_sets:
            redis_db.srem(character_id_set_name, sid)

    def remove_for_player_id(self, player_id):
        redis_db.delete("sid_by_player_id:" + str(player_id))

    def remove_for_character_id(self, character_id):
        redis_db.delete("sid_by_character_id:" + str(character_id))


socketio_users = SocketioUsers()


@socketio.on("connect")
def on_connect():
    character_id = request.args.get("character_id", None)
    character_id = int(character_id) if character_id else 0

    if current_user.is_authenticated:
        socketio_users.add_for_player_id(request.sid, current_user.id)
        character = models.Character.by_id(character_id)
        if character and character.player == current_user and character.is_alive:
            socketio_users.add_for_character_id(request.sid, character_id)


@socketio.on("disconnect")
def on_disconnect():
    socketio_users.remove_sid(request.sid)


@socketio.on_error()
def error_handler(exception):
    if isinstance(exception, main.GameException):
        client_socket.emit("global.show_error", g.pyslate.t(exception.error_tag, **exception.error_kwargs))
    else:
        client_socket.emit("global.show_error", "socketio error for " + str(request.event) + ": " + str(exception))
    if isinstance(exception, main.MalformedInputErrorMixin) or not isinstance(exception, main.GameException):
        logger.exception(exception)
    return False,


@app.errorhandler(Exception)
def handle_error(exception):
    if isinstance(exception, main.GameException):
        return g.pyslate.t(exception.error_tag, **exception.error_kwargs)
    logger.exception(exception)
    return traceback.print_tb(exception.__traceback__), 404


app.register_blueprint(outer_bp)
app.register_blueprint(player_bp)
app.register_blueprint(character_bp)
app.register_blueprint(character_static)

app.jinja_env.globals.update(t=lambda *args, **kwargs: g.pyslate.t(*args, **kwargs))
app.jinja_env.globals.update(encode=main.encode)
app.jinja_env.globals.update(decode=main.decode)
app.jinja_env.globals.update(debug_dict=lambda data_dict: {k: round(v, 2) if type(v) is float else v
                                                           for (k, v) in data_dict.items()})
