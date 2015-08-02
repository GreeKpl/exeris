from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core.main import db
from exeris.core.models import RootLocation, LocationType, Location, EntityTypeProperty, ObservedName
from exeris.core.properties_base import P
from exeris.core import properties
from tests import util

__author__ = 'alek'


class PassageTest(TestCase):
    create_app = util.set_up_app_with_database

    def test_set_dynamic_name(self):
        rl = RootLocation(Point(1, 1), True, 123)
        building_type = LocationType("building", 1000)
        building = Location(rl, building_type)

        doer = util.create_character("doer", rl, util.create_player("ABC"))

        # make BUILDING nameable
        prop = EntityTypeProperty(building_type, P.DYNAMIC_NAMEABLE)

        db.session.add_all([rl, building_type, building, prop])

        # use method taken from property
        building.set_dynamic_name(doer, "Krakow")

        # check if name is really changed
        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Krakow", new_name.name)

        # change the existing name
        building.set_dynamic_name(doer, "Wroclaw")

        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Wroclaw", new_name.name)

    tearDown = util.tear_down_rollback
