from flask.ext.testing import TestCase
from tests import util

__author__ = 'alek'


class TranslationTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_resource_name(self):
        pass#Pyslate()

    tearDown = util.tear_down_rollback

