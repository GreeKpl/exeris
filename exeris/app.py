import datetime
import traceback

import flask_socketio as client_socket
import psycopg2
from exeris.core import models, main, general
from exeris.core.i18n import create_pyslate
from exeris.core.main import create_app, db, Types
from exeris.core.properties_base import P
from flask import g, request
from flask.ext.bootstrap import Bootstrap
from flask.ext.bower import Bower
from flask.ext.login import current_user
from flask.ext.security import SQLAlchemyUserDatastore, Security, RegisterForm
from flask.ext.security.forms import Required
from flask.ext.socketio import SocketIO
from functools import wraps
from geoalchemy2.shape import from_shape
from pyslate.backends import postgres_backend
from shapely.geometry import Point, Polygon
from wtforms import StringField, SelectField

# noinspection PyUnresolvedReferences
from exeris.core import achievements

app = create_app()

Bootstrap(app)
socketio = SocketIO(app)
Bower(app)


class ExtendedRegisterForm(RegisterForm):
    id = StringField('login', [Required()])
    language = SelectField('language', [Required()], choices=[("en", "English")])


user_datastore = SQLAlchemyUserDatastore(db, models.Player, models.Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)


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
            if not current_user.is_authenticated():
                print("DISCONNECTED UNWANTED USER")
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
            if not current_user.is_authenticated():
                print("DISCONNECTED UNWANTED USER")
                client_socket.disconnect()
            character_id = request.args.get("character_id")
            g.player = current_user
            g.character = models.Character.by_id(character_id)
            g.language = g.character.language
            conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
            g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"),
                                       character=g.character)
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

        new_plr = models.Player("jan", "jan@gmail.com", "en", "test")
        db.session.add(new_plr)

        character_type = models.EntityType.by_name(Types.ALIVE_CHARACTER)

        character_type.properties.append(models.EntityTypeProperty(P.DYNAMIC_NAMEABLE))

        hammer_type = models.ItemType("hammer", 200)
        hammer = models.Item(hammer_type, models.RootLocation.query.one())

        potatoes_type = models.ItemType("potatoes", 20, stackable=True)
        potatoes = models.Item(potatoes_type, models.RootLocation.query.one(), amount=5000)
        signpost_type = models.ItemType("signpost", 500, portable=False)
        db.session.add_all([potatoes_type, potatoes, signpost_type, hammer])

        potatoes_type = models.EntityType.query.filter_by(name="potatoes").one()
        potatoes_type.properties.append(models.EntityTypeProperty(P.EDIBLE, {"hunger": -0.1, "satiation": 0.05}))

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

        character = models.Character("test", models.Character.SEX_MALE, models.Player.query.get("jan"), "en",
                                     general.GameDate(0), Point(1, 1), models.RootLocation.query.one())
        db.session.add(character)

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
        hut_recipe = models.EntityRecipe("building_hut", {}, {"input": {"group_stone": 5}, "permanence": True}, 3, build_menu_category,
                                         result=[["exeris.core.actions.CreateLocationAction",
                                                  {"location_type": hut_type.name, "properties": {},
                                                   "used_materials": "all",
                                                   "visible_material": {"main": "group_stone"}}],
                                                 ["exeris.core.actions.AddNameToEntityAction", {}]],
                                         activity_container="fixed_item")
        db.session.add_all([hut_type, hut_recipe])

        grass_terrain = models.TerrainType("grass")
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

        land_trav1 = models.PropertyArea(models.AREA_KIND_LAND_TRAVERSABILITY, 1, 1, poly_grass, grass)
        land_trav2 = models.PropertyArea(models.AREA_KIND_LAND_TRAVERSABILITY, 1, 1, poly_grass2, grass2)
        land_trav3 = models.PropertyArea(models.AREA_KIND_LAND_TRAVERSABILITY, 1, 1, poly_forest, forest)

        poly_road_trav = Polygon([(1.2, 0.8), (0.7, 1.3), (3.7, 4.3), (4.2, 3.8)])
        land_trav_road = models.PropertyArea(models.AREA_KIND_LAND_TRAVERSABILITY, 2, 2, poly_road_trav, road)

        visibility_poly = Polygon([(0, 0), (0, 50), (50, 50), (50, 0)])
        world_visibility = models.PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, visibility_poly, water)

        db.session.add_all(
            [grass_terrain, deep_water_terrain, road_terrain, grass, water, grass2, road, forest,
             land_trav1, land_trav2, land_trav3, land_trav_road, world_visibility])

        build_menu_category = models.BuildMenuCategory.query.filter_by(name="structures").one()
        tablet_type = models.ItemType("tablet", 100, portable=False)
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

        pig_type = models.LocationType("pig", 30000)
        horse_type = models.LocationType("horse", 200000)
        impassable_to_animal = models.PassageType("impassable_to_animal", True)
        invisible_to_animal = models.PassageType("invisible_to_animal", True)
        invisible_to_animal.properties.append(models.EntityTypeProperty(P.ENTERABLE))
        invisible_to_animal.properties.append(models.EntityTypeProperty(P.INVISIBLE_PASSAGE))
        impassable_to_animal.properties.append(models.EntityTypeProperty(P.INVISIBLE_PASSAGE))

        db.session.add_all([pig_type, horse_type, impassable_to_animal, invisible_to_animal])

        pig_type = models.LocationType.by_name("pig")
        horse_type = models.LocationType.by_name("horse")

        rl = models.RootLocation.query.filter_by(position=from_shape(Point(1, 1))).first()
        impassable_to_animal = models.PassageType.by_name("impassable_to_animal")
        invisible_to_animal = models.PassageType.by_name("invisible_to_animal")
        pig = models.Location(rl, pig_type, passage_type=impassable_to_animal)
        horse = models.Location(rl, horse_type, passage_type=invisible_to_animal)

        db.session.add_all([pig, horse])

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
    if not current_user.is_authenticated():
        return app.login_manager.unauthorized()
    g.player = current_user
    g.language = g.player.language
    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"))


