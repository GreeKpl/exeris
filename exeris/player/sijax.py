from flask import g

from exeris.core import models, actions
from exeris.core.main import db


class PlayerPage:

        @staticmethod
        def create_character(obj_response, char_name):

            create_character_action = actions.CreateCharacterAction(g.player, char_name, models.Character.SEX_MALE, "en")
            new_char = create_character_action.perform()
            db.session.commit()

            obj_response.call("FRAGMENTS.player.after_create_character", [])

