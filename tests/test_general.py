import unittest
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import time
from unittest.mock import patch
from flask.ext.testing import TestCase

from exeris.core.main import GameDate, db
from exeris.core.models import GameDateCheckpoint
from tests.util import set_up_app_with_database


class GameDateTest(TestCase):

    create_app = set_up_app_with_database

    def test_basic(self):
        last_checkpoint_timestamp = 1000
        checkpoint = GameDateCheckpoint(game_date=100, real_date=last_checkpoint_timestamp)
        db.session.add(checkpoint)
        with patch("exeris.core.main.GameDate._get_timestamp", new=lambda: 1100):
            now = GameDate.now()
            self.assertAlmostEqual(200, now.game_timestamp)  # non-deterministic in a slow environment!!!

    def test_params(self):
        date = GameDate(3600 * 48 * 14 * 5 + 3600 * 48 * 3 + 3600 * 30 + 60 * 17 + 33)
        # 5-3-11:17:33
        self.assertEqual(33, date.second)
        self.assertEqual(17, date.minute)
        self.assertEqual(30, date.hour)
        self.assertEqual(3, date.sol)
        self.assertEqual(5, date.moon)

        self.assertAlmostEqual(0.631, date.sol_progression, places=3)
        self.assertAlmostEqual(0.25936, date.moon_progression, places=3)

        # check if it's night
        self.assertTrue(date.after_twilight)

    def test_comparisons(self):
        old = GameDate(1000)
        new = GameDate(1100)
        like_old = GameDate(1000)

        self.assertTrue(old < new)
        self.assertTrue(old <= new)
        self.assertFalse(old > new)
        self.assertFalse(old >= new)
        self.assertFalse(old == new)
        self.assertTrue(old != new)

        self.assertTrue(old == like_old)
        self.assertFalse(old != like_old)

    def tearDown(self):
        db.session.rollback()
