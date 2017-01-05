import copy

from exeris.core import models, deferred, general, main
from exeris.core import properties
from exeris.core.main import db, Types
from exeris.core.properties_base import P


class ActivityFactory:
    def create_from_recipe(self, recipe, being_in, initiator, user_input=None):

        user_input = user_input if user_input else {}

        amount = 1
        if "amount" in user_input:
            amount = user_input["amount"]

        all_requirements = {}
        for req in recipe.requirements:
            if req == "input":
                input_req = {}
                for req_type, req_amount in recipe.requirements[req].items():
                    input_req[req_type] = {"needed": req_amount * amount, "left": req_amount * amount}
                all_requirements[req] = input_req
            else:
                all_requirements[req] = recipe.requirements[req]

        all_ticks_needed = recipe.ticks_needed * amount

        if self.is_creating_activity_container(recipe):
            being_in = self.create_container_for_activity(being_in, recipe)  # it should become a parent of activity
        else:
            self.check_correctness_of_selected_activity_container(being_in, recipe.activity_container, recipe)

        activity = models.Activity(being_in, recipe.name_tag, recipe.name_params, all_requirements, all_ticks_needed,
                                   initiator)
        all_actions = self._enhance_actions(recipe.result, user_input)

        # entity_result is always the first action, because additional actions can often be some modifiers of this CIA
        activity.result_actions = self.result_actions_list_from_result_entity(recipe.result_entity, user_input)

        activity.result_actions += all_actions

        if self.is_creating_activity_container(recipe):
            activity.result_actions += [["exeris.core.actions.RemoveActivityContainerAction", {}]]

        db.session.add(activity)

        return activity

    def create_container_for_activity(self, being_in, recipe):
        container_type = self.get_activity_container_type(recipe)

        activity_container = models.Item(container_type, being_in, weight=0)
        db.session.add(activity_container)

        entity_type_name = self.get_result_entity_type(recipe)
        activity_container.properties.append(models.EntityProperty(P.HAS_DEPENDENT, data={"name": entity_type_name}))
        return activity_container

    def get_activity_container_type(self, recipe):
        generic_container_name = self.get_generic_activity_container(recipe)
        if generic_container_name:
            return models.ItemType.by_name(generic_container_name)
        elif recipe.activity_container[0] == "new_entity":
            return models.ItemType.by_name(recipe.activity_container[1])
        else:
            raise ValueError("something has broken")

    def get_result_entity_type(self, recipe):
        if recipe.result_entity:
            return recipe.result_entity.name
        return self.get_first_entity_creation_action(recipe)

    def get_first_entity_creation_action(self, recipe):
        first_action = recipe.result[0] if recipe.result else ["", {}]
        entity_type_name = Types.ITEM
        if first_action[0] == "exeris.core.actions.CreateItemAction":
            entity_type_name = first_action[1]["item_type"]
        elif first_action[0] == "exeris.core.actions.CreateLocationAction":
            entity_type_name = first_action[1]["location_type"]
        return entity_type_name

    def get_generic_activity_container(self, recipe):
        activity_container = recipe.activity_container[0]
        if activity_container == "entity_specific_item":
            activity_container = self.get_concrete_entity_specific_container(recipe)
        if activity_container == "portable_item":
            return main.Types.PORTABLE_ITEM_IN_CONSTRUCTION
        elif activity_container == "fixed_item":
            return main.Types.FIXED_ITEM_IN_CONSTRUCTION
        else:
            return None

    def get_concrete_entity_specific_container(self, recipe):
        result_entity_type = models.EntityType.by_name(self.get_result_entity_type(recipe))
        if isinstance(result_entity_type, models.LocationType):
            return "fixed_item"
        elif result_entity_type and result_entity_type.portable:
            return "portable_item"
        elif result_entity_type:
            return "fixed_item"
        else:
            raise ValueError("don't know what entity is going to be created by {}".format(recipe))

    @classmethod
    def is_creating_activity_container(cls, recipe):
        return recipe.activity_container[0] != "selected_entity"

    @classmethod
    def check_correctness_of_selected_activity_container(cls, entity_containing_activity,
                                                         activity_container_spec, recipe):
        if activity_container_spec[0] != "selected_entity":
            raise ValueError("recipe activity container definition '{}' is not 'selected_entity'"
                             .format(activity_container_spec))
        activity_container_params = activity_container_spec[1]
        if "types" in activity_container_params:
            if not any([models.EntityType.by_name(type_name).contains(entity_containing_activity.type)
                        for type_name in activity_container_params["types"]]):
                cls.raise_activity_container_exception(recipe, entity_containing_activity)
        if "properties" in activity_container_params:
            for property_name, property_dict in activity_container_params["properties"].items():
                if not entity_containing_activity.has_property(property_name, **property_dict):
                    cls.raise_activity_container_exception(recipe, entity_containing_activity)
        if "no_properties" in activity_container_params:
            for property_name, property_dict in activity_container_params["no_properties"].items():
                if entity_containing_activity.has_property(property_name, **property_dict):
                    cls.raise_activity_container_exception(recipe, entity_containing_activity)

    @classmethod
    def raise_activity_container_exception(cls, recipe, activity_container):
        raise main.InvalidActivityContainerException(recipe_name_tag=recipe.name_tag,
                                                     recipe_name_params=recipe.name_params,
                                                     activity_container=activity_container)

    @classmethod
    def _enhance_actions(cls, result, user_input):
        actions = []

        for action_name, action_args in result:
            action_args = copy.deepcopy(action_args)
            action_class = deferred.object_import(action_name)  # get result class by name
            if hasattr(action_class, "_form_inputs"):
                for input_name, input_class in action_class._form_inputs.items():
                    # if user_input wasn't already set explicitly
                    if input_name not in action_args and input_class.has_input():
                        action_args[input_name] = user_input[input_name]  # inject user form input to result dict
            actions.append([action_name, action_args])
        return actions

    @classmethod
    def result_actions_list_from_result_entity(cls, entity_type, user_input):
        if entity_type is None:
            return []
        result_entity_action = ActivityFactory.action_from_result_entity(entity_type)
        if result_entity_action:
            return cls._enhance_actions([result_entity_action], user_input)

    @classmethod
    def action_from_result_entity(cls, entity_type):
        if isinstance(entity_type, models.ItemType):
            return ["exeris.core.actions.CreateItemAction",
                    {"item_type": entity_type.name, "properties": {}, "used_materials": "all"}]
        elif isinstance(entity_type, models.LocationType):
            return ["exeris.core.actions.CreateLocationAction",
                    {"location_type": entity_type.name, "properties": {}, "used_materials": "all"}]
        return None

    @classmethod
    def get_user_inputs_for_recipe(cls, recipe):
        result_actions_and_args = [(deferred.object_import(x[0]), x[1]) for x in recipe.result]
        result_actions_requiring_input = [x for x in result_actions_and_args if hasattr(x[0], "_form_inputs")]
        if recipe.result_entity:
            result_entity_action_and_args = ActivityFactory.action_from_result_entity(recipe.result_entity)
            result_entity_action_and_args[0] = deferred.object_import(result_entity_action_and_args[0])
            if hasattr(result_entity_action_and_args[0], "_form_inputs"):
                result_actions_requiring_input.append(result_entity_action_and_args)

        form_inputs = {}
        for action_and_args in result_actions_requiring_input:
            # show inputs unless the parameter was already set explicitly
            form_inputs.update(
                {input_field_name: ActivityFactory._input_field_for_action(field_class, action_and_args)
                 for input_field_name, field_class in action_and_args[0]._form_inputs.items()
                 if input_field_name not in action_and_args[1]})
        return form_inputs

    @staticmethod
    def _input_field_for_action(field_class, action_and_args):
        return field_class(deferred.get_qualified_class_name(action_and_args[0]), action_and_args[1])

    @classmethod
    def get_selectable_entities(cls, recipe, character):
        activity_container_spec = recipe.activity_container
        if activity_container_spec[0] != "selected_entity":
            return []

        allowed_types = []
        for type_name in activity_container_spec[1].get("types", []):
            descending_types = models.EntityType.by_name(type_name).get_descending_types()
            allowed_types += [subtype.name for subtype, eff in descending_types]

        # items
        item_query_parts = cls.property_related_query_parts(activity_container_spec, models.Item)
        if allowed_types:
            item_query_parts += [models.Item.type_name.in_(allowed_types)]
        items = models.Item.query.filter(models.Item.is_in(character.parent_locations()),
                                         *item_query_parts).all()

        # locations
        location_ids = models.ids(character.parent_locations())
        for loc in character.parent_locations():
            location_ids += [directed_passage.other_side.id for directed_passage in loc.passages_to_neighbours
                             if directed_passage.passage.is_accessible(False)]

        loc_query_parts = cls.property_related_query_parts(activity_container_spec, models.Location)
        if allowed_types:
            loc_query_parts += [models.Location.type_name.in_(allowed_types)]

        locations = models.Location.query.filter(models.Location.id.in_(location_ids),
                                                 *loc_query_parts).all()

        # passages
        passage_ids = []
        for loc in character.parent_locations():
            passage_ids += [directed_passage.passage.id for directed_passage in loc.passages_to_neighbours
                            if directed_passage.passage.is_accessible(False)]

        passage_query_parts = cls.property_related_query_parts(activity_container_spec, models.Passage)
        if allowed_types:
            passage_query_parts += [models.Passage.type_name.in_(allowed_types)]

        passages = []
        if passage_ids:
            passages = models.Passage.query.filter(models.Passage.id.in_(passage_ids),
                                                   *passage_query_parts).all()

        return items + locations + passages

    @classmethod
    def property_related_query_parts(cls, activity_container_spec, entity_class):
        property_query_parts = []
        for property_name, property_dict in activity_container_spec[1].get("properties", {}).items():
            property_query_parts += [entity_class.has_property(property_name, **property_dict)]
        for property_name, property_dict in activity_container_spec[1].get("no_properties", {}).items():
            property_query_parts += [~entity_class.has_property(property_name, **property_dict)]
        return property_query_parts

    @classmethod
    def get_list_of_errors(cls, recipe, character):
        req = recipe.requirements

        errors = []

        def make_error_check_if_required(req_key, check_function):
            try:
                if req_key in req:
                    check_function(req[req_key])
            except main.GameException as exception:
                errors.append(exception)

        from exeris.core import actions
        make_error_check_if_required("mandatory_machines", lambda req_value:
        actions.ActivityProgress.check_mandatory_machines(req_value, character, {}))

        make_error_check_if_required("targets", lambda req_value:
        actions.ActivityProgress.check_target_proximity(req_value, character.get_location()))

        make_error_check_if_required("required_resources", lambda req_value:
        actions.ActivityProgress.check_required_resources(req_value, character.get_location()))

        make_error_check_if_required("location_types", lambda req_value:
        actions.ActivityProgress.check_location_types(req_value, character.get_location()))

        make_error_check_if_required("terrain_types", lambda req_value:
        actions.ActivityProgress.check_terrain_types(req_value, character.get_location()))

        make_error_check_if_required("excluded_by_entities", lambda req_value:
        actions.ActivityProgress.check_excluded_by_entities(req_value, character.get_location()))

        make_error_check_if_required("mandatory_tools", lambda req_value:
        actions.ActivityProgress.check_mandatory_tools(character, req_value, {}))

        make_error_check_if_required("skills", lambda req_value:
        actions.ActivityProgress.check_skills(character, req_value, {}))

        make_error_check_if_required("permanence", lambda req_value:
        actions.ActivityProgress.check_permanence_of_location(character.get_location()))

        return errors


