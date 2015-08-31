import traceback
from flask import g, render_template

from exeris.character import sijax, character_bp


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
    return render_template("entities/page_entities.html")


@character_bp.with_sijax_route('/map')
def page_map():
    pass


@character_bp.with_sijax_route('/actions')
def page_actions():
    pass