@character_bp.url_value_preprocessor
def character_preprocessor(endpoint, values):
    if not current_user.is_authenticated():
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
        self.sid_by_player_id = {}
        self.sid_by_character_id = {}

    def get_all_by_player_id(self, player_id):
        return self.sid_by_player_id.get(player_id, [])

    def get_all_by_character_id(self, character_id):
        return self.sid_by_character_id.get(character_id, [])

    def add_for_player_id(self, sid, player_id):
        self.sid_by_player_id[player_id] = [sid] + self.sid_by_player_id.get(player_id, [])

    def add_for_character_id(self, sid, character_id):
        self.sid_by_character_id[character_id] = [sid] + self.sid_by_character_id.get(character_id, [])

    def remove_sid(self, sid):
        for player_id, users in self.sid_by_player_id.items():
            self.sid_by_player_id[player_id] = [x for x in users if x != sid]

        for character_id, users in self.sid_by_character_id.items():
            self.sid_by_player_id[character_id] = [x for x in users if x != sid]

    def remove_for_player_id(self, player_id):
        self.sid_by_player_id.pop(player_id, None)

    def remove_for_character_id(self, character_id):
        self.sid_by_character_id.pop(character_id, None)


socketio_users = SocketioUsers()


@socketio.on("connect")
def on_connect():
    character_id = request.args.get("character_id", None)
    character_id = int(character_id) if character_id else 0

    if current_user.is_authenticated():
        socketio_users.add_for_player_id(request.sid, current_user.id)
        character = models.Character.by_id(character_id)
        if character and character.player == current_user and character.is_alive:
            socketio_users.add_for_character_id(request.sid, character_id)


@socketio.on("disconnect")
def on_disconnect():
    socketio_users.remove_sid(request.sid)
    print("REMOVED", request.sid)


@socketio.on_error()
def error_handler(exception):
    if isinstance(exception, main.GameException):
        client_socket.emit("global.show_error", g.pyslate.t(exception.error_tag, **exception.error_kwargs))
    else:
        print(traceback.format_exc())
        client_socket.emit("global.show_error", "socketio error for " + str(request.event) + ": " + str(exception))
    return False,


@app.errorhandler(Exception)
def handle_error(exception):
    if isinstance(exception, main.GameException):
        return g.pyslate.t(exception.error_tag, **exception.error_kwargs)
    print(exception)
    print(traceback.print_tb(exception.__traceback__))
    return traceback.print_tb(exception.__traceback__), 404


app.register_blueprint(outer_bp)
app.register_blueprint(player_bp)
app.register_blueprint(character_bp)
app.register_blueprint(character_static)

app.jinja_env.globals.update(t=lambda *args, **kwargs: g.pyslate.t(*args, **kwargs))
app.jinja_env.globals.update(encode=main.encode)
app.jinja_env.globals.update(decode=main.decode)
