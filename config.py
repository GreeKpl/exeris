import json
import os
from pyslate.backends import json_backend

_author__ = 'alek'


class Config:
    DEBUG = False
    TESTING = False
    LOGIN_DISABLED = False
    SQLALCHEMY_DATABASE_URI_BASE = "postgresql://postgres:root@localhost/"
    SQLALCHEMY_DATABASE_NAME = "exeris1"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_BASE + SQLALCHEMY_DATABASE_NAME
    SECRET_KEY = "I LIKE POTATOES"
    SIJAX_STATIC_PATH = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
    STATIC_PATH = os.path.join('.', os.path.dirname(__file__))
    SIJAX_JSON_URI = '/static/js/sijax/json2.js'
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    PYSLATE_BACKEND = ""


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI_BASE = "postgresql://postgres:root@localhost/"
    SQLALCHEMY_DATABASE_NAME = "exeris_test"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_BASE + SQLALCHEMY_DATABASE_NAME
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True