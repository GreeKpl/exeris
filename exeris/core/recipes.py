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

        if recipe.activity_container and recipe.activity_container != "selected_machine":
            activity_container = self.get_container_for_activity(being_in, recipe)
            being_in = activity_container  # it should become parent of activity

        activity = models.Activity(being_in, recipe.name_tag, recipe.name_params, all_requirements, all_ticks_needed,
                                   initiator)
        all_actions = self._enhance_actions(recipe.result, user_input)

        # entity_result is always the first action, because additional actions can often be some modifiers of this CIA
        activity.result_actions = self.result_actions_list_from_result_entity(recipe.result_entity, user_input)

        activity.result_actions += all_actions

        if recipe.activity_container and recipe.activity_container != "selected_machine":
            activity.result_actions += [["exeris.core.actions.RemoveActivityContainerAction", {}]]

        db.session.add(activity)

        return activity

    def get_container_for_activity(self, being_in, recipe):

        generic_container_name = self.get_generic_activity_container(recipe)
        if generic_container_name:
            container_type = models.ItemType.by_name(generic_container_name)
        else:
            container_type = models.ItemType.by_name(recipe.activity_container)

        activity_container = models.Item(container_type, being_in, weight=0)
        db.session.add(activity_container)

        if generic_container_name:
            if recipe.result_entity:
                activity_container.properties.append(models.EntityProperty(P.HAS_DEPENDENT,
                                                                           data={
                                                                               "name": recipe.result_entity.name}))
            else:
                entity_type_name = self.get_first_entity_creation_action(recipe)
                activity_container.properties.append(models.EntityProperty(P.HAS_DEPENDENT,
                                                                           data={"name": entity_type_name}))
        return activity_container

    def get_first_entity_creation_action(self, recipe):
        first_action = recipe.result[0] if recipe.result else ["", {}]
        entity_type_name = Types.ITEM
        if first_action[0] == "exeris.core.actions.CreateItemAction":
            entity_type_name = first_action[1]["item_type"]
        elif first_action[0] == "exeris.core.actions.CreateLocationAction":
            entity_type_name = first_action[1]["location_type"]
        return entity_type_name

    def get_generic_activity_container(self, recipe):
        if recipe.activity_container == "portable_item":
            return main.Types.PORTABLE_ITEM_IN_CONSTRUCTION
        elif recipe.activity_container == "fixed_item":
            return main.Types.FIXED_ITEM_IN_CONSTRUCTION
        elif recipe.activity_container == "entity_specific_item":
            if isinstance(recipe.result_entity, models.LocationType):
                return main.Types.FIXED_ITEM_IN_CONSTRUCTION
            elif recipe.result_entity and recipe.result_entity.portable:
                return main.Types.PORTABLE_ITEM_IN_CONSTRUCTION
            elif recipe.result_entity:
                return main.Types.FIXED_ITEM_IN_CONSTRUCTION
            else:
                raise ValueError("don't know what entity is going to be created by {}".format(recipe))

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
    def get_selectable_machines(cls, recipe, character):
        mandatory_machines = recipe.requirements.get("mandatory_machines", [])
        if recipe.activity_container != "selected_machine" or not mandatory_machines:
            return []

        selectable_machine_type = mandatory_machines[0]  # first mandatory machine is the one to hold the activity
        selectable_machine_type = models.EntityType.by_name(selectable_machine_type)
        type_eff_pairs = selectable_machine_type.get_descending_types()
        allowed_types = [pair[0] for pair in type_eff_pairs]

        from exeris.core import actions
        return actions.ActivityProgress.get_all_machines_around_entity(allowed_types, character)

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

        make_error_check_if_required("terrain_type", lambda req_value:
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
                    type_eff_pairs = group.get_descending_types()
                    allowed_types = [pair[0] for pair in type_eff_pairs]
                    from exeris.core import actions
                    machines = actions.ActivityProgress.get_all_machines_around_entity(allowed_types,
                                                                                       self.character)
                    if not machines:
                        return False

            if "mandatory_tools" in req:
                for tool_type_name in req["mandatory_tools"]:
                    group = models.EntityType.by_name(tool_type_name)
                    type_eff_pairs = group.get_descending_types()
                    allowed_types = [pair[0] for pair in type_eff_pairs]

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


class AnimalResourceLevel(InputField):
    __name__ = "AnimalResourceLevel"

    def convert(self, value):
        return None

    @classmethod
    def has_input(cls):
        return False
