import math
from exeris.core import models, deferred, actions
from exeris.core.main import db

__author__ = 'alek'


class ActivityFactory:
    def create_from_recipe(self, recipe, being_in, amount=1):

        all_requirements = {}
        for req in recipe.requirements:
            if req == "input":
                all_requirements[req] = {k: math.ceil(v * amount) for (k, v) in recipe.requirements[req].items()}
            else:
                all_requirements[req] = recipe.requirements[req]

        all_ticks_needed = recipe.ticks_needed * amount

        activity = models.Activity(being_in, recipe.requirements, all_ticks_needed)

        db.session.add(activity)
        db.session.flush()

        activity.result_actions = recipe.result
        activity.result_actions += self.result_actions_list_from_result_entity(recipe.result_entity, activity)

        return activity

    @staticmethod
    def result_actions_list_from_result_entity(entity_type, activity):
        if entity_type is None:
            return []
        elif type(entity_type) is models.ItemType:
            return [deferred.dumps(actions.CreateItemAction, entity_type, activity, {})]
