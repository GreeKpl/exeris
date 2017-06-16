from flask import Blueprint

admin_bp = Blueprint('admin',
                     __name__,
                     template_folder="./../../",
                     static_folder="static",
                     url_prefix="/admin")

from exeris.admin import views
