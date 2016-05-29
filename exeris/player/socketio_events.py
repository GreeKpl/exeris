import flask_socketio as client_socket
from exeris.app import socketio_player_event
from exeris.core import models, actions, util
from exeris.core.main import db
from flask import g, render_template
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

    notifications = util.serialize_notifications(notifications, g.pyslate)

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
