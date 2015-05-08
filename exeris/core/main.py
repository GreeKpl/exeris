from collections import deque
from enum import Enum

__author__ = 'aleksander chrabąszcz'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = None


def create_app(database=db, config_object_module="config.DevelopmentConfig"):
    global app
    app = Flask(__name__)
    app.config.from_object(config_object_module)
    database.init_app(app)
    return app

