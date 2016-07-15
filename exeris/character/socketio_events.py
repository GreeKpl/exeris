import time

import flask_socketio as client_socket
from exeris.app import socketio_character_event
from exeris.core import models, actions, accessible_actions, recipes, deferred, general, main, combat
from exeris.core.main import db, app
from exeris.core.properties_base import P
from flask import g, render_template


@socketio_character_event("rename_entity")
def rename_entity(entity_id, new_name):
    entity_id = app.decode(entity_id)
    entity_to_rename = models.Entity.by_id(entity_id)

    entity_to_rename.set_dynamic_name(g.character, new_name)

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


@socketio_character_event("say_aloud")
def say_aloud(message):
    action = actions.SayAloudAction(g.character, message)
    action.perform()

    db.session.commit()
    return ()


@socketio_character_event("say_to_somebody")
def say_to_somebody(receiver_id, message):
    receiver_id = app.decode(receiver_id)
    receiver = models.Character.by_id(receiver_id)

    action = actions.SpeakToSomebodyAction(g.character, receiver, message)
    action.perform()

    db.session.commit()
    return ()


@socketio_character_event("whisper")
def whisper(receiver_id, message):
    receiver_id = app.decode(receiver_id)
    receiver = models.Character.by_id(receiver_id)

    action = actions.WhisperToSomebodyAction(g.character, receiver, message)
    action.perform()

    db.session.commit()
    return ()


@socketio_character_event("get_activity_info")
def get_activity_info():
    pass


@socketio_character_event("join_activity")
def join_activity(activity_id):
    activity_id = app.decode(activity_id)

    activity = models.Activity.by_id(activity_id)
    action = actions.JoinActivityAction(g.character, activity)

    deferred.perform_or_turn_into_intent(g.character, action)

    db.session.commit()
    return ()


@socketio_character_event("character.pull_events_initial")
def pull_events_initial():
    start = time.time()
    events = db.session.query(models.Event).join(models.EventObserver).filter_by(observer=g.character) \
        .order_by(models.Event.id.asc()).all()

    queried = time.time()
    print("query: ", queried - start)

    events = [{"id": event.id, "text": g.pyslate.t("game_date", game_date=event.date) + ": " +
                                       g.pyslate.t(event.type_name, html=True, **event.params)} for event in events]

    tran = time.time()
    print("translations:", tran - queried)
    all_time = time.time()
    print("esc: ", all_time - tran)
    db.session.commit()
    return events,


@socketio_character_event("people_short.refresh_list")
def people_short_refresh_list():
    visibility_range = general.VisibilityBasedRange(10)
    chars = visibility_range.characters_near(g.character)
    rendered = render_template("events/people_short.html", chars=chars)

    db.session.commit()
    return rendered,


@socketio_character_event("character.combat_refresh_box")
def combat_refresh_box(combat_id=None):
    if combat_id:
        combat_id = app.decode(combat_id)
        combat_entity = models.Combat.query.get(combat_id)
        own_combat_action = None
    else:  # default - try to show own combat
        combat_intent = models.Intent.query.filter_by(executor=g.character, type=main.Intents.COMBAT).first()
        if not combat_intent:
            return ""
        combat_entity = combat_intent.target
        own_combat_action = deferred.call(combat_intent.serialized_action)
    if not combat_entity:
        return ""

    attackers, defenders = combat.get_combat_actions_of_attackers_and_defenders(g.character, combat_entity)

    rendered = render_template("combat.html", own_action=own_combat_action,
                               attackers=attackers, defenders=defenders,
                               combat_entity=combat_entity, combat_stances=actions.CombatProcess)

    return rendered,


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


@socketio_character_event("eat")
def eat(entity_id, amount=None):
    entity_id = app.decode(entity_id)
    entity = models.Item.by_id(entity_id)

    if not amount:
        client_socket.emit("before_eat", (app.encode(entity_id), entity.get_max_edible(g.character)))
    else:
        eat_action = actions.EatAction(g.character, entity, amount)
        eat_action.perform()
        entity_info = g.pyslate.t("entity_info", **entity.pyslatize(item_amount=amount))

        db.session.commit()
        return entity_info, amount


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

    moving_entity_intent = models.Intent.query \
        .filter_by(target=actions.get_moving_entity(g.character)) \
        .filter(models.Intent.serialized_action[0] == control_movement_class_name).first()

    rendered_info_page = render_template("map/control_movement.html", moving_entity_intent=moving_entity_intent)
    return rendered_info_page,


