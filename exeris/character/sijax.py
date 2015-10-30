import time

from flask import g, render_template

from exeris.core import models, actions, accessible_actions, recipes, deferred, general, main
from exeris.core.main import db, app


class GlobalMixin:
    @staticmethod
    def rename_entity(obj_response, entity_id, new_name):
        entity_id = app.decode(entity_id)
        entity_to_rename = models.Entity.by_id(entity_id)

        entity_to_rename.set_dynamic_name(g.character, new_name)

        obj_response.call("FRAGMENTS.character.after_rename_entity", [app.encode(entity_id)])
        db.session.commit()

    @staticmethod
    def get_entity_tag(obj_response, entity_id):
        entity_id = app.decode(entity_id)

        entity = models.Entity.by_id(entity_id)
        text = g.pyslate.t("entity_info", html=True, **entity.pyslatize())

        obj_response.call("FRAGMENTS.character.after_get_entity_tag", [app.encode(entity_id), text])

    @staticmethod
    def update_top_bar(obj_response):
        activity = g.character.activity
        if not activity:
            msg = "not working"
        else:
            msg = "{} - {} / {}".format(activity.name_tag, activity.ticks_needed - activity.ticks_left,
                                        activity.ticks_needed)
        rendered = render_template("character_top_bar.html", activity_name=msg)
        obj_response.call("FRAGMENTS.top_bar.after_update_top_bar", [rendered])


class SpeakingMixin:
    @staticmethod
    def speaking_form_refresh(obj_response, message_type, receiver=None):
        if receiver:
            receiver = app.decode(receiver)
            receiver = models.Character.by_id(receiver)

        rendered = render_template("events/speaking.html", message_type=message_type, receiver=receiver)

        obj_response.call("FRAGMENTS.speaking.after_speaking_form_refresh", [rendered])

    @staticmethod
    def say_aloud(obj_response, message):
        action = actions.SayAloudAction(g.character, message)
        action.perform()

        obj_response.call("FRAGMENTS.speaking.after_say_aloud", [])
        db.session.commit()

    @staticmethod
    def say_to_somebody(obj_response, receiver_id, message):
        receiver_id = app.decode(receiver_id)
        receiver = models.Character.by_id(receiver_id)

        action = actions.SpeakToSomebodyAction(g.character, receiver, message)
        action.perform()

        obj_response.call("FRAGMENTS.speaking.after_say_to_somebody", [])
        db.session.commit()

    @staticmethod
    def whisper(obj_response, receiver_id, message):
        receiver_id = app.decode(receiver_id)
        receiver = models.Character.by_id(receiver_id)

        action = actions.WhisperToSomebodyAction(g.character, receiver, message)
        action.perform()

        obj_response.call("FRAGMENTS.speaking.after_whisper", [])
        db.session.commit()


class ActivityMixin:
    @staticmethod
    def get_activity_info(obj_response):
        pass

    @staticmethod
    def join_activity(obj_response, activity_id):
        activity_id = app.decode(activity_id)

        activity = models.Activity.by_id(activity_id)
        action = actions.JoinActivityAction(g.character, activity)
        action.perform()

        obj_response.call("FRAGMENTS.activity.after_join", [])
        db.session.commit()


class EventsPage(GlobalMixin, SpeakingMixin, ActivityMixin):
    @staticmethod
    def get_new_events(obj_response, last_event):
        start = time.time()
        events = db.session.query(models.Event).join(models.EventObserver).filter_by(observer=g.character) \
            .filter(models.Event.id > last_event).order_by(models.Event.id.asc()).all()

        queried = time.time()
        print("query: ", queried - start)
        last_event_id = events[-1].id if len(events) else last_event
        events_texts = [g.pyslate.t("game_date", game_date=event.date) + ": " + g.pyslate.t(event.type_name, html=True,
                                                                                            **event.params) for event in
                        events]

        tran = time.time()
        print("translations:", tran - queried)
        events_texts = [event for event in events_texts]
        all = time.time()
        print("esc: ", all - tran)
        obj_response.call("FRAGMENTS.events.update_list", [events_texts, last_event_id])
        db.session.commit()

    @staticmethod
    def people_short_refresh_list(obj_response):
        chars = models.Character.query.all()
        rendered = render_template("events/people_short.html", chars=chars)

        obj_response.call("FRAGMENTS.people_short.after_refresh_list", [rendered])
        db.session.commit()


class EntityActionMixin:
    @staticmethod
    def eat(obj_response, entity_id, amount=None):
        entity_id = app.decode(entity_id)
        entity = models.Item.by_id(entity_id)

        if not amount:
            obj_response.call("FRAGMENTS.entities.before_eat",
                              [app.encode(entity_id), entity.get_max_edible(g.character)])
        else:
            eat_action = actions.EatAction(g.character, entity, amount)
            eat_action.perform()
            entity_info = g.pyslate.t("entity_info", **entity.pyslatize(item_amount=amount))

            obj_response.call("FRAGMENTS.entities.after_eat", [entity_info, amount])
            db.session.commit()

    @staticmethod
    def open_readable_contents(obj_response, entity_id):
        entity_id = app.decode(entity_id)
        entity = models.Entity.by_id(entity_id)

        title = entity.read_title()
        contents = entity.read_contents()
        raw_contents = entity.read_raw_contents()
        modal = render_template("entities/modal_readable.html", title=title, contents=contents, entity_id=entity_id,
                                raw_contents=raw_contents)

        obj_response.call("FRAGMENTS.entities.after_open_readable_contents", [modal])

    @staticmethod
    def edit_readable(obj_response, entity_id, text):
        entity_id = app.decode(entity_id)
        entity = models.Entity.by_id(entity_id)

        entity.alter_contents("title", text, models.TextContent.FORMAT_MD)

        obj_response.call("FRAGMENTS.entities.after_edit_readable", [app.encode(entity_id)])
        db.session.commit()


