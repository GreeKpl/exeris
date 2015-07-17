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

        transl_name, form = helper.translation_and_form("entity_" + item_name)
        transl_name += " "  # TODO THIS IS WEAK

        parts_text = ""
        material_text = ""
        damage_text = ""

        if item.visible_parts:
            parts_text = helper.translation("tp_item_parts", parts=item.visible_parts, item_form=form)
            parts_text += " "

        material_prop = item.get_property(P.VISIBLE_MATERIAL)
        if material_prop and "main" in material_prop:
            main_material_type = models.ItemType.by_id(material_prop["main"])
            material_text = helper.translation("tp_item_main_material", material_name=main_material_type.name, item_form=form)
            material_text += " "

        if item.damage > models.Item.DAMAGED_LB:
            damage_text = helper.translation("tp_item_damaged", item_name=transl_name, item_form=form)
            damage_text += " "

        return helper.translation("tp_item_info", damage=damage_text, main_material=material_text,
                                  item_name=transl_name, parts=parts_text).strip()  # TODO strip is weak

    pyslate.register_function("item_info", func_item_info)


    def func_parts(helper, tag_name, params):

        parts = []
        for part in params["parts"]:
            part_name = models.ItemType.by_id(part).name
            parts += [helper.translation("entity_" + part_name)]

        if len(parts) > 1:
            return helper.translation("tp_parts#y", most=", ".join(parts[:-1]), last=parts[-1])

        return helper.translation("tp_parts", last=parts[0])

    pyslate.register_function("_parts", func_parts)

    def func_parts_pl(helper, tag_name, params):

        parts = []
        for part in params["parts"]:
            part_name = models.ItemType.by_id(part).name
            parts += [helper.translation("entity_" + part_name + "#b")]  # "#b" is Polish only

        if len(parts) > 1:
            return helper.translation("tp_parts#y", most=", ".join(parts[:-1]), last=parts[-1])

        return helper.translation("tp_parts", last=parts[0])

    pyslate.register_function("_parts", func_parts_pl, language="pl")

    return pyslate