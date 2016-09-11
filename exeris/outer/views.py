# noinspection PyUnresolvedReferences
from exeris.outer import outer_bp, socketio_events
from flask import render_template


@outer_bp.route("/")
def front_page():
    return render_template("front_page.html")
