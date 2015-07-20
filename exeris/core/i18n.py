from exeris.core.properties import P
from pyslate.backends import json_backend
from pyslate.pyslate import Pyslate
from exeris.core import models

__author__ = 'alek'


def create_pyslate(language, data=None, **kwargs):

    pyslate = Pyslate(language, backend=json_backend.JsonBackend(json_data=data), **kwargs)

    def func_item_info(helper, tag_name, params):

        item = None
        if "item" in params:
            item = params["item"]
        elif "item_id" in params:
            item = models.Item.by_id(params["item_id"])

        if not item:  # fallback
            item_name = params["item_name"]
            return helper.translation("entity_" + item_name)  # this is all

        item_name = item.type.name

        number_text = ""
        parts_text = ""
        material_text = ""
        damage_text = ""
        title_text = ""

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
                                  item_name=transl_name, parts=parts_text, title=title_text).strip()  # TODO strip is weak

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

    return pyslate