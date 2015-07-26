from exeris.core.properties import P
from pyslate.backends import json_backend
from pyslate.pyslate import Pyslate
from exeris.core import models

__author__ = 'alek'


def create_pyslate(language, data=None, **kwargs):

    pyslate = Pyslate(language, backend=json_backend.JsonBackend(json_data=data), **kwargs)

    #################
    #   ITEM_INFO   #
    #################

    def func_item_info(helper, tag_name, params):

        item = None
        if "item" in params:
            item = params["item"]
        elif "item_id" in params:
            item = models.Item.by_id(params["item_id"])

        if not item:  # fallback
            item_name = params["item_name"]
            return helper.translation("entity_" + item_name)  # this is all

        item_name = item.type_name

        number_text = ""
        parts_text = ""
        material_text = ""
        damage_text = ""
        title_text = ""
        states_text = ""

        number = item.amount
        if item.type.stackable:
            number_text = str(number) + " "

        transl_name, form = helper.translation_and_form("entity_" + item_name, number=number)
        transl_name += " "  # TODO THIS IS WEAK

        if item.visible_parts:
            parts_text = helper.translation("tp_item_parts", parts=item.visible_parts, item_form=form)
            parts_text += " "

        material_prop = item.get_property(P.VISIBLE_MATERIAL)
        if material_prop and "main" in material_prop:
            main_material_type_name = material_prop["main"]
            material_text = helper.translation("tp_item_main_material", material_name=main_material_type_name, item_form=form)
            material_text += " "

        if item.damage > models.Item.DAMAGED_LB:
            damage_text = helper.translation("tp_item_damaged", item_name=transl_name, item_form=form)
            damage_text += " "

        return helper.translation("tp_item_info", damage=damage_text, main_material=material_text, amount=number_text,
                                  item_name=transl_name, parts=parts_text, title=title_text, states=states_text).strip()  # TODO strip is weak

    pyslate.register_function("item_info", func_item_info)





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

    def func_activity_info(helper, tag_name, params):
        activity_name = params["activity_name"]
        text, form = helper.translation_and_form("activity_" + activity_name, **params["activity_params"])  # this is all
        helper.return_form(form)
        return text

    pyslate.register_function("activity_info", func_activity_info)

    #################
    # LOCATION_INFO #
    #################

    def func_location_info(helper, tag_name, params):
        location_name = params["location_name"]
        text, form = helper.translation_and_form("entity_" + location_name)  # this is all
        helper.return_form(form)
        return text

    pyslate.register_function("location_info", func_location_info)

    def func_passage_info(helper, tag_name, params):
        passage_name = params["passage_name"]
        text, form = helper.translation_and_form("entity_" + passage_name)  # this is all
        helper.return_form(form)
        return text

    pyslate.register_function("passage_info", func_passage_info)

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

        text, form = helper.translation_and_form(tag_to_call, **params)  # pass to correct custom function
        helper.return_form(form)
        return text

    pyslate.register_function("entity_info", func_entity_info)

    return pyslate
