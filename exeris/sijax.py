from flask import g
from exeris.core import models
from exeris.core.main import db

__author__ = 'alek'


class GlobalMixin:
        @staticmethod
        def rename_entity(obj_response, character_id, new_name):
            entity_to_rename = models.Entity.by_id(character_id)
            entity_to_rename.set_dynamic_name(g.character, new_name)
            db.session.commit()

            obj_response.call("$.publish", ["refresh_entity", character_id])

        @staticmethod
        def get_entity_tag(obj_response, entity_id):
            entity = models.Entity.by_id(entity_id)
            text = g.pyslate.t("entity_info", html=True, **entity.pyslatize())
            obj_response.call("FRAGMENTS.global.alter_entity", [entity_id, text])
