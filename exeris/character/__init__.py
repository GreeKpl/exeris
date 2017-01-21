from flask import Blueprint

character_bp = Blueprint('character',
                         __name__,
                         template_folder="./../../",
                         static_folder="static",
                         url_prefix="/character/<character_id>")

character_static = Blueprint('character_static',
                             __name__,
                             static_folder="static",
                             url_prefix="/character")

from exeris.character import views
