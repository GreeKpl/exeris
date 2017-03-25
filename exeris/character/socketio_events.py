import logging
import string
import time

import flask_socketio as client_socket
import math
from flask import g, render_template
import sqlalchemy as sql

from exeris.app import socketio_character_event
from exeris.core import models, actions, accessible_actions, recipes, deferred, general, main, combat
from exeris.core import properties
from exeris.core import util
from exeris.core.main import db, app
from exeris.core.properties_base import P

logger = logging.getLogger(__name__)


def decode_and_load_entities(enc_entities_ids):
    entities_ids = [app.decode(entity_id) for entity_id in enc_entities_ids]
    return models.Entity.query.filter(models.Entity.id.in_(entities_ids)).all()


def decode_and_load_entity(enc_entity_id):
    entity_id = app.decode(enc_entity_id)
    return models.Entity.query.filter_by(id=entity_id).one()


def single_entity_action(wrapped_function):
    def f(*args):
        entities_ids = args[0]
        return wrapped_function(entities_ids[0], *args[1:])

    return f


@socketio_character_event("character.rename_entity")
def rename_entity(entity_id, new_name):
    entity_id = app.decode(entity_id)
    entity_to_rename = models.Entity.by_id(entity_id)

    dynamic_nameable_property = properties.DynamicNameableProperty(entity_to_rename)
    dynamic_nameable_property.set_dynamic_name(g.character, new_name)

    db.session.commit()
    return app.encode(entity_id),


@socketio_character_event("get_entity_tag")
def get_entity_tag(entity_id):
    entity_id = app.decode(entity_id)

    entity = models.Entity.by_id(entity_id)
    text = g.pyslate.t("entity_info", html=True, **entity.pyslatize())

    return app.encode(entity_id), text


@socketio_character_event("character.update_top_bar")
def update_top_bar(endpoint_name):
    intents = models.Intent.query.filter_by(executor=g.character).all()

    # queue is not supported, so max 1 allowed TODO #72
    assert len([intent for intent in intents if intent.type == main.Intents.WORK]) <= 1

    pyslatized_intents = [deferred.call(intent.serialized_action).pyslatize() for intent in intents]

    rendered = render_template("character_top_bar.html", intents=pyslatized_intents, endpoint_name=endpoint_name)
    return rendered,


@socketio_character_event("speaking_form_refresh")
def speaking_form_refresh(message_type, receiver=None):
    if receiver:
        receiver = app.decode(receiver)
        receiver = models.Character.by_id(receiver)

    rendered = render_template("events/speaking.html", message_type=message_type, receiver=receiver)

    return rendered,


@socketio_character_event("character.say_aloud")
def say_aloud(message):
    action = actions.SayAloudAction(g.character, message)
    action.perform()

    db.session.commit()
    return ()


@socketio_character_event("character.say_to_somebody")
def say_to_somebody(receiver_id, message):
    receiver_id = app.decode(receiver_id)
    receiver = models.Character.by_id(receiver_id)

    action = actions.SpeakToSomebodyAction(g.character, receiver, message)
    action.perform()

    db.session.commit()
    return ()


@socketio_character_event("character.whisper")
def whisper(receiver_id, message):
    receiver_id = app.decode(receiver_id)
    receiver = models.Character.by_id(receiver_id)

    action = actions.WhisperToSomebodyAction(g.character, receiver, message)
    action.perform()

    db.session.commit()
    return ()


@socketio_character_event("character.join_activity")
@single_entity_action
def join_activity(enc_activity_id):
    activity = decode_and_load_entity(enc_activity_id)

    join_activity_action = actions.JoinActivityAction(g.character, activity)
    deferred.perform_or_turn_into_intent(g.character, join_activity_action)

    db.session.commit()
    client_socket.emit("character.join_activity_after", (str(g.character.id), enc_activity_id))


@socketio_character_event("character.get_all_events")
def get_all_events():
    start = time.time()
    events = db.session.query(models.Event).join(models.EventObserver).filter_by(observer=g.character) \
        .order_by(models.Event.id.asc()).all()

    queried = time.time()
    logger.debug("Initial pull of events on events page")
    logger.debug("query time: %s", queried - start)

    events = [{"id": event.id,
               "text": g.pyslate.t("game_date", game_date=event.date) + ": " +
                       g.pyslate.t(event.type_name, html=True, **event.params)
               } for event in events]

    tran = time.time()
    logger.debug("translations: %s", tran - queried)

    db.session.commit()
    return events,


