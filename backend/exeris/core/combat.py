import random

from exeris.core import deferred, models, general, main, properties
from exeris.core.properties_base import P

SIDE_ATTACKER = 0
SIDE_DEFENDER = 1

STANCE_OFFENSIVE = "stance_offensive"
STANCE_DEFENSIVE = "stance_defensive"
STANCE_RETREAT = "stance_retreat"


def get_combat_actions_of_visible_foes_and_allies(participant, combat_entity):
    attackers, defenders = get_combat_actions_of_attackers_and_defenders(participant, combat_entity)

    participant_combatable_property = properties.CombatableProperty(participant)
    own_combat_action = participant_combatable_property.combat_action
    if own_combat_action.side == SIDE_ATTACKER:
        foes, allies = defenders, attackers
    else:
        foes, allies = attackers, defenders
    return foes, allies


def get_combat_actions_of_attackers_and_defenders(participant, combat_entity):
    combatant_intents = models.Intent.query.filter_by(target=combat_entity).all()

    combat_actions_of_both_sides = [deferred.call(intent.serialized_action) for intent in combatant_intents]

    attacker_combat_actions = [action for action in combat_actions_of_both_sides if
                               action.side == SIDE_ATTACKER]
    defender_combat_actions = [action for action in combat_actions_of_both_sides if
                               action.side == SIDE_DEFENDER]

    combat_range = general.VisibilityBasedRange(10)

    return (filter_visible_combatants(attacker_combat_actions, participant, combat_range),
            filter_visible_combatants(defender_combat_actions, participant, combat_range))


def filter_visible_combatants(combat_actions, participant, combat_range):
    return [combat for combat in combat_actions if combat_range.is_near(participant, combat.executor)]


def get_combat_actions_of_visible_foes(participant, combat_entity):
    """
    Returns list of :class:`exeris.core.actions.FightInCombatAction` for fighters
    that can be a potential target of an attack by the `participant` (A). For each other participant (B) it means:
     - Participant B is range of mutual attack of A (weapon is irrelevant)
     - Participant B is in the same combat as A
    It's just a preliminary list of potential combat targets. The list can be shortened (filtered), but NOT expanded.
    It can be interpreted as: "Each of listed participants can be attacked in some specific circumstances".
    :param participant: participant in proximity of whom combatants need to be
    :param combat_entity: entity of combat in which `participant` is
    :return: list of combat actions of all potential targets
    """
    return get_combat_actions_of_visible_foes_and_allies(participant, combat_entity)[0]


def get_hit_target(attacker_combat_action, foe_combat_actions):
    """
    Returns a combat action for a fighter which is selected as target for the hit.
    It takes into the consideration
    :param attacker_combat_action: action of a fighter who needs a target to hit
    :param foe_combat_actions: list of combat actions of all potential targets being in visibility range
    :return: hit target's combat action or None when nobody can be hit
    """

    combat_entity = attacker_combat_action.combat_entity
    foe_combat_actions = [action for action in foe_combat_actions if combat_entity.is_able_to_fight(action.executor)]

    if not has_ranged_weapon(attacker_combat_action.executor):
        attacker = attacker_combat_action.executor

        # we can attack melee only traversably-accessible targets
        range_to_fight_melee = general.TraversabilityBasedRange(50, allowed_terrain_types=[main.Types.LAND_TERRAIN])
        foe_combat_actions = [foe_action for foe_action in foe_combat_actions if
                              range_to_fight_melee.is_near(attacker, foe_action.executor)]

        # we are melee, so we can hit only melee foes, unless only ranged foes are there
        melee_fighters = [foe_action for foe_action in foe_combat_actions if not has_ranged_weapon(foe_action.executor)]
        if melee_fighters:  # melee fighters protect ranged fighters, so they are ignored
            foe_combat_actions = melee_fighters

    if not foe_combat_actions:
        return None

    return _get_random(foe_combat_actions)


def has_ranged_weapon(participant):
    participant_combatable_property = properties.CombatableProperty(participant)
    weapon = participant_combatable_property.get_weapon()
    return weapon.has_property(P.WEAPONIZABLE, ranged=True)


def _get_random(foe_actions):
    """
    To be mocked in tests.
    :return: random element of list
    """
    return random.choice(foe_actions)
