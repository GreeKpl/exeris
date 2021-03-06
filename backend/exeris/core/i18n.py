import html
import json
import os

import collections
from pyslate.pyslate import Pyslate

from exeris.core import main, models, general


def create_pyslate(language, backend=None, character=None, **kwargs):
    # converters for custom info
    pre_converters = collections.OrderedDict([
        ("closed", lambda helper, value, form: helper.translation(
            "passage_closed" if value else "passage_open", psg_form=form)),
    ])
    post_converters = collections.OrderedDict([
        ("unique_id", lambda helper, value, form: "({})".format(value)),
    ])

    def all_converters_for_info(converters, helper, params, form):
        info_text = ""
        for key, converter in converters.items():
            if key in params:
                info_text += converter(helper, params[key], form) + " "
        return info_text.strip()

    def htmlize(f):
        def g(helper, tag_name, params):
            result_text = f(helper, tag_name, params)
            if not params.get("html", False):
                return result_text
            entity_type_name = params["entity_type"]
            entity_id = params.get(entity_type_name + "_id", 0)
            from exeris.app import app
            observer_id_for_encryption = params.get("observer").id if params.get("observer", None) else 0
            enc_entity_id = app.encode(entity_id, character_id=observer_id_for_encryption)
            classes = ["entity", entity_type_name]
            classes += ["dynamic_nameable"] if params.get("dynamic_nameable", False) else []
            return '<span data-entity-id="{}" class="{}">{}</span>'.format(
                enc_entity_id,
                " ".join(classes),
                result_text)

        return g

    def on_missing_tag_key(key, params):
        file_path = os.path.join(os.path.dirname(__file__), "../../log/missing_tags.json")  # TODO pass as argument
        with open(file_path, 'r+') as f:
            try:
                old_data = json.loads(f.read())
            except ValueError:
                old_data = {}
            f.seek(0)

            def turn_into_string(text):
                if isinstance(params[text], dict):
                    return "{}[{}]".format(text, ",".join(params[text].keys()))
                return text

            old_data[key] = {
                "en": ",".join([turn_into_string(x) for x in params.keys()])}
            f.write(json.dumps(old_data, indent=4))
            f.truncate()

        return "[MISSING TAG {}]".format(key)

    def get_the_most_trusted(trusted_dict):
        """
        :arg trusted_dict a dict where key is a character id (as str) and value is trust level (float)
        :return the id having the highest trust level. None if the dict is empty
        """
        the_most_trusted = None
        for trusted_id in trusted_dict:
            if the_most_trusted is None or trusted_dict[trusted_id] > trusted_dict[str(the_most_trusted)]:
                the_most_trusted = int(trusted_id)
        return the_most_trusted

    if character:  # add character-specific data if character is specified
        kwargs["context"] = dict(kwargs.get("context", {}), observer=character, obs_gen=character.sex)

    pyslate = Pyslate(language, backend=backend, on_missing_tag_key_callback=on_missing_tag_key, **kwargs)

    #################
    #  DECORATORS   #
    #################

    pyslate.register_decorator("escape_html", lambda text: html.escape(text))

    #################
    #   ITEM_INFO   #
    #################

    @htmlize
    def func_item_info(helper, tag_name, params):

        detailed = params.get("detailed", False)

        dependent_text = ""
        number_text = ""
        parts_text = ""
        material_text = ""
        damage_text = ""
        title_text = ""
        trust_text = ""

        number = 1
        if params.get("item_amount", None):
            number = params["item_amount"]
            number_text = str(number) + " "

        item_name = params["item_name"]
        if detailed:
            item_text, form = helper.translation_and_form("entity_" + item_name + helper.pass_the_suffix(tag_name),
                                                          number=number)
        else:
            item_text, form = helper.translation_and_form("entity_" + item_name + "#u" + helper.get_suffix(tag_name))
        item_text += " "

        if "item_dependent" in params:
            dependent_text = helper.translation("tp_item_dependent", dependent=params["item_dependent"], item_form=form)
            dependent_text += " "

        if "item_parts" in params:
            parts_text = helper.translation("tp_item_parts", parts=params["item_parts"], item_form=form)
            parts_text += " "

        material_prop = params.get("item_material", {})
        if "main" in material_prop:
            main_material_type_name = material_prop["main"]
            material_text = helper.translation("tp_item_main_material", material_name=main_material_type_name,
                                               item_form=form)
            material_text += " "

        if params.get("item_damage", 0) > models.Item.DAMAGED_LB:
            if "item_amount" in params:  # it's stackable
                damage_text = helper.translation("tp_item_rotten", number=params["item_amount"],
                                                 item_name=item_text, item_form=form)
                damage_text += " "
            else:
                damage_text = helper.translation("tp_item_damaged", item_name=item_text, item_form=form)
                damage_text += " "

        if params.get("item_title"):
            title_text = helper.translation("tp_item_title", title=params["item_title"])
            title_text += " "

        if "observer" in params and "trusted" in params:
            observer_id = params["observer"].id
            trust_dict = params.get("trusted", {})
            if observer_id == get_the_most_trusted(trust_dict):
                trust_text = " " + helper.translation("domestication_most_trusted")
            elif str(observer_id) in trust_dict:
                trust_text = " " + helper.translation("domestication_trusted")

        post_info_text = all_converters_for_info(post_converters, helper, params, form)

        if detailed:
            return helper.translation("tp_detailed_item_info", damage=damage_text, main_material=material_text,
                                      dependent=dependent_text, amount=number_text, item_name=item_text,
                                      parts=parts_text, title=title_text,
                                      post_info=post_info_text, trust=trust_text) \
                .strip()  # TODO such strip is weak
        else:
            return helper.translation("tp_item_info", dependent=dependent_text, main_material=material_text,
                                      item_name=item_text, parts=parts_text) \
                .strip()  # TODO such strip is weak

    pyslate.register_function("item_info", func_item_info)

    #

    def func_parts(helper, tag_name, params):

        parts = []
        for part_name in params["parts"]:
            parts += [helper.translation("entity_" + part_name + "#u")]

        if len(parts) > 1:
            return helper.translation("tp_parts#p", most=", ".join(parts[:-1]), last=parts[-1])

        return helper.translation("tp_parts", last=parts[0])

    pyslate.register_function("_parts", func_parts)

    def func_parts_pl(helper, tag_name, params):

        parts = []
        for part_name in params["parts"]:
            parts += [helper.translation("entity_" + part_name + "#ub")]  # "#b" is Polish only

        if len(parts) > 1:
            return helper.translation("tp_parts#p", most=", ".join(parts[:-1]), last=parts[-1])

        return helper.translation("tp_parts", last=parts[0])

    pyslate.register_function("_parts", func_parts_pl, language="pl")

    #################
    # ACTIVITY_INFO #
    #################

    @htmlize
    def func_activity_info(helper, tag_name, params):
        activity_name = params["activity_name"]
        text, form = helper.translation_and_form("activity_" + activity_name,
                                                 **params["activity_params"])  # this is all
        helper.return_form(form)
        return text

    pyslate.register_function("activity_info", func_activity_info)

    #################
    # LOCATION_INFO #
    #################

    @htmlize
    def func_location_info(helper, tag_name, params):

        if "observer" in params and "location_id" in params:
            observer = params["observer"]
            location_id = params["location_id"]
            observed_name = models.ObservedName.query.filter_by(observer=observer, target_id=location_id).first()
            if observed_name:
                return observed_name.name

        title_text = ""
        if "location_title" in params:
            title_text = helper.translation("tp_location_title", title=params["location_title"])

        if "location_terrain" in params:
            location_terrain = params["location_terrain"]
            return helper.translation("terrain_" + location_terrain + helper.pass_the_suffix(tag_name))

        location_name, form = helper.translation_and_form(
            "entity_" + params["location_name"] + helper.pass_the_suffix(tag_name))
        location_name += " "

        material_text = ""
        material_prop = params.get("location_material", {})
        if "main" in material_prop:
            main_material_type_name = material_prop["main"]
            material_text = helper.translation("tp_location_main_material", material_name=main_material_type_name,
                                               item_form=form)
            material_text += " "

        trust_text = ""
        if "observer" in params and "trusted" in params:
            observer_id = params["observer"].id
            trust_dict = params.get("trusted", {})
            if observer_id == get_the_most_trusted(trust_dict):
                trust_text = " " + helper.translation("domestication_most_trusted")
            elif str(observer_id) in trust_dict:
                trust_text = " " + helper.translation("domestication_trusted")

        return helper.translation("tp_location_info", location_name=location_name, title=title_text,
                                  main_material=material_text, trust=trust_text).strip()

    pyslate.register_function("location_info", func_location_info)

    ##################
    # CHARACTER INFO #
    ##################

    @htmlize
    def func_character_info(helper, tag_name, params):
        character_gen = params["character_gen"]
        helper.return_form(character_gen)

        visible_name = None
        if "observer" in params and "character_id" in params:
            observer = params["observer"]
            character_id = params["character_id"]

            observed_name = models.ObservedName.query.filter_by(observer=observer, target_id=character_id).first()
            if observed_name:
                visible_name = helper.translation("tp_character_title", title=observed_name.name)
        elif "character_title" in params:
            visible_name = helper.translation("tp_character_title", title=params["character_title"])

        if not visible_name:  # name unknown, show generic name
            visible_name = helper.translation("entity_character#" + character_gen)

        if params["character_name"] == main.Types.DEAD_CHARACTER:
            return helper.translation("tp_dead_character#" + character_gen, name=visible_name)

        return visible_name

    pyslate.register_function("character_info", func_character_info)

    ##################
    #  PASSAGE INFO  #
    ##################

    @htmlize
    def func_passage_info(helper, tag_name, params):
        detailed = params.get("detailed", False)
        passage_name = params["passage_name"]

        passage_text, form = helper.translation_and_form("entity_" + passage_name + helper.pass_the_suffix(tag_name))
        helper.return_form(form)

        if not detailed:
            return passage_name

        pre_info_text = all_converters_for_info(pre_converters, helper, params, form)
        post_info_text = all_converters_for_info(post_converters, helper, params, form)

        if "other_side" in params:
            if params.get("invisible", False):
                return helper.translation("entity_info", **params["other_side"])
            return helper.translation("tp_detailed_passage_other_side", passage_name=passage_text,
                                      groups={"other_side": params["other_side"]},
                                      pre_info=pre_info_text, post_info=post_info_text)

        if params.get("invisible", True):
            return ""

        return helper.translation("tp_detailed_passage_info", passage_name=passage_text,
                                  pre_info=pre_info_text, post_info=post_info_text)

    pyslate.register_function("passage_info", func_passage_info)

    ###################
    #   ENTITY INFO   #
    ###################

    def func_entity_info(helper, tag_name, params):
        entity_type = params["entity_type"]

        if entity_type == models.ENTITY_ITEM:
            tag_to_call = "item_info"
        elif entity_type == models.ENTITY_LOCATION:
            tag_to_call = "location_info"
        elif entity_type == models.ENTITY_ROOT_LOCATION:
            tag_to_call = "location_info"
        elif entity_type == models.ENTITY_PASSAGE:
            tag_to_call = "passage_info"
        elif entity_type == models.ENTITY_CHARACTER:
            tag_to_call = "character_info"
        elif entity_type == models.ENTITY_ACTIVITY:
            tag_to_call = "activity_info"
        else:
            tag_to_call = None

        # pass the tag (with the same suffix) to the correct "*_info" custom function
        text, form = helper.translation_and_form(tag_to_call + helper.pass_the_suffix(tag_name), **params)
        helper.return_form(form)
        return text

    pyslate.register_function("entity_info", func_entity_info)

    ###################
    #    DATE INFO    #
    ###################

    def func_game_date(helper, tag_name, params):
        date = params["game_date"]
        if isinstance(date, int):
            date = general.GameDate(date)

        return helper.translation("tp_game_date", moon=date.moon, day=date.day, hour=date.hour,
                                  minute=str(date.minute).zfill(2))

    pyslate.register_function("game_date", func_game_date)

    def func_action_info(helper, tag_name, params):
        action_tag = params["action_tag"]
        return helper.translation(action_tag, **params)

    pyslate.register_function("action_info", func_action_info)

    def func_list_of_entities(helper, tag_name, params):

        entities = params["entities"]
        tag_for_each_entity = "entity_info" + helper.pass_the_suffix(tag_name)
        return ", ".join(
            [helper.translation(tag_for_each_entity, **dict(entity_info, **params)) for entity_info in entities])

    pyslate.register_function("list_of_entities", func_list_of_entities)

    return pyslate
