import copy
import math

from exeris.core import models, deferred
from exeris.core.main import db


__author__ = 'alek'


class ActivityFactory:
    def create_from_recipe(self, recipe, being_in, initiator, amount=1, user_input=None):

        user_input = user_input if user_input else {}

        all_requirements = {}
        for req in recipe.requirements:
            if req == "input":
                all_requirements[req] = {k: math.ceil(v * amount) for (k, v) in recipe.requirements[req].items()}
            else:
                all_requirements[req] = recipe.requirements[req]

        all_ticks_needed = recipe.ticks_needed * amount

        print(being_in, recipe.requirements, all_ticks_needed, initiator)
        activity = models.Activity(being_in, recipe.requirements, all_ticks_needed, initiator)

        db.session.add(activity)

        actions = self._enhance_actions(recipe.result, user_input)
        activity.result_actions = actions
        activity.result_actions += self.result_actions_list_from_result_entity(recipe.result_entity, user_input)

        return activity

    @classmethod
    def _enhance_actions(cls, result, user_input):
        actions = []
        for action in copy.deepcopy(result):
            action_object = deferred.object_import(action[0])

            if hasattr(action_object, "_form_inputs"):
                for in_name, in_data in action_object._form_inputs.items():
                    action[1][in_name] = user_input[in_name]
            actions.append(action)
        return actions

    @classmethod
    def result_actions_list_from_result_entity(cls, entity_type, user_input):
        if entity_type is None:
            return []
        elif type(entity_type) is models.ItemType:
            standard_actions = [["exeris.core.actions.CreateItemAction",
                                 {"item_type": entity_type.name, "properties": {}, "used_materials": "all"}]]
            return cls._enhance_actions(standard_actions, user_input)  # TODO
