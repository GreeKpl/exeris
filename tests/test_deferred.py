from flask.ext.testing import TestCase
import pickle
from exeris.core import deferred
from tests import util

__author__ = 'alek'


def some_method(a, b):
    return a + b


def inc(a):
    return a + 1


class PassageTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_terrain_representation(self):

        serialized_call = deferred.dumps((some_method, 5, 7))
        self.assertEqual(12, deferred.call(serialized_call))

        serialized_call = deferred.dumps((some_method, inc(5), 7))
        self.assertEqual(13, deferred.call(serialized_call))

    tearDown = util.tear_down_rollback