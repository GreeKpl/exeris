import traceback
from flask import g, render_template
import flask

from exeris.character import sijax, character_bp
from exeris.core import models, main
from exeris.core.graphics import get_map

@character_bp.with_sijax_route('/events')
def page_events():

    if g.sijax.is_sijax_request:
        g.sijax.register_object(sijax.EventsPage)
        return g.sijax.process_request()

    return render_template("events/page_events.html")


@character_bp.with_sijax_route('/entities')
def page_entities():
    if g.sijax.is_sijax_request:
        g.sijax.register_object(sijax.EntitiesPage)
        return g.sijax.process_request()

    return render_template("entities/page_entities.html")


@character_bp.with_sijax_route('/map')
def page_map():
    return render_template("map/page_map.html")


@character_bp.with_sijax_route('/actions')
def page_actions():
    if g.sijax.is_sijax_request:
        g.sijax.register_object(sijax.ActionsPage)
        return g.sijax.process_request()

    return render_template("actions/page_actions.html")


@character_bp.route("/map_image")
def map_image():

    resp = flask.make_response(get_map())
    resp.content_type = "image/png"
    return resp