@socketio_character_event("character.get_all_characters_around")
def get_all_characters_around():
    visibility_range = general.VisibilityBasedRange(10)
    chars = visibility_range.characters_near(g.character)

    # rendered = render_template("events/people_short.html", chars=chars,
    #                            get_combat_action=lambda char: properties.CombatableProperty(char).combat_action)

    def get_combat_id(char):
        combat_action = properties.CombatableProperty(char).combat_action
        if combat_action:
            return combat_action.combat_entity.id
        return None

    def get_combat_name(char):
        combat_action = properties.CombatableProperty(char).combat_action
        if combat_action:
            return g.pyslate.t("action_info", **combat_action.pyslatize())
        return None

    characters_list = [{
                           "id": app.encode(char.id),
                           "name": g.pyslate.t("character_info", html=True, **char.pyslatize()),
                           "combatName": get_combat_name(char),
                           "combatId": get_combat_id(char)
                       } for char in chars]

    db.session.commit()
    return characters_list,


@socketio_character_event("character.get_combat_details")
def combat_refresh_box(combat_id=None):
    if combat_id:
        combat_id = app.decode(combat_id)
        combat_entity = models.Combat.query.get(combat_id)
    else:  # default - try to show own combat
        combat_intent = models.Intent.query.filter_by(executor=g.character, type=main.Intents.COMBAT).first()
        if not combat_intent:
            return ""
        combat_entity = combat_intent.target
    if not combat_entity:
        return None

    attackers, defenders = combat.get_combat_actions_of_attackers_and_defenders(g.character, combat_entity)

    def convert_to_json(fighter_action):
        return {"id": app.encode(fighter_action.executor.id),
                "name": g.pyslate.t("character_info", **fighter_action.executor.pyslatize()),
                "stance": fighter_action.stance,
                "damage": fighter_action.executor.damage,
                "recordedDamage": combat_entity.get_recorded_damage(fighter_action.executor),
                }

    return {
               "attackers": [convert_to_json(action) for action in attackers],
               "defenders": [convert_to_json(action) for action in defenders],
           },


@socketio_character_event("character.combat_change_stance")
def combat_change_stance(new_stance):
    change_stance_action = actions.ChangeCombatStanceAction(g.character, new_stance)
    change_stance_action.perform()

    db.session.commit()
    return ()


@socketio_character_event("combat.join_side")
def combat_change_stance(combat_id, side):
    side = int(side)

    combat_id = app.decode(combat_id)
    combat_entity = models.Combat.query.get(combat_id)

    join_combat_action = actions.JoinCombatAction(g.character, combat_entity, side)
    join_combat_action.perform()

    db.session.commit()
    return ()


@socketio_character_event("character.eat")
@single_entity_action
def eat(enc_entity_id, amount=None):
    entity = decode_and_load_entity(enc_entity_id)

    if not amount:
        entity_edible_property = properties.EdibleProperty(entity)
        max_amount = min(entity.amount, entity_edible_property.get_max_edible(g.character))
        client_socket.emit("character.eat_setup",
                           (str(g.character.id), max_amount))
    else:
        eat_action = actions.EatAction(g.character, entity, amount)
        eat_action.perform()

        db.session.commit()
        client_socket.emit("character.eat_after",
                           (str(g.character.id), enc_entity_id))
        return ()


@socketio_character_event("character.move_in_direction")
def character_move_in_direction(direction):
    change_movement_direction_action = actions.ChangeMovementDirectionAction(g.character, int(direction))
    change_movement_direction_action.perform()

    db.session.commit()
    return ()


@socketio_character_event("character.stop_movement")
def character_stop_movement():
    stop_movement_direction_action = actions.StopMovementAction(g.character)
    stop_movement_direction_action.perform()

    db.session.commit()
    return ()


@socketio_character_event("character.get_movement_info")
def get_moving_entity_info():
    control_movement_class_name = deferred.get_qualified_class_name(actions.ControlMovementAction)

    try:
        moving_entity = actions.get_moving_entity(g.character)

        moving_entity_intent = models.Intent.query \
            .filter_by(target=moving_entity) \
            .filter(models.Intent.serialized_action[0] == control_movement_class_name).first()

        if moving_entity_intent:
            movement_info = {
                "canBeControlled": True,
                "youAreDriving": moving_entity_intent.executor == g.character,
            }
            rng = general.NeighbouringLocationsRange(False)
            can_see_driver = rng.is_near(g.character, moving_entity_intent.executor)
            if can_see_driver:
                with moving_entity_intent as action:
                    movement_info["movementAction"] = g.pyslate.t("character_info", html=True,
                                                                  **moving_entity_intent.executor.pyslatize()) + " " + \
                                                      g.pyslate.t("action_info", **action.pyslatize())
            return movement_info,
        elif moving_entity:
            return {
                       "canBeControlled": True,
                   },
    except main.CannotControlMovementException:
        pass
    return {
               "canBeControlled": False,
           },


