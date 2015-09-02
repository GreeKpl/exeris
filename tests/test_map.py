from flask.ext.testing import TestCase
from shapely.geometry import Polygon
from exeris.core.main import db
from exeris.core.models import TerrainArea, TerrainType
from tests import util

__author__ = 'alek'


class PassageTest(TestCase):

    create_app = util.set_up_app_with_database

    def test_terrain_representation(self):

        tt = TerrainType("grassland")
        db.session.add(tt)

        coords = ((0, 0), (2, 0), (3, 2), (1, 1), (0, 0))
        poly = Polygon(coords)
        area = TerrainArea(poly, tt)

        db.session.add(area)

        grassland_area = TerrainArea.query.one()

        self.assertEqual(1, grassland_area.priority)
        self.assertEqual(poly, grassland_area.terrain)

    tearDown = util.tear_down_rollback
