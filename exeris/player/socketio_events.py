import exeris
import flask_socketio as client_socket
import psycopg2
from exeris.app import socketio_player_event, app
from exeris.core import models, actions, main
from exeris.core.main import hook
from exeris.core.i18n import create_pyslate
from exeris.core.main import db
from flask import g, render_template
from pyslate.backends import postgres_backend
from sqlalchemy import sql


@socketio_player_event("create_character")
def create_character(char_name):
    create_character_action = actions.CreateCharacterAction(g.player, char_name, models.Character.SEX_MALE, "en")
    new_char = create_character_action.perform()
    db.session.commit()

    return ()


@socketio_player_event("player.update_top_bar")
def player_update_top_bar():
    rendered = render_template("player_top_bar.html")
    return rendered,


@socketio_player_event("player.pull_notifications_initial")
def get_notifications_list():
    notifications = models.Notification.query.filter_by(player=g.player).all()

    if hasattr(g, "character"):
        notifications += models.Notification.query.filter_by(character=g.character).all()

    notifications = [{"notification_id": n.id, "title": g.pyslate.t(n.title_tag, **n.title_params), "count": n.count,
                      "date": n.game_date} for n in notifications]

    for notification in notifications:
        client_socket.emit("player.new_notification", (notification,))


@socketio_player_event("show_notification_dialog")
def show_notification_dialog(notification_id):
    owner_condition = models.Notification.player == g.player
    if hasattr(g, "character"):
        owner_condition = sql.or_(models.Notification.character == g.character, models.Notification.player == g.player)

    notification = models.Notification.query.filter_by(id=notification_id).filter(owner_condition).one()
    rendered = render_template("modal_notification.html", notification=notification)
    return rendered,


@hook(main.Hooks.NEW_PLAYER_NOTIFICATION)
def on_new_player_notification(player, notification):
    conn = psycopg2.connect(app.config["SQLALCHEMY_DATABASE_URI"])
    pyslate = create_pyslate(player.language, backend=postgres_backend.PostgresBackend(conn, "translations"))

    for sid in exeris.app.socketio_users.get_all_by_player_id(player.id):
        notification_info = {"notification_id": notification.id,
                             "title": pyslate.t(notification.title_tag, **notification.title_params)}
        client_socket.emit("player.new_notification", notification_info, room=sid)
