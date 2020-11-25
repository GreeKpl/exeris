from flask import render_template
# noinspection PyUnresolvedReferences
from exeris.admin import admin_bp, socketio_events


@admin_bp.route("/", defaults={'path': ''})
@admin_bp.route("/<path:path>")
def page_player(path):
    return render_template("frontend/build/index.html")
