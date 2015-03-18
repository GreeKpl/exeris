import sqlalchemy as sql

__author__ = 'alek'

from config import Config
from exeris2.core.models import Base

engine = sql.create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
