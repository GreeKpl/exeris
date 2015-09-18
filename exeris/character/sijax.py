import time

from flask import g, render_template

from exeris.core import models, actions, accessible_actions, recipes
from exeris.core.main import db, app


class GlobalMixin:
    @staticmethod
    def rename_entity(obj_response, character_id, new_name):
        character_id = app.decode(character_id)

        entity_to_rename = models.Entity.by_id(character_id)
        entity_to_rename.set_dynamic_name(g.character, new_name)

        obj_response.call("FRAGMENTS.character.after_rename_entity", [app.encode(character_id)])
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

        action = actions.SpeakToSomebody(g.character, receiver, message)
        action.perform()

        obj_response.call("FRAGMENTS.speaking.after_say_to_somebody", [])
        db.session.commit()

    @staticmethod
    def whisper(obj_response, receiver_id, message):
        receiver_id = app.decode(receiver_id)
        receiver = models.Character.by_id(receiver_id)

        action = actions.WhisperToSomebody(g.character, receiver, message)
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
        events_texts = [g.pyslate.t(event.type_name, html=True, **event.params) for event in events]

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
    def get_entities_in(parent_entity, exclude=None):
        exclude = exclude if exclude else []

        entities = models.Entity.query.filter(models.Entity.is_in(parent_entity)) \
            .filter(~models.Entity.id.in_([e.id for e in exclude])).all()

        if isinstance(parent_entity, models.Location):
            entities += [passage.other_side for passage in parent_entity.passages_to_neighbours]

        entity_entries = []
        for entity in entities:
            full_name = g.pyslate.t("entity_info", **entity.pyslatize(html=True, detailed=True))

            def has_needed_prop(action):
                return entity.has_property(action.required_property)

            possible_actions = [action for action in accessible_actions.ACTIONS_ON_GROUND if has_needed_prop(action)]

            # TODO translation

            activity = models.Activity.query.filter(models.Activity.is_in(entity)).first()

            entity_html = render_template("entities/entity_info.html", full_name=full_name, entity_id=entity.id,
                                          actions=possible_actions, activity=activity)
            has_children = models.Entity.query.filter(models.Entity.is_in(entity)) \
                               .filter(models.Entity.discriminator_type != models.ENTITY_ACTIVITY).first() is not None
            entity_entries.append({"html": entity_html, "has_children": has_children, "children": []})

        return entity_entries

    @staticmethod
    def entities_refresh_list(obj_response):
        location = g.character.being_in

        entity_entries = EntitiesPage.get_entities_in(location)
        obj_response.call("FRAGMENTS.entities.after_refresh_list", [entity_entries])

    @staticmethod
    def move_to_location(obj_response, to_loc_id):
        to_loc_id = app.decode(to_loc_id)
        loc = models.Location.by_id(to_loc_id)

        passage = models.Passage.query.filter(models.Passage.between(g.character.being_in, loc)).one()

        action = actions.MoveToLocationAction(g.character, loc, passage)
        action.perform()

        db.session.commit()
        obj_response.call("FRAGMENTS.entities.after_move_to_location", [app.encode(loc.id)])


class MapPage(GlobalMixin):
    pass


class ActionsPage(GlobalMixin, ActivityMixin):
    @staticmethod
    def update_actions_list(obj_response):
        recipes = models.EntityRecipe.query.all()
        recipe_names = [{"name": recipe.name_tag, "id": app.encode(recipe.id)} for recipe in recipes]
        obj_response.call("FRAGMENTS.actions.after_update_actions_list", [recipe_names])

    @staticmethod
    def create_activity_from_recipe(obj_response, recipe_id):
        recipe_id = app.decode(recipe_id)
        recipe = models.EntityRecipe.query.filter_by(id=recipe_id).one()

        activity_factory = recipes.ActivityFactory()

        activity = activity_factory.create_from_recipe(recipe, g.character.being_in, g.character)

        db.session.add_all([activity])
        obj_response.call("FRAGMENTS.actions.after_create_activity_from_recipe", [])
        db.session.commit()
