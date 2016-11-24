from unittest.mock import patch, MagicMock

from flask_testing import TestCase
from shapely.geometry import Point, Polygon

from exeris.core import main, combat, deferred, models
from exeris.core.actions import FightInCombatAction, CombatProcess, AttackCharacterAction, JoinCombatAction, \
    ChangeCombatStanceAction
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

        grass_type = TerrainType("grassland")
        shallow_water_type = TerrainType("shallow_water", travel_type=TerrainType.TRAVEL_WATER)
        TypeGroup.by_name(main.Types.LAND_TERRAIN).add_to_group(grass_type)
        TypeGroup.by_name(main.Types.WATER_TERRAIN).add_to_group(shallow_water_type)

        grass_poly = Polygon([(10, 5), (10, 15), (30, 15), (30, 5)])
        grass_terrain = TerrainArea(grass_poly, grass_type)
        grass_traversability_area = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, grass_poly, grass_terrain)
        grass_vis_area = PropertyArea(models.AREA_KIND_VISIBILITY, 1, 1, grass_poly, grass_terrain)

        water_poly = Polygon([(0, 5), (0, 15), (10, 15), (10, 5)])
        water_terrain = TerrainArea(water_poly, shallow_water_type)
        water_traversability_area = PropertyArea(models.AREA_KIND_TRAVERSABILITY, 1, 1, water_poly, water_terrain)
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
                                                                      combat.STANCE_OFFENSIVE)))
        roman2_combat = Intent(roman2, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman2, combat_entity, ROMAN_SIDE,
                                                                      combat.STANCE_OFFENSIVE)))
        roman3_combat = Intent(roman3, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman3, combat_entity, ROMAN_SIDE,
                                                                      combat.STANCE_OFFENSIVE)))

        GAUL_SIDE = 0
        gaul1_combat = Intent(gaul1, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul1, combat_entity, GAUL_SIDE, combat.STANCE_OFFENSIVE)))
        gaul2_combat = Intent(gaul2, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul2, combat_entity, GAUL_SIDE, combat.STANCE_OFFENSIVE)))
        gaul3_combat = Intent(gaul3, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul3, combat_entity, GAUL_SIDE, combat.STANCE_OFFENSIVE)))
        gaul_on_a_ship_combat = Intent(gaul_on_a_ship, main.Intents.COMBAT, 1, combat_entity,
                                       deferred.serialize(
                                           FightInCombatAction(gaul_on_a_ship, combat_entity, GAUL_SIDE,
                                                               combat.STANCE_OFFENSIVE)))

        db.session.add_all([roman1_combat, roman2_combat, roman3_combat,
                            gaul1_combat, gaul2_combat, gaul3_combat, gaul_on_a_ship_combat])

        combat_potential_foes_actions = combat.get_combat_actions_of_visible_foes(roman1, combat_entity)
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

        class TaskMock:
            pass

        roman1 = util.create_character("roman1", rl, util.create_player("abc1"))
        roman2 = util.create_character("roman2", rl, util.create_player("abc12"))

        gaul1 = util.create_character("gaul1", rl, util.create_player("abc21"))

        combat_entity = Combat()
        db.session.add(combat_entity)
        db.session.flush()

        ROMAN_SIDE = 1
        roman1_combat = Intent(roman1, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman1, combat_entity, ROMAN_SIDE,
                                                                      combat.STANCE_OFFENSIVE)))
        roman2_combat = Intent(roman2, main.Intents.COMBAT, 1, combat_entity,
                               deferred.serialize(FightInCombatAction(roman2, combat_entity, ROMAN_SIDE,
                                                                      combat.STANCE_OFFENSIVE)))

        GAUL_SIDE = 0
        gaul1_combat = Intent(gaul1, main.Intents.COMBAT, 1, combat_entity,
                              deferred.serialize(
                                  FightInCombatAction(gaul1, combat_entity, GAUL_SIDE, combat.STANCE_DEFENSIVE)))

        db.session.add_all([roman1_combat, roman2_combat, gaul1_combat])

        # It's necessary to load the data from db, otherwise the test fails during the rollback (since SQLA 1.1)
        roman1_combat, roman2_combat, gaul1_combat = None, None, None
        roman1_combat = Intent.query.filter_by(executor=roman1, target=combat_entity).one()
        roman2_combat = Intent.query.filter_by(executor=roman2, target=combat_entity).one()
        gaul1_combat = Intent.query.filter_by(executor=gaul1, target=combat_entity).one()

        with patch("exeris.core.actions.FightInCombatAction.calculate_hit_damage", new=lambda x, y: 0.1):
            task_mock = TaskMock()
            task_mock.stop_repeating = MagicMock()
            combat_process = CombatProcess(combat_entity, task_mock)
            combat_process.perform()

            # test if gaul is hit twice, each for 0.1
            self.assertAlmostEqual(0.2, gaul1.damage)

            # one of two romans should be hit
            self.assertAlmostEqual(0.1, roman1.damage + roman2.damage)
        CombatProcess.RETREAT_CHANCE = 1.0  # retreat is always successful
        with patch("exeris.core.actions.FightInCombatAction.calculate_hit_damage", new=lambda x, y: 0.01):
            with roman1_combat as roman1_combat_action:
                roman1_combat_action.stance = combat.STANCE_RETREAT

            task_mock = TaskMock()
            task_mock.stop_repeating = MagicMock()
            combat_process = CombatProcess(combat_entity, task_mock)
            combat_process.perform()

            task_mock.stop_repeating.assert_not_called()

            self.assertCountEqual([roman2_combat, gaul1_combat], Intent.query.all())

            with gaul1_combat as gaul1_combat_action:
                gaul1_combat_action.stance = combat.STANCE_RETREAT

            task_mock = TaskMock()
            task_mock.stop_repeating = MagicMock()
            combat_process = CombatProcess(combat_entity, task_mock)
            combat_process.perform()

            task_mock.stop_repeating.assert_called_once_with()

            self.assertEqual([], Intent.query.all())
            self.assertEqual(0, Combat.query.count())

    def test_attack_character_and_join_combat_action(self):
        util.initialize_date()
        rl = RootLocation(Point(1, 1), 100)

        roman1 = util.create_character("roman1", rl, util.create_player("abc1"))
        gaul1 = util.create_character("gaul1", rl, util.create_player("abc21"))

        db.session.add(rl)
        db.session.flush()

        attack_action = AttackCharacterAction(roman1, gaul1)
        attack_action.perform()

        combat_entity = Combat.query.one()
        fighter_intents = Intent.query.filter_by(type=main.Intents.COMBAT).all()
        fighter_actions = [intent.serialized_action for intent in fighter_intents]
        self.assertCountEqual([["exeris.core.actions.FightInCombatAction",
                                {"side": combat.SIDE_ATTACKER, "executor": roman1.id,
                                 "stance": combat.STANCE_OFFENSIVE, "combat_entity": combat_entity.id}],
                               ["exeris.core.actions.FightInCombatAction",
                                {"side": combat.SIDE_DEFENDER, "executor": gaul1.id,
                                 "stance": combat.STANCE_OFFENSIVE, "combat_entity": combat_entity.id}]],
                              fighter_actions)

        # join ongoing combat
        gaul2 = util.create_character("gaul1", rl, util.create_player("abc231"))

        join_combat_action = JoinCombatAction(gaul2, combat_entity, combat.SIDE_DEFENDER)
        join_combat_action.perform()

        self.assertIsNotNone(gaul2.combat_action)
        self.assertEqual(combat.SIDE_DEFENDER, gaul2.combat_action.side)
        self.assertEqual(3, Intent.query.filter_by(target=combat_entity).count())

        # make it impossible to join the combat again
        join_combat_action = JoinCombatAction(gaul2, combat_entity, combat.SIDE_DEFENDER)
        self.assertRaises(main.AlreadyBeingInCombat, join_combat_action.perform)

        # change stance in combat

        self.assertEqual(combat.STANCE_OFFENSIVE, gaul2.combat_action.stance)

        change_stance_action = ChangeCombatStanceAction(gaul2, combat.STANCE_RETREAT)
        change_stance_action.perform()

        self.assertEqual(combat.STANCE_RETREAT, gaul2.combat_action.stance)

    def test_raise_exception_on_invalid_argument_for_combat_actions(self):
        util.initialize_date()
        rl = RootLocation(Point(1, 1), 100)

        roman1 = util.create_character("roman1", rl, util.create_player("abc1"))
        gaul1 = util.create_character("gaul1", rl, util.create_player("abc21"))
        germanic1 = util.create_character("germanic1", rl, util.create_player("abc31"))

        db.session.add(rl)
        db.session.flush()

        attack_yourself_action = AttackCharacterAction(roman1, roman1)
        self.assertRaises(main.CannotAttackYourselfException, attack_yourself_action.perform)

        # set up existing combat
        attack_gaul_action = AttackCharacterAction(roman1, gaul1)
        attack_gaul_action.perform()

        # try to attack sb when already being in combat
        attack_germanic_action = AttackCharacterAction(gaul1, germanic1)
        self.assertRaises(main.AlreadyBeingInCombat, attack_germanic_action.perform)

        # try to attack sb already in combat
        attack_gaul_action = AttackCharacterAction(germanic1, gaul1)
        self.assertRaises(main.TargetAlreadyInCombat, attack_gaul_action.perform)

        INCORRECT_STANCE_TYPE = 231
        change_stance_action = ChangeCombatStanceAction(gaul1, INCORRECT_STANCE_TYPE)
        self.assertRaises(ValueError, change_stance_action.perform)

        roman_gaul_combat = Combat.query.one()
        INCORRECT_SIDE = 123
        join_combat_on_incorrect_side = JoinCombatAction(germanic1, roman_gaul_combat, INCORRECT_SIDE)
        self.assertRaises(ValueError, join_combat_on_incorrect_side.perform)

    def test_if_character_has_ranged_weapon(self):
        rl = RootLocation(Point(1, 1), 30)
        char = util.create_character("uga", rl, util.create_player("buga"))

        bow_type = ItemType("bow", 200)
        bow_type.properties += [
            EntityTypeProperty(P.WEAPONIZABLE, {"ranged": True}),
            EntityTypeProperty(P.EQUIPPABLE, {"eq_part": main.EqParts.WEAPON}),
        ]

        bow = Item(bow_type, char)
        db.session.add_all([rl, bow_type, bow])

        self.assertFalse(combat.has_ranged_weapon(char))

        char.set_preferred_equipment_part(bow)

        self.assertTrue(combat.has_ranged_weapon(char))
