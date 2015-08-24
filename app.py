from functools import wraps
import traceback
import types
import html
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

from exeris.core import general
from exeris.core import models
from exeris.core.i18n import create_pyslate
from exeris.core.main import app, create_app, db, Types
from pyslate.backends import postgres_backend
import translations

app = create_app()

outer_bp = Blueprint('outer', __name__, template_folder='templates', url_prefix="")
player_bp = Blueprint("player", __name__, template_folder="templates", url_prefix="/player")
character_bp = Blueprint('character', __name__, template_folder='templates', url_prefix="/character/<character_id>")

Bootstrap(app)
flask_sijax.Sijax(app)


class ExtendedRegisterForm(RegisterForm):
    id = StringField('login', [Required()])


user_datastore = SQLAlchemyUserDatastore(db, models.Player, models.Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)


@app.before_first_request
def create_database():
    db.create_all()
    if not models.RootLocation.query.count():
        outside_type = models.LocationType(Types.OUTSIDE, 100)
        db.session.add(outside_type)

        new_root = models.RootLocation(Point(1, 1), False, 123)
        db.session.add(new_root)
    if not models.GameDateCheckpoint.query.count():
        ch_pt = models.GameDateCheckpoint(game_date=0, real_date=datetime.datetime.now().timestamp())
        db.session.add(ch_pt)

    from translations import data
    for tag_key in data:
        for language in data[tag_key]:
            print("ADDING " + tag_key + " for " + language)
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
    g.pyslate = create_pyslate(g.language, backend=postgres_backend.PostgresBackend(conn, "translations"))


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
            print("DO IT!!!")
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

    class SijaxActions:

        @staticmethod
        def update_events(obj_response, newest_event):
            start = time.time()
            new_events = models.Event.filter(models.Event.id > newest_event)\
                .filter_by(observer_id=g.player.id).order_by(models.Event.id.asc()).all()

            queried = time.time()
            print("query: ", queried - start)
            last_event_id = new_events[-1].id if len(new_events) else newest_event
            new_events = [g.pyslate.t(event.type, gender=g.player.sex, **event.params) for event in new_events]

            tran = time.time()
            print("translations:", tran - queried)
            new_events = [html.escape(event) for event in new_events]
            all = time.time()
            print("esc: ", all - tran)
            obj_response.call("EVENTS.update_events", [new_events, last_event_id])

    try:
        if g.sijax.is_sijax_request:
            g.sijax.register_object(SijaxActions)
            return g.sijax.process_request()

        models.Character.query.all()
        return render_template("page_events.html")
    except Exception:
        print(traceback.format_exc())

@outer_bp.route("/")
def nic():
    return "HI"

app.register_blueprint(outer_bp)
app.register_blueprint(player_bp)
app.register_blueprint(character_bp)

app.jinja_env.globals.update(t=lambda *args, **kwargs: g.pyslate.t(*args, **kwargs))


if __name__ == '__main__':
    print(app.url_map)
    app.run()
