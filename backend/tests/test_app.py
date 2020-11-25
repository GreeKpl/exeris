from flask import g

from flask_testing import TestCase
from shapely.geometry import Point
from exeris.core import models, main

from tests import util


class EncoderTest(TestCase):
    create_app = util.set_up_app_with_database

    def setUp(self):
        rl = models.RootLocation(Point(1, 1), 111)
        pl = util.create_player('player1')
        self.character1 = util.create_character('char1', rl, pl)
        self.character2 = util.create_character('char2', rl, pl)
        str(self.character2)

    values = (0, 1, 2, 3, 10, 100, 1053218997898321983, 2 ** 63 - 4, 2 ** 64 - 3, 2 ** 64 - 1)

    def test_codec_match(self):
        g.character = self.character1
        for val in self.values:
            enc = main.encode(val)
            self.assertTrue(len(enc) > 0)
            self.assertTrue(enc.isdigit())
            self.assertEqual(main.decode(enc), val)

    def test_codec_no_match(self):
        g.character = self.character1
        encoded = [main.encode(i) for i in self.values]
        g.character = self.character2
        for val, enc in zip(self.values, encoded):
            self.assertRaises(ValueError, main.decode, enc)
            self.assertNotEqual(main.encode(val), enc)

    def test_codec_invalid(self):
        g.character = self.character1
        for val in self.values:
            enc = main.encode(val)
            self.assertRaises(ValueError, main.decode, str(int(enc) + 1))

    tearDown = util.tear_down_rollback
