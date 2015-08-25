from pyslate.backends import json_backend
from pyslate.pyslate import Pyslate
from exeris.core import models

__author__ = 'alek'


def create_pyslate(language, backend=None, **kwargs):

    def htmlize(f):
        def g(helper, tag_name, params):
            print(params)
            result_text = f(helper, tag_name, params)
            if not params.get("html", False):
                return result_text
            entity_type_name = models.NAMES[params["entity_type"]]
            entity_id = params.get(entity_type_name + "_id", 0)
            return '''<span class="entity {} id_{}">{}</span>'''.format(entity_type_name, entity_id, result_text)

        return g

    pyslate = Pyslate(language, backend=backend, **kwargs)

    #################
    #   ITEM_INFO   #
    #################

    @htmlize
    def func_item_info(helper, tag_name, params):

        detailed = params.get("detailed", False)

        number_text = ""
        parts_text = ""
        material_text = ""
        damage_text = ""
        title_text = ""
        states_text = ""

        number = 1
        if params.get("item_amount", None):
            number = params["item_amount"]
            number_text = str(number) + " "

        item_name = params["item_name"]
        if detailed:
            item_text, form = helper.translation_and_form("entity_" + item_name + helper.pass_the_suffix(tag_name), number=number)
        else:
            item_text, form = helper.translation_and_form("entity_" + item_name + "#u" + helper.get_suffix(tag_name))
        item_text += " "

        if "item_parts" in params:
            parts_text = helper.translation("tp_item_parts", parts=params["item_parts"], item_form=form)
            parts_text += " "

        material_prop = params.get("item_material", {})
        if "main" in material_prop:
            main_material_type_name = material_prop["main"]
            material_text = helper.translation("tp_item_main_material", material_name=main_material_type_name, item_form=form)
            material_text += " "

        if params.get("item_damage", 0) > models.Item.DAMAGED_LB:
            damage_text = helper.translation("tp_item_damaged", item_name=item_text, item_form=form)
            damage_text += " "

        if params.get("item_title", None):
            title_text = helper.translation("tp_item_title", title=params["item_title"])
            title_text += " "

        if detailed:
            return helper.translation("tp_detailed_item_info", damage=damage_text, main_material=material_text,
                                      amount=number_text, item_name=item_text, parts=parts_text,
                                      title=title_text, states=states_text).strip()  # TODO strip is weak
        else:
            return helper.translation("tp_item_info", main_material=material_text,
                                      item_name=item_text, parts=parts_text).strip()  # TODO strip is weak

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
        text, form = helper.translation_and_form("activity_" + activity_name, **params["activity_params"])  # this is all
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

        if "location_title" in params:
            return helper.translation("tp_location_title", title=params["location_title"])

        if "location_terrain" in params:
            location_terrain = params["location_terrain"]
            return helper.translation("terrain_" + location_terrain)

        location_name = params["location_name"]
        return helper.translation("entity_" + location_name)

    pyslate.register_function("location_info", func_location_info)

    ##################
    # CHARACTER INFO #
    ##################

    @htmlize
    def func_character_info(helper, tag_name, params):
        character_gen = params["character_gen"]
        helper.return_form(character_gen)

        if "character_title" in params:
            return helper.translation("tp_character_title", title=params["character_title"])

        if "observer" in params and "character_id" in params:
            observer = params["observer"]
            character_id = params["character_id"]

            observed_name = models.ObservedName.query.filter_by(observer=observer, target_id=character_id).first()
            if observed_name:
                return observed_name.name

        return helper.translation("entity_character#" + character_gen)

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

        states_text = ""
        return helper.translation("tp_detailed_passage_info", passage_name=passage_text, states=states_text)

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
        # elif entity_type == models.ENTITY_ROOT_LOCATION:
        #     tag_to_call = "location_info"
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

    return pyslate
