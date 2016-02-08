import copy
import math

from exeris.core import models, deferred
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

        activity = models.Activity(being_in, recipe.name_tag, recipe.name_params, all_requirements, all_ticks_needed, initiator)
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
                    action[1][in_name] = user_input[in_name]  # inject user defined form input to result dict
            actions.append(action)
        return actions

    @classmethod
    def result_actions_list_from_result_entity(cls, entity_type, user_input):
        if entity_type is None:
            return []
        elif isinstance(entity_type, models.ItemType):
            standard_actions = [["exeris.core.actions.CreateItemAction",
                                 {"item_type": entity_type.name, "properties": {}, "used_materials": "all"}]]
            return cls._enhance_actions(standard_actions, user_input)
        elif isinstance(entity_type, models.LocationType):
            standard_actions = [["exeris.core.actions.CreateLocationAction",
                                 {"location_type": entity_type.name, "properties": {}, "used_materials": "all"}]]
            return cls._enhance_actions(standard_actions, user_input)
