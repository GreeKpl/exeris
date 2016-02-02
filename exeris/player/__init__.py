from flask import Blueprint

player_bp = Blueprint("player",
                      __name__,
                      template_folder="templates",
                      static_folder="static",
                      url_prefix="/player")

import exeris.player.views
