import os

_author__ = 'alek'


class Config:
    DEBUG = False
    TESTING = False
    LOGIN_DISABLED = False
    SQLALCHEMY_DATABASE_URI_BASE = "postgresql://postgres:root@localhost/"
    SQLALCHEMY_DATABASE_NAME = "exeris1"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_BASE + SQLALCHEMY_DATABASE_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOCKETIO_REDIS_DATABASE_URI = "redis://localhost:6379/1"
    REDIS_URL = "redis://localhost:6379/1"
    SECRET_KEY = "I LIKE POTATOES"
    STATIC_PATH = os.path.join('.', os.path.dirname(__file__))
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_DEFAULT_REMEMBER_ME = True
    ENABLE_SSO_FOR_DISCOURSE = False
    DISCOURSE_SSO_LOGIN_BACK_URL = ""
    DISCOURSE_SSO_SECRET = "CHOCOLATE IS NICE"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI_BASE = "postgresql://postgres:root@localhost/"
    SQLALCHEMY_DATABASE_NAME = "exeris_test"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_BASE + SQLALCHEMY_DATABASE_NAME
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = True
