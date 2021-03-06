import datetime

from exeris.core import general
from exeris.core.main import create_app, db
from exeris.core.models import Player, Character, GameDateCheckpoint, init_database_contents
from shapely.geometry import Point


def set_up_app_with_database(self):
    global db
    app = create_app(own_config_file_path="config/test_config.py", database=db)
    with app.app_context():
        db.create_all()

        init_database_contents()
        db.session.commit()

    return app


def tear_down_rollback(self):
    db.session.rollback()


def create_player(player_id, save=True):
    plr = Player(id=player_id, email=player_id + "aa@gmail.com", language="en", register_date=datetime.datetime.now(),
                 register_game_date=general.GameDate(1000), password="ala123")
    if save:
        db.session.add(plr)
    return plr


def create_character(name, being_in, player, save=True, sex=Character.SEX_MALE):
    char = Character(name, sex, player, "en", general.GameDate(1200), Point(10, 20), being_in)
    if save:
        db.session.add(char)
    return char


def initialize_date():
    checkpoint = GameDateCheckpoint(game_date=2000, real_date=datetime.datetime.now().timestamp())
    db.session.add(checkpoint)
