data = {
    "title_page_player": {
        "en": "Player page"
    },
    "title_page_events": {
        "en": "Events page",
    },
    "title_people_short": {
        "en": "People near",
    },
    "title_page_entities": {
        "en": "Entities",
    },
    "title_page_actions": {
        "en": "Actions",
    },
    "event_say_aloud_doer": {
        "en": "You say: %{message@escape_html}",
    },
    "event_say_aloud_observer": {
        "en": "${doer:character_info} say: %{message@escape_html}",
    },
    "event_speak_to_somebody_doer": {
        "en": "You say to ${target:character_info}: %{message@escape_html}",
    },
    "event_speak_to_somebody_observer": {
        "en": "${doer:character_info} speaks to ${target:character_info}: %{message@escape_html}",
    },
    "event_speak_to_somebody_target": {
        "en": "${doer:character_info} speaks to you: %{message@escape_html}",
    },
    "event_whisper_doer": {
        "en": "You whisper to ${target:character_info}: %{message@escape_html}",
    },
    "event_whisper_observer": {
        "en": "${doer:character_info} whispers to ${target:character_info}.",
    },
    "event_whisper_target": {
        "en": "${doer:character_info} whispers to you: %{message@escape_html}",
    },
    "event_eat_doer": {
        "en": "You eat ${food:entity_info}",
    },
    "event_move_doer": {
        "en": "You move from ${from:location_info} to ${destination:location_info}",
    },
    "event_move_observer": {
        "en": "You see ${doer:character_info} move from ${from:location_info} to ${destination:location_info}",
    },
    "event_eat_observer": {
        "en": "You see ${doer:entity_info} eat ${food:entity_info}",
    },
    "event_attack_character_target": {
        "en": "You are attacked by ${doer:entity_info} and thus start a combat.",
    },
    "event_attack_character_doer": {
        "en": "You attack ${target:entity_info} and start a combat.",
    },
    "event_attack_character_observer": {
        "en": "You see ${doer:entity_info} attack ${target:entity_info} and begin a combat.",
    },
    "event_hit_target_in_combat_target": {
        "en": "You are hit by ${doer:entity_info}.",
    },
    "event_retreat_from_combat_observer": {
        "en": "You see ${doer:entity_info} retreat from combat.",
    },
    "event_hit_target_in_combat_observer": {
        "en": "You see ${doer:entity_info} hit ${target:entity_info}.",
    },
    "event_hit_target_in_combat_doer": {
        "en": "You hit ${target:entity_info}.",
    },
    "event_end_of_combat_observer": {
        "en": "You see the combat between ${list_of_entities} ends, "
              "because there are no active participants on one side."
    },
    "event_end_of_combat_doer": {
        "en": "You see the combat between ${list_of_entities} ends, "
              "because there are no active participants on one side."
    },
    "event_take_item_doer": {
        "en": "You take ${item:item_info}."
    },
    "event_take_item_from_location_doer": {
        "en": "You take ${item:item_info} from ${item_loc:location_info}."
    },
    "event_take_item_from_other_location_observer": {
        "en": "You see ${doer:entity_info} from ${doer_loc:location_info} take ${item:item_info}."
    },
    "event_take_item_from_storage_doer": {
        "en": "Your take ${item:item_info} from ${storage:entity_info}."
    },
    "event_take_item_from_storage_observer": {
        "en": "You see ${doer:entity_info} take ${item:item_info} from ${storage:entity_info}."
    },
    "entity_character#f": {
        "en": "unknown woman",
    },
    "entity_character#m": {
        "en": "unknown man",
    },
    "tp_dead_character": {
        "en": "dead %{name}",
    },
    "tp_location_title": {
        "en": "'%{title@escape_html}'",
    },
    "tp_character_title": {
        "en": "%{title@escape_html}",
    },
    "say_to_all_button": {
        "en": "Say to all",
    },
    "speak_to_somebody_button": {
        "en": "Speak to ${character_info}",
    },
    "whisper_to_somebody_button": {
        "en": "Whisper to ${character_info}",
    },
    "tp_item_info": {
        "en": "%{main_material}%{dependent}%{item_name}%{parts}",
    },
    "tp_location_info": {
        "en": "%{main_material}%{location_name}%{title}%{trust}",
    },
    "tp_item_title": {
        "en": "'%{title@escape_html}'",
    },
    "entity_item": {
        "en": "item",
    },
    "tp_detailed_item_info": {
        "en": "%{amount}%{damage}%{main_material}%{dependent}%{item_name}%{title}%{states}%{parts}%{trust}",
    },
    "tp_item_parts": {
        "en": "with ${_parts}",
        "pl": "z ${_parts}",
    },
    "tp_item_main_material": {
        "en": "${entity_%{material_name}_adj#%{item_form}}",
    },
    "tp_location_main_material": {
        "en": "${entity_%{material_name}_adj#%{location_form}}",
    },
    "tp_game_date": {
        "en": "%{day}-%{moon}m. %{hour}:%{minute}",
        "pl": "%{day}-%{moon}k. %{hour}:%{minute}",
    },
    "tp_item_rotting": {
        "en": "rotting",
    },
    "tp_item_dependent": {
        "en": "${entity_%{dependent}}",
    },
    "tp_detailed_passage_info": {
        "en": "%{states} %{passage_name}",
    },
    "tp_detailed_passage_other_side": {
        "en": "%{states} %{passage_name} to ${other_side:entity_info}",
    },
    "domestication_most_trusted": {
        "en": "(trusting you most)",
    },
    "domestication_trusted": {
        "en": "(trusting you)",
    },
    "passage_closed": {
        "en": "closed",
    },
    "passage_open": {
        "en": "open",
    },
    "entity_door": {
        "en": "door",
    },
    "entity_hammer": {
        "en": "hammer",
    },
    "entity_potatoes": {
        "en": "potato",
    },
    "entity_potatoes#p": {
        "en": "potatoes",
    },
    "entity_scaffolding": {
        "en": "scaffolding",
    },
    "entity_hut": {
        "en": "hut",
    },
    "entity_signpost": {
        "en": "signpost",
    },
    "terrain_grass": {
        "en": "grassland",
    },
    "terrain_forest": {
        "en": "forest",
    },
    "terrain_deep_water": {
        "en": "deep water",
    },
    "entity_portable_item_in_constr": {
        "en": "in construction",
    },
    "entity_fixed_item_in_constr": {
        "en": "in construction",
    },
    "entity_tablet": {
        "en": "tablet",
    },
    "entity_oak_tree": {
        "en": "oak tree",
    },
    "entity_oak": {
        "en": "oak branch",
    },
    "entity_oak#p": {
        "en": "oak branches",
    },
    "entity_milk": {
        "en": "pint of milk",
    },
    "entity_milk#p": {
        "en": "pints of milk",
    },
    "entity_anvil": {
        "en": "anvil",
    },
    "entity_longsword": {
        "en": "longsword",
    },
    "entity_clay_adj": {
        "en": "clay",
    },
    "entity_pig": {
        "en": "pig"
    },
    "entity_mare": {
        "en": "mare"
    },
    "entity_granite": {
        "en": "block of granite",
    },
    "entity_granite#p": {
        "en": "blocks of granite",
    },
    "entity_granite_adj": {
        "en": "granite",
    },
    "entity_sandstone": {
        "en": "block of sandstone",
    },
    "entity_sandstone#p": {
        "en": "blocks of sandstone",
    },
    "entity_sandstone_adj": {
        "en": "sandstone",
    },
    "entity_marble": {
        "en": "block of marble",
    },
    "entity_marble#p": {
        "en": "blocks of marble",
    },
    "entity_marble_adj": {
        "en": "marble",
    },
    "entity_group_stone": {
        "en": "stone",
    },
    "entity_female_aurochs": {
        "en": "female aurochs",
    },
    "entity_cow": {
        "en": "cow",
    },
    "achievement_unlocked": {
        "en": "Achievement %{name} unlocked!",
    },
    "notification_close": {
        "en": "Close",
    },
    "entity_invisible_to_animal": {
        "en": ""
    },
    "entity_impassable_to_animal": {
        "en": ""
    },
    "error_character_dead": {
        "en": "Your character %{name} is dead.",
    },
    "action_generic": {
        "en": "perform %{action_name}",
    },
    "action_work_on_activity": {
        "en": "work on ${activity:activity_info} [%{ticks_done} / %{ticks_needed}]",
    },
    "action_travel_in_direction": {
        "en": "move in direction %{direction}",
    },
    "action_controlling_vehicle_standing": {
        "en": "controlling ${vehicle:location_info} to stand still",
    },
    "action_controlling_vehicle": {
        "en": "controlling ${vehicle:location_info} in order to ${movement_action:action_info}",
    },
    "action_walking": {
        "en": "walking in order to ${movement_action:action_info}",
    },
    "action_walking_standing": {
        "en": "standing",
    },
}
