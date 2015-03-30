from flask.ext.testing import TestCase
from exeris.core.main import db
from exeris.core.models import TerrainArea
from tests import util
from pygeoif.geometry import Polygon

__author__ = 'alek'


class PassageTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_terrain_representation(self):

        coords = ((0, 0), (2, 0), (3, 2), (1, 1), (0, 0))
        poly = Polygon(coords)
        area = TerrainArea(poly, poly, poly)

        db.session.add(area)

        a = TerrainArea.query.all()

        print("FINISH")


    tearDown = util.tear_down_rollback