# Notification and in-game event queue service. Should be referenced directly.
# It queues all pending notifications and events to send them to the client through socketio
# if and only if the transaction is commited successfully.
# In case of rollback all the queued data is discarded

import sqlalchemy
from exeris.app import socketio
from flask_sqlalchemy import SignallingSession

_notifications_to_send = []
_events_to_send = []


def add_event_to_send(sid, observer_id, event_id, event_text):
    _events_to_send.append((sid, observer_id, event_id, event_text))


def add_notification_to_send(sid, notification):
    _notifications_to_send.append((sid, notification))


@sqlalchemy.event.listens_for(SignallingSession, 'after_commit')
def send_after_commit(session):
    for new_event in _events_to_send:
        socketio.emit("character.new_event", (new_event[1],
                                              {"id": new_event[2], "text": new_event[3]}), room=new_event[0])

    for new_notification in _notifications_to_send:
        socketio.emit("player.new_notification", (new_notification[1],), room=new_notification[0])

    _notifications_to_send.clear()
    _events_to_send.clear()


@sqlalchemy.event.listens_for(SignallingSession, 'after_rollback')
def send_after_rollback(session):
    _notifications_to_send.clear()
    _events_to_send.clear()
