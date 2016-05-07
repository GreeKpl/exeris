import random

from exeris.core import actions, deferred, models, general
from exeris.core.properties_base import P


def get_combat_actions_of_visible_foes_and_allies(character, combat_entity):
    attackers, defenders = get_combat_actions_of_attackers_and_defenders(character, combat_entity)

    own_combat_action = character.get_combat_action()
    if own_combat_action.side == actions.CombatProcess.SIDE_ATTACKER:
        foes, allies = defenders, attackers
    else:
        foes, allies = attackers, defenders
    return foes, allies


def get_combat_actions_of_attackers_and_defenders(character, combat_entity):
    combatant_intents = models.Intent.query.filter_by(target=combat_entity).all()

    combat_actions_of_both_sides = [deferred.call(intent.serialized_action) for intent in combatant_intents]

    attacker_combat_actions = [action for action in combat_actions_of_both_sides if
                               action.side == actions.CombatProcess.SIDE_ATTACKER]
    defender_combat_actions = [action for action in combat_actions_of_both_sides if
                               action.side == actions.CombatProcess.SIDE_DEFENDER]

    combat_range = general.VisibilityBasedRange(10)
    visible_combatants = combat_range.characters_near(character)
    return (filter_visible_combatants(attacker_combat_actions, visible_combatants),
            filter_visible_combatants(defender_combat_actions, visible_combatants))


def filter_visible_combatants(combat_actions, visible_combatants):
    return [combat for combat in combat_actions if combat.executor in visible_combatants]


def get_combat_actions_of_visible_foes(character, combat_entity):
    """
    Returns list of :class:`exeris.core.actions.FightInCombatAction` for characters
    that can be potential target of an attack by `character` (A). For each other character (B) it means:
     - Character B is range of mutual attack of A (weapon is irrelevant)
     - Character B is in the same combat as A
    It's just a preliminary list of potential combat targets. The list can be shortened (filtered), but NOT expanded.
    It can be interpreted as: "Each of listed characters can be attacked in some specific circumstances".
    :param character: character in proximity of whom combatants need to be
    :param combat_entity: entity of combat in which `character` is
    :return: list of combat actions of all potential targets
    """
    return get_combat_actions_of_visible_foes_and_allies(character, combat_entity)[0]


def get_hit_target(character_combat_action, foe_combat_actions):
    """
    Returns character action for character which is selected as target for the hit.
    It takes into the consideration
    :param character_combat_action: action of character who needs a target to hit
    :param foe_combat_actions: list of combat actions of all potential targets being in visibility range
    :return: hit target's combat action or None when nobody can be hit
    """

    def has_ranged_weapon(character):
        weapon = character.get_weapon()
        return weapon.get_property(P.WEAPONIZABLE).get("ranged", False)

    if not has_ranged_weapon(character_combat_action.executor):
        character = character_combat_action.executor

        # we can attack melee only traversably-accessible targets
        range_to_fight_melee = general.LandTraversabilityBasedRange(50)
        foe_combat_actions = [foe_action for foe_action in foe_combat_actions if
                              range_to_fight_melee.is_near(character, foe_action.executor)]

        # we are melee, so we can hit only melee foes, unless only ranged foes are there
        melee_fighters = [foe_action for foe_action in foe_combat_actions if not has_ranged_weapon(foe_action.executor)]
        if melee_fighters:  # melee fighters protect ranged fighters, so they are ignored
            foe_combat_actions = melee_fighters

    if not foe_combat_actions:
        return None

    return _get_random(foe_combat_actions)


def _get_random(foe_actions):
    """
    To be mocked in tests.
    :return: random element of list
    """
    return random.choice(foe_actions)
