from exeris.core import models
from exeris.core.properties_base import P


class ActionRecord:
    def __init__(self, tag_name, image, required_property, endpoint, other_req=lambda x: True, multi_entities=False,
                 multi_tag_name=None):
        self.tag_name = tag_name
        self.image = image
        self.required_property = required_property
        self.endpoint = endpoint
        self.other_req = other_req
        self.multi_entities = multi_entities
        self.multi_tag_name = multi_tag_name


class EntityActionRecord:
    def __init__(self, entity, action):
        self.entity = entity
        self.tag_name = action.tag_name
        self.image = action.image
        self.required_property = action.required_property
        self.endpoint = action.endpoint
        self.other_req = action.other_req
        self.multi_entities = action.multi_entities
        self.multi_tag_name = action.multi_tag_name


ACTIONS_ON_GROUND = [
    ActionRecord("eat", "image", P.EDIBLE, "character.eat"),
    ActionRecord("enter", "image", P.ENTERABLE, "character.move_to_location"),
    ActionRecord("read", "image", P.READABLE, "character.show_readable_contents"),
    ActionRecord("add_to_activity", "image", P.ANY, "character.add_item_to_activity",
                 lambda x: isinstance(x, models.Item)),
    ActionRecord("go_to_location", "image", P.ANY, "character.go_to_location",
                 lambda x: isinstance(x, models.RootLocation)),
    ActionRecord("open", "image", P.CLOSEABLE, "character.toggle_closeable",
                 lambda x: x.has_property(P.CLOSEABLE, closed=True), multi_entities=True),
    ActionRecord("close", "image", P.CLOSEABLE, "character.toggle_closeable",
                 lambda x: x.has_property(P.CLOSEABLE, closed=False), multi_entities=True),
    ActionRecord("attack", "image", P.COMBATABLE, "character.attack"),
    ActionRecord("bury_body", "image", P.BURYABLE, "character.start_burying_entity",
                 lambda x: isinstance(x, models.Character), multi_entities=True),
    ActionRecord("tame_animal", "image", P.TAMABLE, "character.start_taming_animal", multi_entities=True),
    ActionRecord("take", "image", P.ANY, "character.take_item",
                 lambda x: isinstance(x, models.Item) and x.type.portable
                           and not isinstance(x.being_in, models.Character), multi_entities=True,
                 multi_tag_name="take_all"),
    ActionRecord("drop", "image", P.ANY, "character.drop_item",
                 lambda x: isinstance(x, models.Item) and isinstance(x.being_in, models.Character),
                 multi_entities=True, multi_tag_name="drop_all"),
    ActionRecord("put_into_storage", "image", P.ANY, "character.put_into_storage",
                 lambda x: isinstance(x, models.Item) and x.type.portable, multi_entities=True,
                 multi_tag_name="put_all_into_storage"),
    ActionRecord("get_entities_to_bind_to", "image", P.BINDABLE, "character.get_entities_to_bind_to"),
    ActionRecord("unbind_from_vehicle", "image", P.BINDABLE, "character.unbind_from_vehicle",
                 lambda x: x.has_property(P.MEMBER_OF_UNION)),
    ActionRecord("start_boarding_ship", "image", P.BOARDABLE,
                 "character.start_boarding_ship"),  # should have access to executor's loc
    ActionRecord("unboard_ship", "image", P.IN_BOARDING, "character.start_unboarding_from_ship"),
]
