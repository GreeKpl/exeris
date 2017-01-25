import exeris
from exeris.app import app
from exeris.core import main, actions, models, util
from exeris.core.properties_base import P
from exeris.extra import notifications_service
from exeris.core.i18n import create_pyslate
from pyslate.backends import postgres_backend
import psycopg2


@main.hook(main.Hooks.DAMAGE_EXCEEDED)
def on_character_death(entity):
    if entity.type_name == main.Types.ALIVE_CHARACTER:
        death_action = actions.CharacterDeathAction(executor=entity)
        death_action.perform()
    elif isinstance(entity, (models.Item, models.Location)) and entity.has_property(P.ANIMAL):
        death_action = actions.AnimalDeathAction(executor=entity)
        death_action.perform()


@main.hook(main.Hooks.ENTITY_CONTENTS_COUNT_DECREASED)
def on_root_location_contents_reduced(entity):
    if not isinstance(entity, models.RootLocation):  # other entities are not yet supported
        return

    if entity.is_empty():  # RootLocation can disappear
        entity.remove()


@main.hook(main.Hooks.NEW_EVENT)
def on_new_event(event_observer):
    observer = event_observer.observer
    event = event_observer.event

    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    pyslate = create_pyslate(observer.language, backend=postgres_backend.PostgresBackend(conn, "translations"),
                             character=observer)

    for sid in exeris.app.socketio_users.get_all_by_player_id(observer.player_id):
        notifications_service.add_event_to_send(sid, observer.id, event.id,
                                                pyslate.t("game_date", game_date=event.date) + ": " +
                                                pyslate.t(event.type_name, html=True, **event.params))


@main.hook(main.Hooks.NEW_CHARACTER_NOTIFICATION)
def on_new_notification(character, notification):
    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    pyslate = create_pyslate(character.language, backend=postgres_backend.PostgresBackend(conn, "translations"),
                             character=character)

    for sid in exeris.app.socketio_users.get_all_by_player_id(character.player_id):
        notification_info = util.serialize_notifications([notification], pyslate)[0]
        notifications_service.add_notification_to_send(sid, notification_info)


@main.hook(main.Hooks.NEW_PLAYER_NOTIFICATION)
def on_new_player_notification(player, notification):
    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    pyslate = create_pyslate(player.language, backend=postgres_backend.PostgresBackend(conn, "translations"))

    for sid in exeris.app.socketio_users.get_all_by_player_id(player.id):
        notification_info = util.serialize_notifications([notification], pyslate)[0]
        notifications_service.add_notification_to_send(sid, notification_info)
