from pyslate.backend import PyslateJsonBackend
from pyslate.pyslate import Pyslate
from exeris.core import models

__author__ = 'alek'


def create_pyslate(language, data=None, **kwargs):

    pyslate = Pyslate(language, backend=PyslateJsonBackend(data=data), **kwargs)

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

        if item.visible_parts:
            return helper.translation("tp_item_with_parts", item_name=transl_name, parts=item.visible_parts)

        if item.damage > models.Item.DAMAGED_LB:
            transl_name = helper.translation("tp_item_damaged", item_name=transl_name, item_form=form)

        return transl_name

    pyslate.register_function("item_info", func_item_info)

    def func_parts(helper, tag_name, params):

        parts = []
        for part in params["parts"]:
            part_name = models.ItemType.by_id(part).name
            parts += [helper.translation("entity_" + part_name + "#b")]  # TODO WHY #b - Polish only

        if len(parts) > 1:
            return helper.translation("tp_parts#y", most=", ".join(parts[:-1]), last=parts[-1])

        return helper.translation("tp_parts", last=parts[0])


    pyslate.register_function("_parts", func_parts)

    return pyslate