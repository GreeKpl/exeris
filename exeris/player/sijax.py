from flask import g
from shapely.geometry import Point
from exeris.core import general, models
from exeris.core.main import db


class PlayerPage:

        @staticmethod
        def create_character(obj_response, char_name):

            loc = models.RootLocation.query.one()
            new_char = models.Character(char_name, models.Character.SEX_FEMALE, g.player, "en",
                                        general.GameDate.now(), Point(1, 1), loc)
            db.session.add(new_char)
            db.session.commit()

            obj_response.call("FRAGMENTS.player.after_create_character", [])

