from functools import wraps
import traceback
import types
import datetime
import time

from flask import Blueprint, g, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import current_user
from flask.ext.security import login_required, SQLAlchemyUserDatastore, Security, RegisterForm
from flask.ext.security.forms import Required
import psycopg2
from shapely.geometry import Point
import flask_sijax
from wtforms import StringField

from exeris.core import general, actions, models
from exeris.core.i18n import create_pyslate
from exeris.core.main import app, create_app, db, Types
from exeris.core.properties_base import P
from pyslate.backends import postgres_backend

app = create_app()

outer_bp = Blueprint('outer', "exeris", template_folder='templates', url_prefix="")
player_bp = Blueprint("player", "exeris", template_folder="templates", url_prefix="/player")
character_bp = Blueprint('character', "exeris", template_folder='templates', url_prefix="/character/<character_id>")

Bootstrap(app)
flask_sijax.Sijax(app)


class ExtendedRegisterForm(RegisterForm):
    id = StringField('login', [Required()])


user_datastore = SQLAlchemyUserDatastore(db, models.Player, models.Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)


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

    t = models.EntityType.by_name(Types.CHARACTER)
    if not models.EntityTypeProperty.query.filter_by(type=t, name=P.DYNAMIC_NAMEABLE).count():
        t.properties.append(models.EntityTypeProperty(t, P.DYNAMIC_NAMEABLE))

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


def with_sijax_route(*args, **kwargs):
    flask_fun = flask_sijax.route(*args, **kwargs)

    def dec(f):
        @wraps(f)
        def g(*a, **k):
            return f(*a, **k)

        return flask_fun(login_required(g))
    return dec


# monkey patching to make the decorator more comfortable to use
outer_bp.with_sijax_route = types.MethodType(with_sijax_route, outer_bp)
player_bp.with_sijax_route = types.MethodType(with_sijax_route, player_bp)
character_bp.with_sijax_route = types.MethodType(with_sijax_route, character_bp)


@player_bp.with_sijax_route("/")
def page_player():

    class SijaxActions:

        @staticmethod
        def create_character(obj_response, char_name):

            loc = models.RootLocation.query.one()
            new_char = models.Character(char_name, models.Character.SEX_FEMALE, g.player, "en",
                                        general.GameDate.now(), Point(1, 1), loc)
            db.session.add(new_char)
            db.session.commit()

            #obj_response.call("EVENTS.update_events", [new_events, last_event_id])

    try:
        if g.sijax.is_sijax_request:
            g.sijax.register_object(SijaxActions)
            return g.sijax.process_request()

        chars = models.Character.query.filter_by(player=g.player).all()
        return render_template("page_player.html", chars=chars)
    except Exception:
        print(traceback.format_exc())


@character_bp.with_sijax_route('/events')
def page_events():

    class EventsSijax:

        @staticmethod
        def update_events(obj_response, last_event):
            start = time.time()
            events = db.session.query(models.Event).join(models.EventObserver).filter_by(observer=g.character)\
                .filter(models.Event.id > last_event).order_by(models.Event.id.asc()).all()

            queried = time.time()
            print("query: ", queried - start)
            last_event_id = events[-1].id if len(events) else last_event
            events_texts = [g.pyslate.t(event.type_name, html=True, **event.params) for event in events]

            tran = time.time()
            print("translations:", tran - queried)
            events_texts = [event for event in events_texts]
            all = time.time()
            print("esc: ", all - tran)
            obj_response.call("FRAGMENTS.events.update_list", [events_texts, last_event_id])

        @staticmethod
        def say_aloud(obj_response, message):

            action = actions.SayAloudAction(g.character, message)
            action.perform()

            db.session.commit()

            obj_response.call("EVENTS.trigger", ["events:refresh_list"])

        @staticmethod
        def speak_to_somebody(obj_response, receiver_id, message):

            action = actions.SpeakToSomebody(g.character, receiver_id, message)
            action.perform()

            db.session.commit()

            obj_response.call("EVENTS.trigger", ["events:refresh_list"])

        @staticmethod
        def people_list_small_refresh(obj_response):
            chars = models.Character.query.all()
            rendered = render_template("fragments/people_list_small.html", chars=chars)

            obj_response.call("FRAGMENTS.people_list_small.build", [rendered])

        @staticmethod
        def rename_entity(obj_response, character_id, new_name):
            entity_to_rename = models.Entity.by_id(character_id)
            entity_to_rename.set_dynamic_name(g.character, new_name)
            db.session.commit()

            obj_response.call("EVENTS.trigger", ["people_list_small:refresh_list"])

    try:
        if g.sijax.is_sijax_request:
            g.sijax.register_object(EventsSijax)
            return g.sijax.process_request()

        return render_template("page_events.html")
    except Exception:
        print(traceback.format_exc())


@character_bp.with_sijax_route('/entities')
def page_entities():
    pass


@character_bp.with_sijax_route('/map')
def page_map():
    pass


@character_bp.with_sijax_route('/actions')
def page_actions():
    pass


@outer_bp.route("/")
def nic():
    return "OUTER PAGE"

app.register_blueprint(outer_bp)
app.register_blueprint(player_bp)
app.register_blueprint(character_bp)

app.jinja_env.globals.update(t=lambda *args, **kwargs: g.pyslate.t(*args, **kwargs))