class RecipeListProducer:
    def __init__(self, character):
        self.character = character

    def get_recipe_list(self):
        # prefetch data
        location = self.character.get_location()

        skills = {}
        for (skill_name,) in db.session.query(models.SkillType.name).all():
            skills_property = properties.SkillsProperty(self.character)
            skills[skill_name] = skills_property.get_skill_factor(skill_name)

        character_position = location.get_position()

        location_type = location.type_name
        terrain_types = db.session.query(models.TerrainArea.type_name) \
            .filter(models.TerrainArea.terrain.ST_Intersects(character_position.wkt)).all()
        terrain_types = [terain_type[0] for terain_type in terrain_types]

        available_resources = db.session.query(models.ResourceArea.resource_type_name) \
            .filter(models.ResourceArea.center.ST_DWithin(character_position.wkt, models.ResourceArea.radius)).all()
        available_resources = [resource[0] for resource in available_resources]

        can_be_permanent = location.get_root().can_be_permanent()

        all_recipes = models.EntityRecipe.query.all()

        def is_recipe_available(recipe):
            req = recipe.requirements

            if "location_types" in req:
                if location_type not in req["location_types"]:
                    return False

            if "terrain_types" in req:
                if not set(req["terrain_types"]).intersection(set(terrain_types)):
                    return False

            if "permanence" in req:
                if not can_be_permanent:
                    return False

            if "skills" in req:
                for skill_name, min_skill_value in req["skills"]:
                    if skills[skill_name] < min_skill_value:
                        return False

            if "required_resources" in req:
                if not set(req["required_resources"]).intersection(set(available_resources)):
                    return False

            if "mandatory_machines" in req:
                for machine_name in req["mandatory_machines"]:
                    group = models.EntityType.by_name(machine_name)
                    allowed_types = models.get_concrete_types_for_groups([group])

                    from exeris.core import actions
                    machines = actions.ActivityProgress.get_all_machines_around_entity(allowed_types,
                                                                                       self.character)
                    if not machines:
                        return False

            if "mandatory_tools" in req:
                for tool_type_name in req["mandatory_tools"]:
                    group = models.EntityType.by_name(tool_type_name)
                    allowed_types = models.get_concrete_types_for_groups([group])

                    tools = general.ItemQueryHelper.query_all_types_in(allowed_types, self.character).first()
                    if not tools:
                        return False

            return True

        return [recipe for recipe in all_recipes if is_recipe_available(recipe)]


class InputField:
    __name__ = "InputField"

    def __init__(self, action_name, action_args):
        self.action_name = action_name
        self.action_args = action_args

    @classmethod
    def has_input(cls):
        return True

    def convert(self, value):
        pass


class NameInput(InputField):
    __name__ = "NameInput"

    def convert(self, value):
        return value


class AmountInput(InputField):
    __name__ = "AmountInput"

    def convert(self, value):
        return int(value)


class WorkDaysInput(InputField):
    __name__ = "WorkDaysInput"

    def convert(self, value):
        return float(value)


class AnimalResourceLevel(InputField):
    __name__ = "AnimalResourceLevel"

    def convert(self, value):
        return None

    @classmethod
    def has_input(cls):
        return False
