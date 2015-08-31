import traceback

from flask import g, render_template

from exeris.core import models
from exeris.player import player_bp, sijax


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
