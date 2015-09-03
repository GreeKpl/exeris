from flask.ext.testing import TestCase
from shapely.geometry import Point

from exeris.core.main import db
from exeris.core.models import RootLocation, LocationType, Location, EntityTypeProperty, ObservedName, Character, \
    SkillType, EntityProperty
from exeris.core.properties import SkillsPropertyType
from exeris.core.properties_base import P
from exeris.core import properties
from tests import util

__author__ = 'alek'


class PassageTest(TestCase):
    create_app = util.set_up_app_with_database

    def test_set_and_alter_dynamic_name_success(self):
        rl = RootLocation(Point(1, 1), True, 123)
        building_type = LocationType("building", 1000)
        building = Location(rl, building_type)

        doer = util.create_character("doer", rl, util.create_player("ABC"))

        # make BUILDING nameable
        type_prop = EntityTypeProperty(P.DYNAMIC_NAMEABLE)
        building_type.properties.append(type_prop)

        db.session.add_all([rl, building_type, building, type_prop])

        # use method taken from property
        building.set_dynamic_name(doer, "Krakow")

        # check if name is really changed
        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Krakow", new_name.name)

        # change the existing name
        building.set_dynamic_name(doer, "Wroclaw")

        new_name = ObservedName.query.filter_by(observer=doer, target=building).one()
        self.assertEqual("Wroclaw", new_name.name)

    def test_get_and_alter_skill_success(self):

        rl = RootLocation(Point(1, 1), False, 111)
        char = util.create_character("ABC", rl, util.create_player("wololo"))

        char.properties.append(EntityProperty(P.SKILLS, {}))

        db.session.add_all([rl, SkillType("baking", "cooking"),
                            SkillType("frying", "cooking")])
        db.session.flush()

        self.assertAlmostEqual(0.1, char.get_raw_skill("baking"))

        char.alter_skill_by("frying", 0.2)  # 0.1 changed by 0.2 means 0.3 frying

        self.assertAlmostEqual(0.1, char.get_raw_skill("baking"))
        self.assertAlmostEqual(0.3, char.get_raw_skill("frying"))

        self.assertAlmostEqual(0.2, char.get_skill("frying"))  # mean value of 0.1 cooking and 0.3 frying = 0.2

    tearDown = util.tear_down_rollback

