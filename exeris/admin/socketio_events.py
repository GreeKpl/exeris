import json

from exeris.app import socketio_player_event
from exeris.core import models
from exeris.core.models import ENTITY_ITEM, ENTITY_LOCATION, ENTITY_PASSAGE
from exeris.core.properties_base import P


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
    entity_names["properties"] = [{
        "name": prop.name,
        "data": json.dumps(prop.data),
    } for prop in entity_type.properties]

    return entity_names,


@socketio_player_event("admin.create_or_update_entity_type")
def create_or_update_entity_type(entity_type_data):
    entity_type_exists = models.EntityType.by_name(entity_type_data["name"])
    if entity_type_exists:
        update_entity_type(entity_type_data)
    else:
        create_entity_type(entity_type_data)


def update_entity_type(entity_type_data):
    existing_entity_type = models.EntityType.by_name(entity_type_data["name"])

    entity_class = entity_type_data["class"]
    existing_entity_type.name = entity_type_data["name"]
    if entity_class == ENTITY_ITEM:
        existing_entity_type.unit_weight = entity_type_data["unit_weight"]
        existing_entity_type.portable = entity_type_data["portable"]
        existing_entity_type.stackable = entity_type_data["stackable"]
    elif entity_class == ENTITY_LOCATION:
        existing_entity_type.unit_weight = entity_type_data["unit_weight"]
    elif entity_class == ENTITY_PASSAGE:
        existing_entity_type.unlimited = entity_type_data["unlimited"]
    else:
        raise ValueError("Unsupported entity type")

    existing_entity_type.properties.clear()
    for entity_prop in entity_type_data["properties"]:
        existing_entity_type.properties.append(models.EntityTypeProperty(entity_prop["name"],
                                                                         json.loads(entity_prop["data"])))


def create_entity_type(entity_type_data):
    entity_class = entity_type_data["class"]
    if entity_class == ENTITY_ITEM:
        new_entity_type = models.ItemType(entity_type_data["name"], entity_type_data["unit_weight"],
                                          entity_type_data["portable"], entity_type_data["stackable"])
    elif entity_class == ENTITY_LOCATION:
        new_entity_type = models.LocationType(entity_type_data["name"], entity_type_data["unit_weight"])
    elif entity_class == ENTITY_PASSAGE:
        new_entity_type = models.PassageType(entity_type_data["name"], entity_type_data["unlimited"])
    else:
        raise ValueError("Unsupported entity type")

    for entity_prop in entity_type_data["properties"]:
        new_entity_type.properties.append(models.EntityTypeProperty(entity_prop["name"],
                                                                    json.loads(entity_prop["data"])))


@socketio_player_event("admin.get_all_property_names")
def get_all_property_names():
    return sorted([val.value for val in P]),
