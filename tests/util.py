import datetime
from shapely.geometry import Point
from exeris.core.main import create_app, db
from exeris.core import general
from exeris.core.models import Player, Character, GameDateCheckpoint, init_database_contents

__author__ = 'alek'


def set_up_app_with_database(self):
    global db
    app = create_app(config_object_module="config.TestingConfig", database=db)
    with app.app_context():
        db.create_all()

        init_database_contents()
        db.session.commit()

    return app


def tear_down_rollback(self):
    db.session.rollback()


def create_player(login, save=True):
    plr = Player(login="jan", email="aa@gmail.com", register_date=datetime.datetime.now(),
                 register_game_date=general.GameDate(1000), sex=Player.SEX_MALE, password="ala123")
    if save:
        db.session.add(plr)
    return plr


def create_character(name, being_in, player, save=True):
    char = Character(name, Character.SEX_MALE, player, general.GameDate(1200), Point(10, 20), being_in)
    if save:
        db.session.add(char)
    return char


def initialize_date():
    checkpoint = GameDateCheckpoint(game_date=2000, real_date=datetime.datetime.now().timestamp())
    db.session.add(checkpoint)
