from exeris.app import socketio_player_event
from flask import g, render_template

from exeris.core import models, actions
from exeris.core.main import db


@socketio_player_event("create_character")
def create_character(char_name):

    create_character_action = actions.CreateCharacterAction(g.player, char_name, models.Character.SEX_MALE, "en")
    new_char = create_character_action.perform()
    db.session.commit()

    return ()


@socketio_player_event("player.update_top_bar")
def player_update_top_bar(character_id):

    rendered = render_template("player_top_bar.html", current_character_id=character_id)
    return rendered,


