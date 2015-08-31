import types
from flask import Blueprint
from exeris.app import with_sijax_route

player_bp = Blueprint("player", "exeris", template_folder="templates", url_prefix="/player")

# monkey patching to make the decorator more comfortable to use
player_bp.with_sijax_route = types.MethodType(with_sijax_route, player_bp)

import exeris.player.views
