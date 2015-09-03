from exeris.core.properties_base import P


class ActionRecord:
    
    def __init__(self, tag_name, image, required_property, endpoint_name):
        self.tag_name = tag_name
        self.image = image
        self.required_property = required_property
        self.endpoint_name = endpoint_name


ACTIONS_ON_GROUND = [
    ActionRecord("eat", "image", P.EDIBLE, "/eat"),
]

TOOLBAR_ACTIONS = [
    "point",
    "repair",
]
