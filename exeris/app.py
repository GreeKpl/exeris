from functools import wraps
import datetime
import traceback
import hashlib

from Crypto.Cipher import AES

from flask import g
from flask.ext.bootstrap import Bootstrap
from flask.ext.bower import Bower
from flask.ext.login import current_user
from flask.ext.security import login_required, SQLAlchemyUserDatastore, Security, RegisterForm
from flask.ext.security.forms import Required
import psycopg2
from shapely.geometry import Point, Polygon
import flask_sijax
from wtforms import StringField, SelectField

from exeris.core import models, main, general
from exeris.core.i18n import create_pyslate
from exeris.core.main import app, create_app, db, Types
from exeris.core.properties_base import P
from pyslate.backends import postgres_backend

app = create_app()

Bootstrap(app)
flask_sijax.Sijax(app)

Bower(app)


class ExtendedRegisterForm(RegisterForm):
    id = StringField('login', [Required()])
    language = SelectField('language', [Required()], choices=[("en", "English")])


user_datastore = SQLAlchemyUserDatastore(db, models.Player, models.Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)


def with_sijax_route(*args, **kwargs):
    flask_fun = flask_sijax.route(*args, **kwargs)

    def dec(f):
        @wraps(f)
        def g(*a, **k):
            return f(*a, **k)

        return flask_fun(login_required(g))

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

    if not models.RootLocation.query.count():
        new_root = models.RootLocation(Point(1, 1), False, 123)
        db.session.add(new_root)
    if not models.GameDateCheckpoint.query.count():
        ch_pt = models.GameDateCheckpoint(game_date=0, real_date=datetime.datetime.now().timestamp())
        db.session.add(ch_pt)
    if not models.Player.query.count():
        new_plr = models.Player("jan", "jan@gmail.com", "en", "test")
        db.session.add(new_plr)

    character_type = models.EntityType.by_name(Types.CHARACTER)
    if not models.EntityTypeProperty.query.filter_by(type=character_type, name=P.DYNAMIC_NAMEABLE).count():
        character_type.properties.append(models.EntityTypeProperty(P.DYNAMIC_NAMEABLE))
    if models.ItemType.query.count() < 2:
        hammer_type = models.ItemType("hammer", 200)
        hammer = models.Item(hammer_type, models.RootLocation.query.one())

        potatoes_type = models.ItemType("potatoes", 20, stackable=True)
        potatoes = models.Item(potatoes_type, models.RootLocation.query.one(), amount=5000)
        signpost_type = models.ItemType("signpost", 500, portable=False)
        db.session.add_all([potatoes_type, potatoes, signpost_type])
    if not models.EntityTypeProperty.query.filter_by(name=P.EDIBLE).count():
        potatoes_type = models.EntityType.query.filter_by(name="potatoes").one()
        potatoes_type.properties.append(models.EntityTypeProperty(P.EDIBLE, {"hunger": -0.1, "satiation": 0.05}))

    if not models.Character.query.count():
        character = models.Character("test", models.Character.SEX_MALE, models.Player.query.get("jan"), "en",
                                     general.GameDate(0), Point(1, 1), models.RootLocation.query.one())
        db.session.add(character)

    if not models.ItemType.by_name("portable_item_in_constr"):
        item_in_construction_type = models.ItemType("portable_item_in_constr", 1, portable=True)
        db.session.add(item_in_construction_type)

    if not models.ItemType.by_name("fixed_item_in_constr"):
        item_in_construction_type = models.ItemType("fixed_item_in_constr", 1, portable=False)
        db.session.add(item_in_construction_type)

    if not models.EntityRecipe.query.count():
        build_menu_category = models.BuildMenuCategory("structures")
        recipe = models.EntityRecipe("building_signpost", {}, {}, 10, build_menu_category,
                                     result_entity=models.ItemType.by_name("signpost"))
        db.session.add_all([build_menu_category, recipe])

    if not models.LocationType.by_name("hut"):
        build_menu_category = models.BuildMenuCategory.query.filter_by(name="structures").one()
        hut_type = models.LocationType("hut", 500)
        hut_type.properties.append(models.EntityTypeProperty(P.ENTERABLE))
        recipe = models.EntityRecipe("building_hut", {}, {"input": {"group_stone": 5}}, 3, build_menu_category,
                                     result=[["exeris.core.actions.CreateLocationAction",
                                              {"location_type": hut_type.name, "properties": {}, "used_materials": "all",
                                               "visible_material": {"main": "group_stone"}}],
                                             ["exeris.core.actions.AddNameToEntityAction", {}]],
                                     activity_container="fixed_item")
        db.session.add_all([hut_type, recipe])

    if not models.TerrainArea.query.count():
        tt1 = models.TerrainType("grass")
        tt2 = models.TerrainType("water")
        road_type = models.TerrainType("road")
        db.session.add_all([tt1, tt2])

        poly1 = Polygon([(0, 0), (0, 2), (1, 2), (3, 1), (0, 0)])
        poly2 = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
        poly3 = Polygon([(1, 1), (5, 1), (5, 3), (3, 5), (1, 1)])
        poly4 = Polygon([(1, 1), (0.9, 1.1), (3.9, 4.1), (4, 4), (1, 1)])

        t1 = models.TerrainArea(poly1, tt1)
        t2 = models.TerrainArea(poly2, tt2, priority=0)
        t3 = models.TerrainArea(poly3, tt1)
        road = models.TerrainArea(poly4, road_type)

        db.session.add_all([t1, t2, t3, road])

    if not models.ItemType.by_name("tablet"):
        build_menu_category = models.BuildMenuCategory.query.filter_by(name="structures").one()
        tablet_type = models.ItemType("tablet", 100, portable=False)
        tablet_type.properties.append(models.EntityTypeProperty(P.READABLE,
                                                                data={"max_length": 300, "allowed_formats": [
                                                                    models.TextContent.FORMAT_MD]}))

        tablet_production_result = [["exeris.core.actions.CreateItemAction",
                                     {"item_type": tablet_type.name,
                                      "properties": {P.VISIBLE_MATERIAL: {"main": "clay"}},
                                      "used_materials": "all"}]]
        tablet_recipe = models.EntityRecipe("carving_tablet", {}, {}, 2, build_menu_category,
                                            result=tablet_production_result,
                                            activity_container="portable_item")
        db.session.add_all([tablet_type, tablet_recipe])

    outside = models.LocationType.by_name(Types.OUTSIDE)
    if not models.EntityTypeProperty.query.filter_by(type=outside, name=P.DYNAMIC_NAMEABLE).count():
        outside.properties.append(models.EntityTypeProperty(P.DYNAMIC_NAMEABLE))

    if not models.ItemType.by_name("granite"):
        stone_group = models.TypeGroup("group_stone")
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
                               context={"observer": g.character})


@app.errorhandler(Exception)
def handle_error(exception):
    def sijax_error_response(obj_response):
        try:
            if isinstance(exception, main.GameException):
                obj_response.call("$.publish",
                                  ["show_error", g.pyslate.t(exception.error_tag, **exception.error_kwargs)])
                return
        except:
            pass  # execute next line...
        fun_name = obj_response._sijax.requested_function
        obj_response.call("$.publish", ["show_error", "SIJAX error on " + fun_name + ": " + str(exception)])
        print(exception)
        print(traceback.print_tb(exception.__traceback__))

    if g.sijax.is_sijax_request:
        return g.sijax.execute_callback([], sijax_error_response)

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
