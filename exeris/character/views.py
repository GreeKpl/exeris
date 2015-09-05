import traceback
from flask import g, render_template

from exeris.character import sijax, character_bp
from exeris.core import models, main


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
    return "NOTHING"


@character_bp.with_sijax_route('/actions')
def page_actions():
    return "NOTHING"
