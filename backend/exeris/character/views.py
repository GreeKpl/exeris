import flask
from flask import g

# noinspection PyUnresolvedReferences
from exeris.character import character_bp, socketio_events
from exeris.core.graphics import get_map
# noinspection PyUnresolvedReferences
from exeris.extra import hooks


@character_bp.route("/map_image")
def map_image():
    resp = flask.make_response(get_map(character=g.character))
    resp.content_type = "image/png"
    return resp
