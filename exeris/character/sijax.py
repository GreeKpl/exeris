import time

from exeris.app import socketio, socketio_character_event
from flask import g, render_template
from sqlalchemy import sql

from exeris.core import models, actions, accessible_actions, recipes, deferred, general, main
from exeris.core.main import db, app


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
    activity = g.character.activity
    if not activity:
        msg = "not working"
    else:
        msg = "{} - {} / {}".format(activity.name_tag, activity.ticks_needed - activity.ticks_left,
                                    activity.ticks_needed)
    rendered = render_template("character_top_bar.html", activity_name=msg, endpoint_name=endpoint_name)
    return rendered,


@socketio_character_event("get_notifications_list")
def get_notifications_list():
    notifications = models.Notification.query.filter(
        sql.or_(models.Notification.character == g.character, models.Notification.player == g.player)).all()

    notification_titles = [{"notification_id": n.id, "title": g.pyslate.t(n.title_tag, **n.title_params)}
                           for n in notifications]
    return notification_titles,


@socketio_character_event("show_notification_dialog")
def show_notification_dialog(notification_id):
    notification = models.Notification.query.filter_by(id=notification_id).filter(
        sql.or_(models.Notification.character == g.character, models.Notification.player == g.player)).one()
    rendered = render_template("modal_notification.html", notification=notification)
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
    action.perform()

    db.session.commit()
    return ()


@socketio_character_event("get_new_events")
def get_new_events(last_event):
    start = time.time()
    events = db.session.query(models.Event).join(models.EventObserver).filter_by(observer=g.character) \
        .filter(models.Event.id > last_event).order_by(models.Event.id.asc()).all()

    queried = time.time()
    print("query: ", queried - start)
    last_event_id = events[-1].id if len(events) else last_event
    events_texts = [g.pyslate.t("game_date", game_date=event.date) + ": " +
                    g.pyslate.t(event.type_name, html=True, **event.params) for event in events]

    tran = time.time()
    print("translations:", tran - queried)
    events_texts = [event for event in events_texts]
    all = time.time()
    print("esc: ", all - tran)
    db.session.commit()
    return events_texts, last_event_id


@socketio_character_event("people_short_refresh_list")
def people_short_refresh_list():
    chars = models.Character.query.all()
    rendered = render_template("events/people_short.html", chars=chars)

    db.session.commit()
    return rendered,


@socketio_character_event("eat")
def eat(entity_id, amount=None):
    entity_id = app.decode(entity_id)
    entity = models.Item.by_id(entity_id)

    if not amount:
        socketio.emit("before_eat", (app.encode(entity_id), entity.get_max_edible(g.character)))
    else:
        eat_action = actions.EatAction(g.character, entity, amount)
        eat_action.perform()
        entity_info = g.pyslate.t("entity_info", **entity.pyslatize(item_amount=amount))

        db.session.commit()
        return entity_info, amount


@socketio_character_event("open_readable_contents")
def open_readable_contents(entity_id):
    entity_id = app.decode(entity_id)
    entity = models.Entity.by_id(entity_id)

    title = entity.read_title()
    contents = entity.read_contents()
    raw_contents = entity.read_raw_contents()
    modal = render_template("entities/modal_readable.html", title=title, contents=contents, entity_id=entity_id,
                            raw_contents=raw_contents)
    socketio.emit("after_open_readable_contents", modal)


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
def entities_refresh_list():
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
    socketio.emit("after_move_to_location", app.encode(passage.id))


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
                    amount = req_data["left"] / needed_type.efficiency(entity_to_add.type)
                    activities_to_add += [
                        {"id": app.encode(activity.id), "name": activity.name_tag, "amount": amount}]

    rendered = render_template("entities/modal_add_to_activity.html", activities=activities_to_add,
                               entity_to_add=entity_to_add)

    socketio.emit("after_form_add_item_to_activity", rendered)


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

    else:
        full_name = g.pyslate.t("entity_info", **entity.pyslatize(html=True, detailed=True))

    def has_needed_prop(action):
        if action.required_property == "any":
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
    socketio.emit("after_toggle_closeable", entity_id)


@socketio_character_event("update_actions_list")
def update_actions_list():
    entity_recipes = models.EntityRecipe.query.all()
    recipe_names = [{"name": recipe.name_tag, "id": app.encode(recipe.id)} for recipe in entity_recipes]

    return recipe_names,


@socketio_character_event("activity_from_recipe_setup")
def activity_from_recipe_setup(recipe_id):
    recipe_id = app.decode(recipe_id)
    recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

    actions_requiring_input = [deferred.object_import(x[0]) for x in recipe.result]
    actions_requiring_input = [x for x in actions_requiring_input if hasattr(x, "_form_inputs")]

    form_inputs = {}
    for i in actions_requiring_input:
        form_inputs.update({k: v.__name__ for k, v in i._form_inputs.items()})

    rendered_modal = render_template("actions/modal_recipe_setup.html", title="recipe", form_inputs=form_inputs,
                                     recipe_id=recipe_id)
    return rendered_modal,


@socketio_character_event("create_activity_from_recipe")
def create_activity_from_recipe(recipe_id, user_input):
    recipe_id = app.decode(recipe_id)
    recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

    activity_factory = recipes.ActivityFactory()

    activity = activity_factory.create_from_recipe(recipe, g.character.being_in, g.character, user_input=user_input)

    db.session.add_all([activity])
    db.session.commit()
    return ()
