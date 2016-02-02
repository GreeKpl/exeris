import flask
# noinspection PyUnresolvedReferences
from exeris.character import character_bp, socketio_events
from exeris.core.graphics import get_map
from flask import render_template


@character_bp.route('/events')
def page_events():
    return render_template("events/page_events.html")


@character_bp.route('/entities')
def page_entities():
    return render_template("entities/page_entities.html")


@character_bp.route('/map')
def page_map():
    return render_template("map/page_map.html")


@character_bp.route('/actions')
def page_actions():

    return render_template("actions/page_actions.html")


@character_bp.route("/map_image")
def map_image():

    resp = flask.make_response(get_map())
    resp.content_type = "image/png"
    return resp
