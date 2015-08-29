from exeris.app import player_bp, character_bp, outer_bp

import traceback
import time

from flask import g, render_template
from shapely.geometry import Point

from exeris.core import general, actions, models
from exeris.core.main import db


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

            obj_response.call("EVENTS.trigger", ["refresh_entity", character_id])

        @staticmethod
        def get_entity_tag(obj_response, entity_id):
            entity = models.Entity.by_id(entity_id)
            text = g.pyslate.t("entity_info", html=True, **entity.pyslatize())
            obj_response.call("FRAGMENTS.global.alter_entity", [entity_id, text])

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