@socketio_character_event("character.get_entities_to_bind_to")
def get_entities_to_bind_to(entity_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)
    rng = general.AdjacentLocationsRange(False)
    if not rng.is_near(g.character, entity):
        raise main.EntityTooFarAwayException(entity=entity)

    if not isinstance(entity, (models.Location, models.Character)):
        raise ValueError("Only locations and characters are allowed")

    entity_bindable_property = properties.BindableProperty(entity)

    allowed_groups = entity_bindable_property.get_allowed_types()
    allowed_concrete_types = [t.name for t in models.get_concrete_types_for_groups(allowed_groups)]

    char_loc = g.character.get_location()
    entities = models.Location.query.filter(models.Location.type_name.in_(allowed_concrete_types)) \
                   .filter(models.Location.id.in_(models.ids(char_loc.neighbours))).all() \
               + models.Character.query.filter(models.Character.type_name.in_(allowed_concrete_types)) \
                   .filter(models.Character.is_in(char_loc)).all()

    client_socket.emit("character.bind_to_vehicle_setup",
                       (str(g.character.id),
                        [{
                             "id": app.encode(entity.id),
                             "name": g.pyslate.t("entity_info", **entity.pyslatize()),
                         } for entity in entities]))


@socketio_character_event("character.bind_to_vehicle")
def bind_to_vehicle(entity_id, entity_to_bind_to_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)
    entity_to_bind_to_id = app.decode(entity_to_bind_to_id)
    entity_to_bind_to = models.Entity.by_id(entity_to_bind_to_id)

    bind_to_vehicle_action = actions.BindToVehicleAction(g.character, entity, entity_to_bind_to)
    bind_to_vehicle_action.perform()

    entity_union_member_property = properties.OptionalMemberOfUnionProperty(entity)
    entities_in_union = [entity_property.entity.id for entity_property
                         in entity_union_member_property.get_entity_properties_of_own_union()]

    db.session.commit()
    client_socket.emit("character.bind_to_vehicle_after",
                       (str(g.character.id), [app.encode(entity_id) for entity_id in entities_in_union]))


