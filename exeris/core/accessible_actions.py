from exeris.core import models
from exeris.core.properties_base import P


class ActionRecord:
    def __init__(self, tag_name, image, required_property, endpoint, other_req=lambda x: True):
        self.tag_name = tag_name
        self.image = image
        self.required_property = required_property
        self.endpoint = endpoint
        self.other_req = other_req


class EntityActionRecord:
    def __init__(self, entity, action):
        self.entity = entity
        self.tag_name = action.tag_name
        self.image = action.image
        self.required_property = action.required_property
        self.endpoint = action.endpoint
        self.other_req = action.other_req


ACTIONS_ON_GROUND = [
    ActionRecord("eat", "image", P.EDIBLE, "eat"),
    ActionRecord("enter", "image", P.ENTERABLE, "move_to_location"),
    ActionRecord("read", "image", P.READABLE, "open_readable_contents"),
    ActionRecord("add_to_activity", "image", P.ANY, "form_add_item_to_activity",
                 lambda x: isinstance(x, models.Item)),
    ActionRecord("go_to_location", "image", P.ANY, "character.go_to_location",
                 lambda x: isinstance(x, models.RootLocation)),
    ActionRecord("open", "image", P.CLOSEABLE, "toggle_closeable",
                 lambda x: x.has_property(P.CLOSEABLE, closed=True)),
    ActionRecord("close", "image", P.CLOSEABLE, "toggle_closeable",
                 lambda x: x.has_property(P.CLOSEABLE, closed=False)),
    ActionRecord("attack", "image", P.COMBATABLE, "character.attack"),
    ActionRecord("bury_body", "image", P.BURYABLE, "character.start_burying_entity",
                 lambda x: isinstance(x, models.Character)),
    ActionRecord("tame_animal", "image", P.TAMABLE, "character.start_taming_animal"),
    ActionRecord("take", "image", P.ANY, "character.take_item",
                 lambda x: isinstance(x, models.Item) and x.type.portable
                           and not isinstance(x.being_in, models.Character)),
    ActionRecord("drop", "image", P.ANY, "inventory.drop_item",
                 lambda x: isinstance(x, models.Item) and isinstance(x.being_in, models.Character)),
    ActionRecord("put_into_storage", "image", P.ANY, "character.put_into_storage",
                 lambda x: isinstance(x, models.Item) and x.type.portable),
]
