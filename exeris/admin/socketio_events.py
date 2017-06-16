from exeris.app import socketio_player_event
from exeris.core import models


@socketio_player_event("admin.get_all_entity_types")
def get_all_entity_types():
    all_entity_types = models.EntityType.query.all()
    return [{
        "name": entity_type.name,
        "class": entity_type.discriminator_type,
    } for entity_type in all_entity_types],


@socketio_player_event("admin.get_entity_type")
def get_entity_type(entity_type_name):
    entity_type = models.EntityType.by_name(entity_type_name)
    entity_names = {
        a.name: getattr(entity_type, a.name)
        for a in entity_type.__table__.columns
    }
    entity_names["class"] = entity_type.discriminator_type

    return entity_names,