@socketio_character_event("character.unbind_from_vehicle")
def unbind_from_vehicle(entity_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    entity_member_of_union_property = properties.OptionalMemberOfUnionProperty(entity)
    members_of_union = [ep.entity.id for ep in entity_member_of_union_property.get_entity_properties_of_own_union()]

    unbind_from_vehicle_action = actions.UnbindFromVehicleAction(g.character, entity)
    unbind_from_vehicle_action.perform()

    db.session.commit()
    client_socket.emit("character.unbind_from_vehicle_after",
                       (str(g.character.id), [app.encode(union_member) for union_member in members_of_union]))
    return ()


@socketio_character_event("character.start_boarding_ship")
def start_boarding_ship(entity_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    start_boarding_action = actions.StartBoardingAction(g.character, entity)
    start_boarding_action.perform()
    db.session.commit()
    client_socket.emit("character.start_boarding_ship_after", (str(g.character.id), app.encode(entity_id)))


@socketio_character_event("character.start_unboarding_from_ship")
@single_entity_action
def get_ship_to_unboard_from(enc_other_ship_id):
    other_ship = decode_and_load_entity(enc_other_ship_id)

    start_unboarding_action = actions.StartUnboardingAction(g.character, other_ship)
    start_unboarding_action.perform()

    db.session.commit()
    client_socket.emit("character.start_unboarding_from_ship_after", (str(g.character.id), enc_other_ship_id))


@socketio_character_event("character.go_to_location")
@single_entity_action
def character_goto_location(entity_id):
    entity = decode_and_load_entity(entity_id)
    assert isinstance(entity, models.Location)

    models.Intent.query.filter_by(executor=g.character, type=main.Intents.WORK).delete()

    start_controlling_movement_action = actions.StartControllingMovementAction(g.character)
    control_movement_intent = start_controlling_movement_action.perform()

    with control_movement_intent as control_movement_action:
        control_movement_action.travel_action = actions.TravelToEntityAction(
            control_movement_intent.target, entity)

    db.session.commit()
    client_socket.emit("character.go_to_location_after", (str(g.character.id),))


@socketio_character_event("character.get_character_details")
def character_goto_location(target_character_id):
    target_character_id = app.decode(target_character_id)
    target_character = models.Character.by_id(target_character_id)

    if not general.VisibilityBasedRange(10).is_near(g.character, target_character):
        raise main.EntityTooFarAwayException(entity=target_character)

    intent_worked_on = models.Intent.query.filter_by(executor=g.character, type=main.Intents.WORK).first()

    action_worked_on = deferred.call(intent_worked_on.serialized_action) if intent_worked_on else None
    location = target_character.get_location()
    modifiers = target_character.modifiers
    target_optional_preferred_equipment_property = properties.OptionalPreferredEquipmentProperty(target_character)
    equipment = target_optional_preferred_equipment_property.get_equipment()

    participant_combatable_property = properties.CombatableProperty(target_character)
    combat_action = participant_combatable_property.combat_action
    character_observed_name = g.pyslate.t("character_info", html=True, **target_character.pyslatize())
    character_observed_raw_name = g.pyslate.t("character_info", html=False, **target_character.pyslatize())
    location_observed_name = g.pyslate.t("location_info", **location.pyslatize())
    if action_worked_on:
        action_name = g.pyslate.t("action_info", **action_worked_on.pyslatize())
    else:
        action_name = None
    if combat_action:
        combat_name = g.pyslate.t("action_info", **combat_action.pyslatize())
    else:
        combat_name = None
    equipment_names = [g.pyslate.t("entity_info", **eq_item.pyslatize()) for eq_item in equipment]

    return {
               "id": app.encode(target_character.id),
               "name": character_observed_name,
               "rawName": character_observed_raw_name,
               "locationName": location_observed_name,
               "locationId": app.encode(location.id),
               "workIntent": action_name,
               "combatIntent": combat_name,
               "shortDescription": "a bald man",
               "longDescription": "a handsome tall band man with blue eyes",
               "equipment": equipment_names,
               "modifiers": modifiers,
           },


@socketio_character_event("character.show_readable_contents")
@single_entity_action
def show_readable_content(enc_entity_id):
    entity = decode_and_load_entity(enc_entity_id)

    entity_readable_property = properties.ReadableProperty(entity)
    title = entity_readable_property.read_title()
    contents = entity_readable_property.read_contents()
    raw_contents = entity_readable_property.read_raw_contents()

    client_socket.emit("character.show_readable_contents_after", (str(g.character.id), {
        "id": enc_entity_id,
        "title": title,
        "contents": contents,
        "rawContents": raw_contents,
    }))


@socketio_character_event("edit_readable")
def edit_readable(entity_id, text):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    entity_readable_property = properties.ReadableProperty(entity)
    entity_readable_property.alter_contents("title", text, models.TextContent.FORMAT_MD)

    db.session.commit()
    return app.encode(entity_id),


def _get_entity_infos_in(parent_entity, observer, excluded=None):
    entities = _get_entities_in(parent_entity, excluded)
    cache_properties_of_entities(entities)

    entity_entries = []
    for entity in entities:
        entity_info = _get_entity_info(entity, observer)

        entity_entries.append(entity_info)
    return entity_entries


def cache_properties_of_entities(entities):
    real_entities = [e for e in entities if isinstance(e, models.Entity)]
    property_cache = main.property_cache
    property_cache.save_all_properties_of_entities(real_entities)
    entities_in_passages_to_neighbours = util.flatten([[e.other_side, e.passage]
                                                       for e in entities if isinstance(e, models.PassageToNeighbour)])
    property_cache.save_all_properties_of_entities(entities_in_passages_to_neighbours)
    all_found_entities = real_entities + entities_in_passages_to_neighbours
    if len(all_found_entities):
        activities = models.Entity.query.filter(
            models.Entity.is_in(all_found_entities)).all()
        property_cache.save_all_properties_of_entities(activities)


def _get_entities_in(parent_entity, excluded=None):
    excluded = excluded if excluded else []
    entities = models.Entity.query.filter(models.Entity.is_in(parent_entity)) \
        .filter(~models.Entity.id.in_(models.ids(excluded))) \
        .filter(models.Entity.discriminator_type != models.ENTITY_ACTIVITY) \
        .all()
    if isinstance(parent_entity, models.Location):
        entities += [passage for passage in parent_entity.passages_to_neighbours if
                     passage.other_side not in excluded]

        if not models.EntityContentsPreference.query.filter_by(character=g.character,
                                                               open_entity=parent_entity).first():
            db.session.add(models.EntityContentsPreference(g.character, parent_entity))
    return entities


@socketio_character_event("character.get_root_entities")
def get_root_entities():
    location = g.character.being_in
    rng = general.VisibilityBasedRange(distance=10, only_through_unlimited=False)

    displayed_locations = rng.root_locations_near(location)
    if location.get_root() in displayed_locations:
        displayed_locations.remove(location.get_root())
    displayed_locations = [location] + displayed_locations

    locations = [_get_entity_info(loc_to_show, g.character) for loc_to_show in displayed_locations]
    return locations,


@socketio_character_event("character.get_items_in_inventory")
def get_inventory_root():
    rng = general.InsideRange()
    items_in_inventory = rng.items_near(g.character)

    items = [_get_entity_info(item_to_show, g.character) for item_to_show in items_in_inventory]
    return items,


@socketio_character_event("character.get_children_entities")
def get_children_entities(entity_id, parent_parent_id):
    parent_entity = models.Entity.by_id(app.decode(entity_id))
    rng = general.VisibilityBasedRange(distance=30)
    if not rng.is_near(g.character, parent_entity):
        raise main.EntityTooFarAwayException(entity=parent_entity)
    exclude = [models.Entity.by_id(app.decode(parent_parent_id))] if parent_parent_id else []
    if isinstance(parent_entity, models.Passage):
        parent_entity = parent_entity.right_location \
            if parent_entity.left_location in exclude \
            else parent_entity.left_location
    rendered = _get_entity_infos_in(parent_entity, g.character, exclude)
    return rendered,


@socketio_character_event("character.get_extended_entity_info")
def get_entities(enc_entity_id, enc_parent_id):
    entity = decode_and_load_entity(enc_entity_id)

    cache_properties_of_entities([entity])

    parent_entity = None
    if enc_parent_id:
        parent_entity = decode_and_load_entity(enc_parent_id)

    rng = general.VisibilityBasedRange(distance=30)
    if not rng.is_near(g.character, entity):
        return {"id": enc_entity_id},

    if not enc_parent_id or entity.being_in == parent_entity:
        entity_info = _get_entity_info(entity, g.character)
    else:
        entity_info = None

    excluded = []
    if parent_entity:
        excluded = [parent_entity]
    return {"id": enc_entity_id,
            "info": entity_info,
            "children": _get_entities_in(entity, excluded)
            },


@socketio_character_event("character.get_detailed_entity_info")
def get_detailed_entity_info(enc_entity_id):
    entity = decode_and_load_entity(enc_entity_id)

    rng = general.VisibilityBasedRange(distance=30)
    if not rng.is_near(g.character, entity):
        raise main.EntityTooFarAwayException(entity=entity)

    if isinstance(entity, models.Activity):
        return {
                   "id": app.encode(entity.id),
                   "type": "Activity",
                   "name": g.pyslate.t("entity_info", **entity.pyslatize()),
                   "input": entity.requirements.get("input", {}),
                   "ticksLeft": entity.ticks_left,
                   "ticksNeeded": entity.ticks_needed,
               },

    return {
               "id": app.encode(entity.id),
               "type": entity.__class__.__name__,
               "name": g.pyslate.t("entity_info", **entity.pyslatize()),
           },


@socketio_character_event("character.move_to_location")
@single_entity_action
def move_to_location(location_id):
    location = decode_and_load_entity(location_id)

    passage = models.Passage.query.filter(models.Passage.between(g.character.being_in, location)).one()

    action = actions.MoveToLocationAction(g.character, passage)
    action.perform()

    db.session.commit()
    client_socket.emit("character.move_to_location_after", (str(g.character.id)))


@socketio_character_event("character.add_item_to_activity")
@single_entity_action
def form_add_item_to_activity(enc_activity_id, req_group_name, enc_entity_to_add_id=None, amount=None):
    activity = decode_and_load_entity(enc_activity_id)

    if not enc_entity_to_add_id:
        loc = g.character.being_in

        req_group = models.EntityType.by_name(req_group_name)
        type_names_in_group = [t_and_e[0].name for t_and_e in req_group.get_descending_types()]

        potential_items_to_add = models.Item.query.filter(
            sql.or_(
                models.Item.is_in(g.character),
                models.Item.is_in(loc),
            ),
            models.Item.type_name.in_(type_names_in_group),
        ).all()
        req_info = activity.requirements["input"][req_group_name]
        used_type = req_info.get("used_type", None)
        req_left = req_info["left"]

        item_infos = []
        for item in potential_items_to_add:
            if used_type and item.type_name != used_type:
                continue
            type_efficiency_ratio = req_group.quantity_efficiency(item.type)
            max_needed = math.ceil(req_left / type_efficiency_ratio)
            max_amount = min(max_needed, item.amount)
            item_infos.append({
                "id": app.encode(item.id),
                "name": item.type.name + " in " + str(item.being_in),  # TODO i18n translate
                "maxAmount": max_amount,
            })

        db.session.commit()
        client_socket.emit("character.add_item_to_activity_setup", (g.character.id,
                                                                    enc_activity_id, {
                                                                        "itemsToAdd": item_infos
                                                                    }))
    else:
        entity_to_add = decode_and_load_entity(enc_entity_to_add_id)

        action = actions.AddEntityToActivityAction(g.character, entity_to_add, activity, amount)
        action.perform()

        db.session.commit()
        client_socket.emit("character.add_item_to_activity_after", (g.character.id,
                                                                    enc_activity_id,
                                                                    enc_entity_to_add_id))
    return ()


@socketio_character_event("character.take_item")
def take_item(enc_item_ids, amount=None):
    items = decode_and_load_entities(enc_item_ids)

    if len(items) == 1 and items[0].type.stackable and not amount:  # one stackable
        client_socket.emit("character.take_item_setup", (str(g.character.id), items[0].amount))
    else:
        for item in items:
            amount = amount if amount else item.amount
            take_from_storage_action = actions.TakeItemAction(g.character, item, amount=amount)
            take_from_storage_action.perform()

        client_socket.emit("character.take_item_after", (str(g.character.id), enc_item_ids))
    db.session.commit()
    return ()


@socketio_character_event("character.put_into_storage")
def put_into_storage(enc_item_ids, storage_id=None, amount=None):
    items = decode_and_load_entities(enc_item_ids)

    if not storage_id:
        storage_items = models.Item.query.filter(models.Item.is_in([g.character, g.character.being_in]),
                                                 models.Item.has_property(P.STORAGE, can_store=True)).all()
        storage_locations = [psg for psg in g.character.get_location().passages_to_neighbours
                             if psg.other_side.has_property(P.STORAGE, can_store=True)]

        accessible_storages = storage_items + storage_locations
        storages_json = [{
                             "id": app.encode(storage.id),
                             "name": g.pyslate.t("entity_info", **storage.pyslatize()),
                         } for storage in accessible_storages]

        max_amount = None
        if len(items) == 1:
            max_amount = items[0].amount
        client_socket.emit("character.put_into_storage_setup", (str(g.character.id), max_amount, storages_json))
    else:
        storage = models.Entity.by_id(app.decode(storage_id))

        for item in items:
            amount = amount if amount else item.amount
            put_into_storage_action = actions.PutIntoStorageAction(g.character, item, storage, amount=amount)
            put_into_storage_action.perform()

        db.session.commit()
        client_socket.emit("character.put_into_storage_after", enc_item_ids)


@socketio_character_event("character.drop_item")
def drop_item(enc_item_ids, amount=None):
    items = decode_and_load_entities(enc_item_ids)

    if len(items) == 1 and items[0].type.stackable and not amount:  # one stackable
        client_socket.emit("character.drop_item_setup", (str(g.character.id), items[0].amount))
    else:
        for item in items:
            amount = amount if amount else item.amount
            drop_item_action = actions.DropItemAction(g.character, item, amount=amount)
            drop_item_action.perform()

        db.session.commit()
        client_socket.emit("character.drop_item_after", (str(g.character.id), enc_item_ids))


def get_identifier_for_union(union_id):
    if not union_id:
        return None
    identifier_index = union_id % len(string.ascii_uppercase)
    return string.ascii_uppercase[identifier_index]


def get_entity_action_info(entity_action):
    return {
        "name": entity_action.tag_name,
        "image": entity_action.image,
        "entity": app.encode(entity_action.entity.id),
        "endpoint": entity_action.endpoint,
        "allowMultipleEntities": entity_action.multi_entities,
        "multiEntitiesName": entity_action.multi_tag_name,
    }


def has_needed_prop(entity, action):
    if action.required_property == P.ANY:
        return True
    return entity.has_property(action.required_property)


def get_accessible_actions(entity, accessible_actions_list):
    return [accessible_actions.EntityActionRecord(entity, action) for action in accessible_actions_list if
            has_needed_prop(entity, action) and action.other_req(entity)]


def get_activity_info(activity):
    possible_actions = get_accessible_actions(activity, accessible_actions.ACTIONS_ON_GROUND)
    available_actions = [get_entity_action_info(a) for a in possible_actions]
    return {
        "id": app.encode(activity.id),
        "name": g.pyslate.t("entity_info", **activity.pyslatize()),
        "parent": app.encode(activity.being_in.id),
        "ticksLeft": activity.ticks_left,
        "ticksNeeded": activity.ticks_needed,
        "actions": available_actions,
    }


def _get_entity_info(entity, observer):
    if isinstance(entity, models.Passage):
        entity = _get_directed_passage_in_correct_direction(g.character.being_in, entity)

    other_side = None
    if isinstance(entity, models.PassageToNeighbour):
        full_name = g.pyslate.t("entity_info",
                                other_side=entity.other_side.pyslatize(detailed=True),
                                **entity.passage.pyslatize(detailed=True))
        passage_to_neighbour = entity
        entity = passage_to_neighbour.passage
        other_side = passage_to_neighbour.other_side
    elif isinstance(entity, models.Entity):
        full_name = g.pyslate.t("entity_info", **entity.pyslatize(detailed=True))
    else:
        raise ValueError("Entity to show is of type {}".format(type(entity)))

    activities = []
    # TODO translation
    activity = models.Activity.query.filter(models.Activity.is_in(entity)).first()
    if activity:
        activities.append(activity)

    possible_actions = get_accessible_actions(entity, accessible_actions.ACTIONS_ON_GROUND)

    if isinstance(entity, models.Passage):
        possible_actions += get_accessible_actions(other_side, accessible_actions.ACTIONS_ON_GROUND)

        other_side_is_enterable_or_storage = other_side.has_property(P.STORAGE) or other_side.has_property(P.ENTERABLE)
        are_entities_on_other_side = models.Entity.query.filter(models.Entity.is_in(other_side)) \
                                         .filter(models.Entity.discriminator_type != models.ENTITY_ACTIVITY).count() > 0
        if not are_entities_on_other_side:
            are_entities_on_other_side = models.Passage.query.filter(models.Passage.incident(other_side)).count() > 1

        can_see_the_other_side = general.VisibilityBasedRange(distance=30).is_near(g.character, other_side)
        expandable = other_side_is_enterable_or_storage and are_entities_on_other_side and can_see_the_other_side

        activity = models.Activity.query.filter(models.Activity.is_in(other_side)).first()
        if activity:
            activities.append(activity)
        other_side_member_of_union = properties.OptionalMemberOfUnionProperty(other_side)
        union_membership = get_identifier_for_union(other_side_member_of_union.get_union_id())
    else:
        expandable = entity == observer or \
                     (entity.has_property(P.STORAGE) or entity.has_property(P.ENTERABLE)) \
                     and not entity.has_property(P.CLOSEABLE, closed=True) and \
                     models.Entity.query.filter(models.Entity.parent_entity == entity) \
                         .filter(models.Entity.discriminator_type != models.ENTITY_ACTIVITY).first() is not None
        entity_member_of_union = properties.OptionalMemberOfUnionProperty(entity)
        union_membership = get_identifier_for_union(entity_member_of_union.get_union_id())

    available_actions = [get_entity_action_info(a) for a in possible_actions]
    return {
        "id": app.encode(entity.id),
        "name": full_name,
        "expandable": expandable,
        "actions": available_actions,
        "activities": [get_activity_info(a) for a in activities],
        "otherSide": app.encode(other_side.id) if other_side else None,
        "unionMembership": union_membership,
    }


def _get_directed_passage_in_correct_direction(char_location, entity):
    if entity.left_location == char_location:  # we are directly on the left side of the passage
        entity = models.PassageToNeighbour(entity, entity.right_location)
    else:  # we need to get the full location path to the passage
        path_to_left_loc = general.RangeSpec.get_path_between_locations(char_location, entity.left_location)
        # check which side of the passage is closer to us
        if path_to_left_loc[-2] == entity.right_location:
            entity = models.PassageToNeighbour(entity, entity.left_location)
        else:
            entity = models.PassageToNeighbour(entity, entity.right_location)
    return entity


@socketio_character_event("character.toggle_closeable")
def toggle_closeable(entity_id):
    entity = models.Entity.by_id(app.decode(entity_id))

    action = actions.ToggleCloseableAction(g.character, entity)
    action.perform()

    db.session.commit()
    client_socket.emit("character.toggle_closeable_after", entity_id)


@socketio_character_event("character.attack")
@single_entity_action
def character_attack(enc_entity_id):
    entity_to_attack = decode_and_load_entity(enc_entity_id)

    action = actions.AttackEntityAction(g.character, entity_to_attack)
    action.perform()

    db.session.commit()
    client_socket.emit("character.attack_after", enc_entity_id)


@socketio_character_event("character.get_all_recipes")
def update_actions_list():
    recipe_list_producer = recipes.RecipeListProducer(g.character)
    entity_recipes = models.EntityRecipe.query.all()
    enabled_entity_recipes = recipe_list_producer.get_recipe_list()
    recipe_names = [{"name": recipe.name_tag,
                     "id": app.encode(recipe.id),
                     "enabled": recipe in enabled_entity_recipes} for recipe in entity_recipes]

    return recipe_names,


@socketio_character_event("character.get_recipe_details")
def activity_from_recipe_setup(recipe_id):
    recipe_id = app.decode(recipe_id)
    recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

    form_inputs = recipes.ActivityFactory.get_user_inputs_for_recipe(recipe)

    errors = recipes.ActivityFactory.get_list_of_errors(recipe, g.character)
    error_messages = [g.pyslate.t(error.error_tag, **error.error_kwargs) for error in errors]

    potential_subjects = recipes.ActivityFactory.get_selectable_entities(recipe, g.character)

    subjects = [
        {
            "id": app.encode(subject.id),
            "name": g.pyslate.t("entity_info", **subject.pyslatize()),
        } for subject in potential_subjects]

    additional_form_inputs = [{
                                  "name": input_name,
                                  "type": input_class.__name__,
                                  "args": input_class.action_args,
                              } for input_name, input_class in form_inputs.items()]

    return {
               "id": recipe.id,
               "name": g.pyslate.t(recipe.name_tag, **recipe.name_params),
               "requiresSubject": recipe.activity_container[0] == "selected_entity",
               "subjects": subjects,
               "requiredInput": list(recipe.requirements.get("input", {}).keys()),
               "requiredTools": recipe.requirements.get("mandatory_tools", []),
               "optionalTools": list(recipe.requirements.get("optional_tools", {}).keys()),
               "requiredMachines": recipe.requirements.get("mandatory_machines", []),
               "optionalMachines": list(recipe.requirements.get("optional_machines", {}).keys()),
               "requiredDays": recipe.ticks_needed,
               "requiredSkills": list(recipe.requirements.get("skills", {}).keys()),
               "requiredFormInputs": additional_form_inputs,
               "errorMessages": error_messages,
           },


@socketio_character_event("character.create_activity_from_recipe")
def create_activity_from_recipe(recipe_id, user_input, selected_entity_id):
    recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

    activitys_being_in = g.character.get_location()
    if selected_entity_id:
        selected_entity_id = app.decode(selected_entity_id)
        selected_entity = models.Entity.by_id(selected_entity_id)
        rng = actions.most_strict_range_spec_for_entity(selected_entity)
        if not rng.is_near(g.character, selected_entity):
            raise main.EntityTooFarAwayException(entity=selected_entity)
        if selected_entity.has_activity():
            raise main.ActivityAlreadyExistsOnEntity(entity=selected_entity)

        activitys_being_in = selected_entity

    activity_factory = recipes.ActivityFactory()
    form_input_by_name = recipes.ActivityFactory.get_user_inputs_for_recipe(recipe)

    recipe_setup_errors = activity_factory.get_list_of_errors(recipe, g.character)
    if recipe_setup_errors:
        raise recipe_setup_errors[0]

    user_input = {name: form_input_by_name[name].convert(value) for name, value in user_input.items()}

    activity = activity_factory.create_from_recipe(recipe, activitys_being_in, g.character, user_input=user_input)

    db.session.add_all([activity])
    db.session.commit()
    return ()


@socketio_character_event("character.start_burying_entity")
@single_entity_action
def start_burying_entity(enc_entity_id):
    entity = decode_and_load_entity(enc_entity_id)

    start_burying_entity_action = actions.StartBuryingEntityAction(g.character, entity)
    start_burying_entity_action.perform()

    db.session.commit()
    client_socket.emit("character.start_burying_entity_after", (str(g.character.id),))


@socketio_character_event("character.start_taming_animal")
def start_taming_animal(enc_entity_ids):
    entities = decode_and_load_entities(enc_entity_ids)

    for entity in entities:
        start_taming_animal_action = actions.StartTamingAnimalAction(g.character, entity)
        start_taming_animal_action.perform()

    db.session.commit()
    client_socket.emit("character.start_taming_animal_after", (str(g.character.id), enc_entity_ids))
