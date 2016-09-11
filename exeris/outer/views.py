# noinspection PyUnresolvedReferences
from exeris.outer import outer_bp, socketio_events
from flask import render_template
from flask.ext.login import current_user


@outer_bp.route("/")
def front_page():
    return render_template("front_page.html", logged_in=current_user.is_authenticated())
