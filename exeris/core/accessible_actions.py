from exeris.core import models
from exeris.core.properties_base import P


class ActionRecord:
    
    def __init__(self, tag_name, image, required_property, endpoint, other_req=lambda x: True):
        self.tag_name = tag_name
        self.image = image
        self.required_property = required_property
        self.endpoint = endpoint
        self.other_req = other_req


ACTIONS_ON_GROUND = [
    ActionRecord("eat", "image", P.EDIBLE, "eat"),
    ActionRecord("enter", "image", P.ENTERABLE, "move_to_location"),
    ActionRecord("read", "image", P.READABLE, "open_readable_contents"),
    ActionRecord("add_to_activity", "image", "any", "form_add_item_to_activity", lambda x: isinstance(x, models.Item))
]

TOOLBAR_ACTIONS = [
    "point",
    "repair",
]
