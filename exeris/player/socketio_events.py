import copy

import flask_socketio as client_socket
from exeris.app import socketio_player_event
from exeris.core import achievements
from exeris.core import main
from exeris.core import models, actions, util
from exeris.core.main import db
from flask import g, render_template
from sqlalchemy import sql


@socketio_player_event("player.create_new_character")
def create_character(char_name):
    create_character_action = actions.CreateCharacterAction(g.player, char_name, models.Character.SEX_MALE, "en")
    new_char = create_character_action.perform()
    db.session.commit()

    return ()


@socketio_player_event("player.update_top_bar")
def player_update_top_bar():
    rendered = render_template("exeris/player/templates/player_top_bar.html")
    return rendered,


@socketio_player_event("player.get_characters_list")
def get_characters_list():
    alive_characters = g.player.alive_characters

    return sorted([{"id": ch.id, "name": ch.name} for ch in alive_characters], key=lambda ch: ch["id"]),


@socketio_player_event("player.get_achievements_list")
def get_achievements_list():
    awarded_achievements = models.Achievement.query.filter_by(achiever=g.player).all()
    achievements_to_show = []
    for awarded_achievement in awarded_achievements:
        for achievement in achievements.achievements:
            if achievement[0] == awarded_achievement.achievement:
                achievements_to_show.append(achievement)

    return [{"title": achievement[0], "content": achievement[1]} for achievement in achievements_to_show],


@socketio_player_event("player.pull_notifications_initial")
def get_notifications_list():
    notifications = models.Notification.query.filter_by(player=g.player).all()

    if hasattr(g, "character"):
        notifications += models.Notification.query.filter_by(character=g.character).all()

    notifications = util.serialize_notifications(notifications, g.pyslate)

    for notification in notifications:
        client_socket.emit("player.new_notification", (notification,))


@socketio_player_event("notification.show_modal")
def show_notification_modal(notification_id):
    owner_condition = models.Notification.player == g.player
    if hasattr(g, "character"):
        owner_condition = sql.or_(models.Notification.character == g.character, models.Notification.player == g.player)

    notification = models.Notification.query.filter_by(id=notification_id).filter(owner_condition).one()

    encoded_options = copy.deepcopy(notification.options)
    for option in encoded_options:
        for idx, param in enumerate(option["request_params"]):
            if idx in option["encoded_indexes"]:
                option["request_params"][idx] = main.app.encode(param)

    rendered = render_template("modal_notification.html", notification=notification,
                               notification_options=encoded_options)
    return rendered,


def check_if_notification_option_exists(notification, expected_option):
    for option in notification.options:
        if option["endpoint"] == expected_option:
            return option
    raise main.InvalidOptionForNotification(player=g.player, option_name=expected_option)


@socketio_player_event("notification.close")
def notification_close(notification_id):
    notification = models.Notification.by_id(notification_id)

    if not notification.get_option("notification.close"):
        raise main.InvalidOptionForNotification(player=g.player, option_name="notification.close")

    db.session.delete(notification)
    db.session.commit()
