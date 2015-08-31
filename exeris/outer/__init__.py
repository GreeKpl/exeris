import types
from flask import Blueprint
from exeris.app import with_sijax_route

outer_bp = Blueprint('outer',
                     __name__,
                     template_folder='templates',
                     url_prefix="")

# monkey patching to make the decorator more comfortable to use
outer_bp.with_sijax_route = types.MethodType(with_sijax_route, outer_bp)

import exeris.outer.views