@socketio_character_event("character.go_to_location")
def character_goto_location(entity_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    assert isinstance(entity, models.Location)

    models.Intent.query.filter_by(executor=g.character, type=main.Intents.WORK).delete()

    start_controlling_movement_action = actions.StartControllingMovementAction(g.character)
    control_movement_intent = start_controlling_movement_action.perform()

    control_movement_action = deferred.call(control_movement_intent.serialized_action)  # TODO improve in #99
    control_movement_action.travel_action = actions.TravelToEntityAction(
        control_movement_intent.target, entity)
    control_movement_intent.serialized_action = deferred.serialize(control_movement_action)

    db.session.commit()
    return ()


@socketio_character_event("open_readable_contents")
def open_readable_contents(entity_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    title = entity.read_title()
    contents = entity.read_contents()
    raw_contents = entity.read_raw_contents()
    modal = render_template("entities/modal_readable.html", title=title, contents=contents, entity_id=entity_id,
                            raw_contents=raw_contents)
    client_socket.emit("after_open_readable_contents", modal)


@socketio_character_event("edit_readable")
def edit_readable(entity_id, text):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    entity.alter_contents("title", text, models.TextContent.FORMAT_MD)

    db.session.commit()
    return app.encode(entity_id),


def _get_entities_in(parent_entity, excluded=None):
    excluded = excluded if excluded else []

    entities = models.Entity.query.filter(models.Entity.is_in(parent_entity)) \
        .filter(~models.Entity.id.in_([e.id for e in excluded])).all()

    if isinstance(parent_entity, models.Location):
        entities += [passage for passage in parent_entity.passages_to_neighbours if
                     passage.other_side not in excluded]

        if not models.EntityContentsPreference.query.filter_by(character=g.character,
                                                               open_entity=parent_entity).first():
            db.session.add(models.EntityContentsPreference(g.character, parent_entity))

    entity_entries = []
    for entity in entities:
        entity_info = _get_entity_info(entity)

        entity_entries.append(entity_info)
    return entity_entries


@socketio_character_event("collapse_entity")
def collapse_entity(parent_entity_id):
    parent_entity = models.Entity.by_id(app.decode(parent_entity_id))
    pref = models.EntityContentsPreference.query.filter_by(character=g.character, open_entity=parent_entity).first()
    if pref:
        db.session.delete(pref)

    db.session.commit()
    return parent_entity_id,


@socketio_character_event("entities_refresh_list")
def entities_refresh_list(view):
    if view == "inventory":
        location = g.character
    else:
        location = g.character.being_in

    rng = general.VisibilityBasedRange(distance=30, only_through_unlimited=False)
    if isinstance(location, models.RootLocation):
        displayed_locations = rng.root_locations_near(location)
    else:
        displayed_locations = [location]

    locations = [_get_entity_info(loc_to_show) for loc_to_show in displayed_locations]
    return locations,


@socketio_character_event("refresh_entity_info")
def refresh_entity_info(entity_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    entity_info = _get_entity_info(entity)
    return entity_info,


@socketio_character_event("entities_get_sublist")
def entities_get_sublist(entity_id, parent_parent_id):
    parent_entity = models.Entity.by_id(app.decode(entity_id))
    rng = general.VisibilityBasedRange(distance=30)
    if not rng.is_near(g.character, parent_entity):
        raise main.EntityTooFarAwayException(entity=parent_entity)
    exclude = [models.Entity.by_id(app.decode(parent_parent_id))] if parent_parent_id else []
    rendered = _get_entities_in(parent_entity, exclude)

    return entity_id, rendered,


@socketio_character_event("move_to_location")
def move_to_location(passage_id):
    passage_id = app.decode(passage_id)
    passage = models.Passage.by_id(passage_id)

    action = actions.MoveToLocationAction(g.character, passage)
    action.perform()

    db.session.commit()
    client_socket.emit("after_move_to_location", app.encode(passage.id))


@socketio_character_event("form_add_item_to_activity")
def form_add_item_to_activity(entity_id):
    entity_id = app.decode(entity_id)
    entity_to_add = models.Entity.by_id(entity_id)
    loc = g.character.being_in
    activity_holders = models.Entity.query.filter(models.Entity.is_in(loc)).all()

    activities = models.Activity.query.filter(models.Activity.is_in(activity_holders)).all()

    activities_to_add = []
    for activity in activities:
        if "input" in activity.requirements:
            for needed_type_name, req_data in activity.requirements["input"].items():
                needed_type = models.EntityType.by_name(needed_type_name)
                if needed_type.contains(entity_to_add.type):
                    amount = req_data["left"] / needed_type.quantity_efficiency(entity_to_add.type)
                    activities_to_add += [
                        {"id": app.encode(activity.id), "name": activity.name_tag, "amount": amount}]

    rendered = render_template("entities/modal_add_to_activity.html", activities=activities_to_add,
                               entity_to_add=entity_to_add)

    client_socket.emit("after_form_add_item_to_activity", rendered)


@socketio_character_event("add_item_to_activity")
def add_item_to_activity(entity_to_add, amount, activity_id):
    entity_to_add = models.Entity.by_id(app.decode(entity_to_add))
    activity = models.Activity.by_id(app.decode(activity_id))

    action = actions.AddEntityToActivityAction(g.character, entity_to_add, activity, amount)
    action.perform()

    db.session.commit()
    return ()


def _get_entity_info(entity):
    if isinstance(entity, models.Passage):
        entity = models.PassageToNeighbour(entity,
                                           models.PassageToNeighbour.get_other_side(entity, g.character.being_in))

    other_side = None
    if isinstance(entity, models.PassageToNeighbour):
        full_name = g.pyslate.t("entity_info",
                                other_side=entity.other_side.pyslatize(html=True, detailed=True),
                                **entity.passage.pyslatize(html=True, detailed=True))
        passage_to_neighbour = entity
        entity = passage_to_neighbour.passage
        other_side = passage_to_neighbour.other_side

    elif isinstance(entity, models.Entity):
        full_name = g.pyslate.t("entity_info", **entity.pyslatize(html=True, detailed=True))
    else:
        raise ValueError("Entity to show is of type {}".format(type(entity)))

    def has_needed_prop(action):
        if action.required_property == P.ANY:
            return True
        return entity.has_property(action.required_property)

    possible_actions = [action for action in accessible_actions.ACTIONS_ON_GROUND if
                        has_needed_prop(action) and action.other_req(entity)]

    # TODO translation
    activity = models.Activity.query.filter(models.Activity.is_in(entity)).first()

    if isinstance(entity, models.Passage):
        expandable = models.Entity.query.filter(models.Entity.is_in(other_side)) \
                         .filter(models.Entity.discriminator_type != models.ENTITY_ACTIVITY).first() is not None
        if expandable:
            expandable = general.VisibilityBasedRange(distance=30).is_near(g.character, other_side, )
    else:
        expandable = models.Entity.query.filter(models.Entity.is_in(entity)) \
                         .filter(models.Entity.discriminator_type != models.ENTITY_ACTIVITY).first() is not None

    entity_html = render_template("entities/entity_info.html", full_name=full_name, entity_id=entity.id,
                                  actions=possible_actions, activity=activity, expandable=expandable,
                                  other_side=other_side)
    return {"html": entity_html, "id": app.encode(entity.id)}


@socketio_character_event("toggle_closeable")
def toggle_closeable(entity_id):
    entity = models.Entity.by_id(app.decode(entity_id))

    action = actions.ToggleCloseableAction(g.character, entity)
    action.perform()

    db.session.commit()
    client_socket.emit("after_toggle_closeable", entity_id)


@socketio_character_event("attack_character")
def attack_character(entity_id):
    character_to_attack = models.Character.by_id(app.decode(entity_id))

    action = actions.AttackCharacterAction(g.character, character_to_attack)
    action.perform()

    db.session.commit()
    client_socket.emit("after_attack_character", entity_id)


@socketio_character_event("update_actions_list")
def update_actions_list():
    recipe_list_producer = recipes.RecipeListProducer(g.character)
    entity_recipes = models.EntityRecipe.query.all()
    enabled_entity_recipes = recipe_list_producer.get_recipe_list()
    recipe_names = [{"name": recipe.name_tag,
                     "id": app.encode(recipe.id),
                     "enabled": recipe in enabled_entity_recipes} for recipe in entity_recipes]

    return recipe_names,


@socketio_character_event("activity_from_recipe_setup")
def activity_from_recipe_setup(recipe_id):
    recipe_id = app.decode(recipe_id)
    recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

    form_inputs = recipes.ActivityFactory.get_user_inputs_for_recipe(recipe)

    errors = recipes.ActivityFactory.get_list_of_errors(recipe, g.character)
    error_messages = [g.pyslate.t(error.error_tag, **error.error_kwargs) for error in errors]

    selectable_machines = recipes.ActivityFactory.get_selectable_machines(recipe, g.character)

    rendered_modal = render_template("actions/modal_recipe_setup.html", title="recipe", form_inputs=form_inputs,
                                     recipe_id=recipe_id, selectable_machines=selectable_machines,
                                     error_messages=error_messages)
    return rendered_modal,


@socketio_character_event("create_activity_from_recipe")
def create_activity_from_recipe(recipe_id, user_input, selected_machine_id):
    recipe_id = app.decode(recipe_id)
    recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

    activitys_being_in = g.character.get_location()
    if selected_machine_id:
        selected_machine_id = app.decode(selected_machine_id)
        selected_machine = models.Item.by_id(selected_machine_id)
        rng = general.SameLocationRange()
        if not rng.is_near(g.character, selected_machine):
            raise main.EntityTooFarAwayException(entity=selected_machine)
        if models.Activity.query.filter(models.Activity.is_in(selected_machine)).first():
            raise main.ActivityAlreadyExistsOnEntity(entity=selected_machine)

        activitys_being_in = selected_machine

    activity_factory = recipes.ActivityFactory()
    form_input_type_by_name = recipes.ActivityFactory.get_user_inputs_for_recipe(recipe)

    recipe_setup_errors = activity_factory.get_list_of_errors(recipe, g.character)
    if recipe_setup_errors:
        raise recipe_setup_errors[0]

    user_input = {name: form_input_type_by_name[name].CAST_FUNCTION(value) for name, value in user_input.items()}

    activity = activity_factory.create_from_recipe(recipe, activitys_being_in, g.character, user_input=user_input)

    db.session.add_all([activity])
    db.session.commit()
    return ()