class EntitiesPage(GlobalMixin, EntityActionMixin, ActivityMixin):
    @staticmethod
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
            entity_info = EntitiesPage._get_entity_info(entity)

            entity_entries.append(entity_info)
        return entity_entries

    @staticmethod
    def collapse_entity(obj_response, parent_entity_id):
        parent_entity = models.Entity.by_id(app.decode(parent_entity_id))
        pref = models.EntityContentsPreference.query.filter_by(character=g.character, open_entity=parent_entity).first()
        if pref:
            db.session.delete(pref)
        obj_response.call("FRAGMENTS.entities.after_collapse_entity", [parent_entity_id])

        db.session.commit()

    @staticmethod
    def entities_refresh_list(obj_response):
        location = g.character.being_in

        rng = general.VisibilityBasedRange(distance=30, only_through_unlimited=False)
        if isinstance(location, models.RootLocation):
            displayed_locations = rng.root_locations_near(location)
        else:
            displayed_locations = [location]

        locations = [EntitiesPage._get_entity_info(loc_to_show) for loc_to_show in displayed_locations]
        obj_response.call("FRAGMENTS.entities.after_refresh_list", [locations])

    @staticmethod
    def refresh_entity_info(obj_response, entity_id):
        entity_id = app.decode(entity_id)
        entity = models.Entity.by_id(entity_id)

        entity_info = EntitiesPage._get_entity_info(entity)
        obj_response.call("FRAGMENTS.entities.after_refresh_entity_info", [entity_info])

    @staticmethod
    def entities_get_sublist(obj_response, entity_id, parent_parent_id):
        parent_entity = models.Entity.by_id(app.decode(entity_id))
        rng = general.VisibilityBasedRange(distance=30)
        if not rng.is_near(g.character, parent_entity):
            raise main.EntityTooFarAwayException(entity=parent_entity)
        exclude = [models.Entity.by_id(app.decode(parent_parent_id))] if parent_parent_id else []
        rendered = EntitiesPage._get_entities_in(parent_entity, exclude)

        obj_response.call("FRAGMENTS.entities.after_entities_get_sublist", [entity_id, rendered])

    @staticmethod
    def move_to_location(obj_response, passage_id):
        passage_id = app.decode(passage_id)
        passage = models.Passage.by_id(passage_id)

        action = actions.MoveToLocationAction(g.character, passage)
        action.perform()

        db.session.commit()
        obj_response.call("FRAGMENTS.entities.after_move_to_location", [app.encode(passage.id)])

    @staticmethod
    def form_add_item_to_activity(obj_response, entity_id):
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

        obj_response.call("FRAGMENTS.entities.after_form_add_item_to_activity", [rendered])

    @staticmethod
    def add_item_to_activity(obj_response, entity_to_add, amount, activity_id):
        entity_to_add = models.Entity.by_id(app.decode(entity_to_add))
        activity = models.Activity.by_id(app.decode(activity_id))

        action = actions.AddEntityToActivityAction(g.character, entity_to_add, activity, amount)
        action.perform()

        obj_response.call("FRAGMENTS.entities.after_add_item_to_activity", [])
        db.session.commit()

    @staticmethod
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

    @staticmethod
    def toggle_closeable(obj_response, entity_id):
        entity = models.Entity.by_id(app.decode(entity_id))

        action = actions.ToggleCloseableAction(g.character, entity)
        action.perform()

        obj_response.call("FRAGMENTS.entities.after_toggle_closeable", [entity_id])
        db.session.commit()


class MapPage(GlobalMixin):
    pass


class ActionsPage(GlobalMixin, ActivityMixin):
    @staticmethod
    def update_actions_list(obj_response):
        entity_recipes = models.EntityRecipe.query.all()
        recipe_names = [{"name": recipe.name_tag, "id": app.encode(recipe.id)} for recipe in entity_recipes]
        obj_response.call("FRAGMENTS.actions.after_update_actions_list", [recipe_names])

    @staticmethod
    def activity_from_recipe_setup(obj_response, recipe_id):
        recipe_id = app.decode(recipe_id)
        recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

        actions_requiring_input = [deferred.object_import(x[0]) for x in recipe.result]
        actions_requiring_input = [x for x in actions_requiring_input if hasattr(x, "_form_inputs")]

        form_inputs = {}
        for i in actions_requiring_input:
            form_inputs.update({k: v.__name__ for k, v in i._form_inputs.items()})

        rendered_modal = render_template("actions/modal_recipe_setup.html", title="recipe", form_inputs=form_inputs,
                                         recipe_id=recipe_id)
        obj_response.call("FRAGMENTS.actions.after_activity_from_recipe_setup", [rendered_modal])

    @staticmethod
    def create_activity_from_recipe(obj_response, recipe_id, user_input):
        recipe_id = app.decode(recipe_id)
        recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

        activity_factory = recipes.ActivityFactory()

        activity = activity_factory.create_from_recipe(recipe, g.character.being_in, g.character, user_input=user_input)

        db.session.add_all([activity])
        obj_response.call("FRAGMENTS.actions.after_create_activity_from_recipe", [])
        db.session.commit()
