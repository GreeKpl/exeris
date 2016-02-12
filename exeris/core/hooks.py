from exeris.core import main, actions


@main.hook(main.Hooks.EXCEEDED_HUNGER_LEVEL)
def on_exceeded_hunger_level(character):
    death_action = actions.DeathOfStarvationAction(executor=character)
    death_action.perform()

