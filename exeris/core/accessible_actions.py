from exeris.core.properties_base import P


class ActionRecord:
    
    def __init__(self, tag_name, image, required_property, endpoint):
        self.tag_name = tag_name
        self.image = image
        self.required_property = required_property
        self.endpoint = endpoint


ACTIONS_ON_GROUND = [
    ActionRecord("eat", "image", P.EDIBLE, "eat"),
    ActionRecord("enter", "image", P.ENTERABLE, "move_to_location"),
    ActionRecord("read", "image", P.READABLE, "open_readable_contents"),
]

TOOLBAR_ACTIONS = [
    "point",
    "repair",
]
