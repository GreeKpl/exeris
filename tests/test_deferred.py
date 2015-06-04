from flask.ext.testing import TestCase
from exeris.core import deferred
from tests import util

__author__ = 'alek'


def some_method(a, b):
    return a + b


class DeferredTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_terrain_representation(self):

        serialized_call = deferred.dumps(some_method, 5, 7)
        self.assertEqual(12, deferred.call(serialized_call))

        serialized_call = deferred.dumps(some_method, 11, 7)
        self.assertEqual(18, deferred.call(serialized_call))

    tearDown = util.tear_down_rollback