from flask import Blueprint

outer_bp = Blueprint('outer',
                     __name__,
                     template_folder='templates',
                     static_folder="static",
                     url_prefix="")

import exeris.outer.views
