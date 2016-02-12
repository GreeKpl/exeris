from flask.ext.testing import TestCase
from shapely.geometry import Point

# noinspection PyUnresolvedReferences
import exeris.core.achievements
from exeris.core.actions import SayAloudAction
from exeris.core.main import db
from exeris.core.models import RootLocation, Achievement
from tests import util


class PassageTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_getting_speaker_achievement(self):
        util.initialize_date()

        rl = RootLocation(Point(1, 1), False, 123)
        player = util.create_player("elo")
        char = util.create_character("jan", rl, player)

        db.session.add_all([rl])

        for i in range(9):
            action = SayAloudAction(char, "Hej")
            action.perform()

        # too little to get achievement, requires speaking 10 times
        self.assertEqual(0, Achievement.query.filter_by(achiever=player, achievement="speaker").count())

        action = SayAloudAction(char, "Hej")
        action.perform()

        # now there should be achievement
        Achievement.query.filter_by(achiever=player, achievement="speaker").one()
