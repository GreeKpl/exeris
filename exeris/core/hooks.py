from exeris.core import main, actions, models


@main.hook(main.Hooks.EXCEEDED_HUNGER_LEVEL)
def on_exceeded_hunger_level(character):
    death_action = actions.DeathOfStarvationAction(executor=character)
    death_action.perform()


@main.hook(main.Hooks.ENTITY_CONTENTS_COUNT_DECREASED)
def on_root_location_contents_reduced(entity):

    if not isinstance(entity, models.RootLocation):  # other entities are not yet supported
        return

    if entity.is_empty():  # RootLocation can disappear
        entity.remove()

