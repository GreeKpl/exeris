import os

# DO NOT EDIT!
# This is a default Exeris server configuration.
# You shouldn't modify it in any way, because it may cause troubles when upgrading.
# When you want to setup custom variables then create a new python file
# with config represented as module-level variables.
# An example file is testing_config.py
# To use config for the server you need to specify a config path (relative to the exeris root directory)
# in environment variable EXERIS_CONFIG_PATH


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
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = ""
    ENABLE_SSO_FOR_DISCOURSE = False
    DISCOURSE_SSO_SECRET = "CHOCOLATE IS NICE"
    ENABLE_CHARACTER_CREATION = True
    USE_RECAPTCHA_IN_FORMS = False
    RECAPTCHA_PUBLIC_KEY = ""
    RECAPTCHA_PRIVATE_KEY = ""
    DASHBOARD_ANNOUNCEMENT = None
    FRONT_PAGE_ANNOUNCEMENT = None
    MAIL_SERVER = "smtp.exeris.org"
    MAIL_PORT = 587
    MAIL_USERNAME = None
    MAIL_PASSWORD = None

    LOGGER_CONFIG_PATH = "exeris/config/default_logging_config.json"

    SECURITY_POST_LOGIN_VIEW = "/player"
    SECURITY_POST_REGISTER_VIEW = "/register"

    SECURITY_LOGIN_URL = "/users/sign_in"  # URL required by SSO for android mattermost app

    OAUTH2_CLIENTS = []
