_author__ = 'alek'


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI_BASE = "postgresql://postgres:root@localhost/"
    SQLALCHEMY_DATABASE_NAME = "exeris111"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_BASE + SQLALCHEMY_DATABASE_NAME


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI_BASE = "postgresql://postgres:root@localhost/"
    SQLALCHEMY_DATABASE_NAME = "exeris_1"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_BASE + SQLALCHEMY_DATABASE_NAME
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_RECORD_QUERIES = True