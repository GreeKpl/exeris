import copy

from exeris.core import models, deferred, general
from exeris.core.main import db, Types
from exeris.core.properties_base import P


class ActivityFactory:
    def create_from_recipe(self, recipe, being_in, initiator, amount=1, user_input=None):

        user_input = user_input if user_input else {}

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

        container_type = self.identify_container_type(recipe)

        if container_type:
            container_type = models.ItemType.by_name(container_type)
            activity_container = models.Item(container_type, being_in, weight=0)
            if recipe.result_entity:
                activity_container.properties.append(models.EntityProperty(P.HAS_DEPENDENT,
                                                                           data={"name": recipe.result_entity.name}))
            else:
                first_action = recipe.result[0] if recipe.result else ["", {}]
                entity_type_name = Types.ITEM
                if first_action[0] == "exeris.core.actions.CreateItemAction":
                    entity_type_name = first_action[1]["item_type"]
                elif first_action[0] == "exeris.core.actions.CreateLocationAction":
                    entity_type_name = first_action[1]["location_type"]
                activity_container.properties.append(models.EntityProperty(P.HAS_DEPENDENT,
                                                                           data={"name": entity_type_name}))
            db.session.add(activity_container)

            being_in = activity_container  # it should become parent of activity

        activity = models.Activity(being_in, recipe.name_tag, recipe.name_params, all_requirements, all_ticks_needed,
                                   initiator)
        actions = self._enhance_actions(recipe.result, user_input)

        # entity_result is always the first action, because additional actions can often be some modifiers of this CIA
        activity.result_actions = self.result_actions_list_from_result_entity(recipe.result_entity, user_input)

        activity.result_actions += actions

        if container_type:
            activity.result_actions += [["exeris.core.actions.RemoveActivityContainerAction", {}]]

        db.session.add(activity)

        return activity

    def identify_container_type(self, recipe):
        container_type = None
        if recipe.activity_container == "portable_item":
            container_type = "portable_item_in_constr"
        elif recipe.activity_container == "fixed_item":
            container_type = "fixed_item_in_constr"
        elif recipe.activity_container == "entity_specific_item":
            if isinstance(recipe.result_entity, models.LocationType):
                container_type = "fixed_item_in_constr"
            elif recipe.result_entity and recipe.result_entity.portable:
                container_type = "portable_item_in_constr"
            elif recipe.result_entity:
                container_type = "fixed_item_in_constr"
            else:
                raise ValueError("don't know what entity is going to be created by {}".format(recipe))
        elif recipe.activity_container == "selected_machine":
            pass  # keep the same being_in
        return container_type

    @classmethod
    def _enhance_actions(cls, result, user_input):
        actions = []
        for action in copy.deepcopy(result):
            action_class = deferred.object_import(action[0])  # get result class by name

            if hasattr(action_class, "_form_inputs"):
                for in_name, in_data in action_class._form_inputs.items():
                    if in_name not in action[1]:  # if wasn't already set explicitly
                        action[1][in_name] = user_input[in_name]  # inject user defined form input to result dict
            actions.append(action)
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
            form_inputs.update(
                {k: v for k, v in action_and_args[0]._form_inputs.items() if
                 k not in action_and_args[1]})  # show inputs unless the parameter was already set explicitly
        return form_inputs


class RecipeListProducer:
    def __init__(self, character):
        self.character = character

    def get_recipe_list(self):
        # prefetch data
        location = self.character.get_location()

        skills = {}
        for skill_name in db.session.query(models.SkillType.name).all():
            skills[skill_name] = self.character.get_skill_factor(skill_name)

        character_position = location.get_position()

        location_type = location.type_name
        terrain_types = db.session.query(models.TerrainArea.type_name) \
            .filter(models.TerrainArea.terrain.ST_Intersects(character_position.wkt)).all()

        available_resources = db.session.query(models.ResourceArea.resource_type_name) \
            .filter(models.ResourceArea.center.ST_DWithin(character_position.wkt,
                                                          models.ResourceArea.radius)).all()

        all_recipes = models.EntityRecipe.query.all()

        def is_recipe_available(recipe):
            req = recipe.requirements
            print(req)

            if "location_types" in req:
                if location_type not in req["location_types"]:
                    return False

            if "terrain_types" in req:
                if not set(req["terrain_types"]).intersection(set(terrain_types)):
                    return False

            if "skill" in req:
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
                    machines = general.ItemQueryHelper.query_all_types_near(allowed_types, location).first()
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
    pass


class NameInput(InputField):
    CAST_FUNCTION = str


class AmountInput(InputField):
    CAST_FUNCTION = int
