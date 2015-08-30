from exeris import sijax
from exeris.app import player_bp, character_bp, outer_bp

import traceback
import time

from flask import g, render_template
from shapely.geometry import Point

from exeris.core import general, actions, models
from exeris.core.main import db


@player_bp.with_sijax_route("/")
def page_player():

    try:
        if g.sijax.is_sijax_request:
            g.sijax.register_object(sijax.PlayerPage)
            return g.sijax.process_request()

        chars = models.Character.query.filter_by(player=g.player).all()
        return render_template("page_player.html", chars=chars, player=g.player)
    except Exception:
        print(traceback.format_exc())


@character_bp.with_sijax_route('/events')
def page_events():

    try:
        if g.sijax.is_sijax_request:
            g.sijax.register_object(sijax.EventsPage)
            return g.sijax.process_request()

        return render_template("events/page_events.html")
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
