import flask
# noinspection PyUnresolvedReferences
from exeris.character import character_bp, socketio_events
# noinspection PyUnresolvedReferences
from exeris.extra import hooks
from exeris.core.graphics import get_map
from flask import render_template, g


@character_bp.route("/", defaults={'path': ''})
@character_bp.route("/<path:path>")
def page_player(path):
    return render_template("front/dist/index.html")


@character_bp.route("/map_image")
def map_image():
    resp = flask.make_response(get_map(character=g.character))
    resp.content_type = "image/png"
    return resp
