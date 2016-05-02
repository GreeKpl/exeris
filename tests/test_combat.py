from unittest.mock import patch

from flask.ext.testing import TestCase
from shapely.geometry import Point, Polygon

from exeris.core import main, combat, deferred, models
from exeris.core.actions import FightInCombatAction, CombatProcess
from exeris.core.main import db
from exeris.core.models import RootLocation, Combat, Intent, TerrainType, TerrainArea, PropertyArea, TypeGroup, \
    ItemType, \
    Item, EntityTypeProperty
from exeris.core.properties_base import P
from tests import util


class CombatTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def test_list_of_foes_in_proximity(self):
        rl_roman = RootLocation(Point(10, 10), 11)
        rl_gaul1 = RootLocation(Point(16, 10), 11)
        rl_gaul2 = RootLocation(Point(20, 10), 11)
        rl_gaul3 = RootLocation(Point(22, 10), 11)
        rl_gaul_on_a_ship = RootLocation(Point(8, 10), 11)
        db.session.add_all([rl_roman, rl_gaul1, rl_gaul2, rl_gaul3, rl_gaul_on_a_ship])

        grass_type = TerrainType("grass")
        shallow_water_type = TerrainType("shallow_water", travel_type=TerrainType.TRAVEL_WATER)
        TypeGroup.by_name(main.Types.LAND_TERRAIN).add_to_group(grass_type)
        TypeGroup.by_name(main.Types.WATER_TERRAIN).add_to_group(shallow_water_type)

        grass_poly = Polygon([(10, 5), (10, 15), (30, 15), (30, 5)])
        grass_terrain = TerrainArea(grass_poly, grass_type)
        grass_traversability_area = PropertyArea(models.AREA_KIND_LAND_TRAVERSABILITY, 1, 1, grass_poly, grass_terrain)
        grass_vis_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, grass_poly, grass_terrain)

        water_poly = Polygon([(0, 5), (0, 15), (10, 15), (10, 5)])
        water_terrain = TerrainArea(water_poly, shallow_water_type)
        water_traversability_area = PropertyArea(models.AREA_KIND_WATER_TRAVERSABILITY, 1, 1, water_poly, water_terrain)
        water_vis_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, water_poly, water_terrain)

        db.session.add_all([grass_type, grass_terrain, shallow_water_type, grass_traversability_area,
                            water_vis_area, water_traversability_area, grass_vis_area])

        roman1 = util.create_character("roman1", rl_roman, util.create_player("abc1"))
        roman2 = util.create_character("roman2", rl_roman, util.create_player("abc12"))
        roman3 = util.create_character("roman3", rl_roman, util.create_player("abc13"))

        gaul1 = util.create_character("gaul1", rl_gaul1, util.create_player("abc21"))
        gaul2 = util.create_character("gaul2", rl_gaul2, util.create_player("abc22"))
        gaul3 = util.create_character("gaul3", rl_gaul3, util.create_player("abc23"))
        gaul_on_a_ship = util.create_character("gaul_on_a_ship", rl_gaul_on_a_ship, util.create_player("abc24"))

        combat_entity = Combat()
        db.session.add(combat_entity)
        db.session.flush()

        ROMAN_SIDE = 1
        roman1_combat = Intent(roman1, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman1, combat_entity, ROMAN_SIDE,
                                                                      CombatProcess.STANCE_OFFENSIVE)))
        roman2_combat = Intent(roman2, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman2, combat_entity, ROMAN_SIDE,
                                                                      CombatProcess.STANCE_OFFENSIVE)))
        roman3_combat = Intent(roman3, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman3, combat_entity, ROMAN_SIDE,
                                                                      CombatProcess.STANCE_OFFENSIVE)))

        GAUL_SIDE = 0
        gaul1_combat = Intent(gaul1, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul1, combat_entity, GAUL_SIDE, CombatProcess.STANCE_OFFENSIVE)))
        gaul2_combat = Intent(gaul2, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul2, combat_entity, GAUL_SIDE, CombatProcess.STANCE_OFFENSIVE)))
        gaul3_combat = Intent(gaul3, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul3, combat_entity, GAUL_SIDE, CombatProcess.STANCE_OFFENSIVE)))
        gaul_on_a_ship_combat = Intent(gaul_on_a_ship, main.Intents.COMBAT, 1, combat_entity,
                                       deferred.serialize(
                                           FightInCombatAction(gaul_on_a_ship, combat_entity, GAUL_SIDE,
                                                               CombatProcess.STANCE_OFFENSIVE)))

        db.session.add_all([roman1_combat, roman2_combat, roman3_combat,
                            gaul1_combat, gaul2_combat, gaul3_combat, gaul_on_a_ship_combat])

        combat_potential_foes_actions = combat.get_combat_actions_of_foes_in_range(roman1, combat_entity)
        combat_potential_foes = [action.executor for action in combat_potential_foes_actions]
        self.assertCountEqual([gaul1, gaul2, gaul_on_a_ship], combat_potential_foes)

        with patch("exeris.core.combat._get_random", new=lambda x: x[0]):
            roman1_combat_action = deferred.call(roman1_combat.serialized_action)

            # everyone fighting melee
            foe_to_hit_action = combat.get_hit_target(roman1_combat_action, combat_potential_foes_actions)
            self.assertEqual(gaul1, foe_to_hit_action.executor)

            # gaul1 will use a ranged weapon
            bow_type = ItemType("bow", 200)
            bow_type.properties += [
                EntityTypeProperty(P.WEAPONIZABLE, {"ranged": True}),
                EntityTypeProperty(P.EQUIPPABLE, {"eq_part": main.EqParts.WEAPON}),
            ]

            bow_for_gaul1 = Item(bow_type, gaul1)
            bow_for_gaul2 = Item(bow_type, gaul2)
            db.session.add_all([bow_type, bow_for_gaul1, bow_for_gaul2])

            gaul1.set_preferred_equipment_part(bow_for_gaul1)
            foe_to_hit_action = combat.get_hit_target(roman1_combat_action, combat_potential_foes_actions)
            self.assertEqual(gaul2, foe_to_hit_action.executor)

            # gaul2 will also get a ranged weapon
            # now both traversibly accessible foes have ranged weapons, so both can be attacked
            gaul2.set_preferred_equipment_part(bow_for_gaul2)
            foe_to_hit_action = combat.get_hit_target(roman1_combat_action, combat_potential_foes_actions)
            self.assertEqual(gaul1, foe_to_hit_action.executor)

            # check only gaul on a ship, who is traversibly inaccessible
            gaul_on_a_ship_combat_action = deferred.call(gaul_on_a_ship_combat.serialized_action)
            foe_to_hit_action = combat.get_hit_target(roman1_combat_action, [gaul_on_a_ship_combat_action])
            self.assertIsNone(foe_to_hit_action)

            # equip attacker with a ranged weapon, so a gaul_on_a_ship can be hit
            bow_for_roman1 = Item(bow_type, roman1)
            db.session.add(bow_for_roman1)

            roman1.set_preferred_equipment_part(bow_for_roman1)

            foe_to_hit_action = combat.get_hit_target(roman1_combat_action, [gaul_on_a_ship_combat_action])
            self.assertEqual(gaul_on_a_ship_combat_action, foe_to_hit_action)

    def test_combat_process(self):
        util.initialize_date()
        rl = RootLocation(Point(1, 1), 100)

        roman1 = util.create_character("roman1", rl, util.create_player("abc1"))
        roman2 = util.create_character("roman2", rl, util.create_player("abc12"))

        gaul1 = util.create_character("gaul1", rl, util.create_player("abc21"))

        combat_entity = Combat()
        db.session.add(combat_entity)
        db.session.flush()

        ROMAN_SIDE = 1
        roman1_combat = Intent(roman1, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman1, combat_entity, ROMAN_SIDE,
                                                                      CombatProcess.STANCE_OFFENSIVE)))
        roman2_combat = Intent(roman2, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman2, combat_entity, ROMAN_SIDE,
                                                                      CombatProcess.STANCE_OFFENSIVE)))

        GAUL_SIDE = 0
        gaul1_combat = Intent(gaul1, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul1, combat_entity, GAUL_SIDE, CombatProcess.STANCE_DEFENSIVE)))

        db.session.add_all([roman1_combat, roman2_combat, gaul1_combat])

        with patch("exeris.core.actions.FightInCombatAction.calculate_hit_damage", new=lambda x, y: 0.1):
            combat_process = CombatProcess(combat_entity)
            combat_process.perform()

            # test if gaul is hit twice, each for 0.1
            self.assertAlmostEqual(0.2, gaul1.damage)

            # one of two romans should be hit
            self.assertAlmostEqual(0.1, roman1.damage + roman2.damage)

        CombatProcess.RETREAT_CHANCE = 1.0  # retreat is always successful
        with patch("exeris.core.actions.FightInCombatAction.calculate_hit_damage", new=lambda x, y: 0.01):

            roman1_combat_action = deferred.call(roman1_combat.serialized_action)
            roman1_combat_action.stance = CombatProcess.STANCE_RETREAT
            roman1_combat.serialized_action = deferred.serialize(roman1_combat_action)

            combat_process = CombatProcess(combat_entity)
            combat_process.perform()

            self.assertCountEqual([roman2_combat, gaul1_combat], Intent.query.all())

            gaul1_combat_action = deferred.call(gaul1_combat.serialized_action)
            gaul1_combat_action.stance = CombatProcess.STANCE_RETREAT
            gaul1_combat.serialized_action = deferred.serialize(gaul1_combat_action)

            combat_process = CombatProcess(combat_entity)
            combat_process.perform()

            self.assertEqual([], Intent.query.all())
            self.assertEqual(0, Combat.query.count())