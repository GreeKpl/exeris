from exeris.core import models


class PropertyCache:
    def __init__(self):
        self.entity_properties = {}
        self.type_properties = {}
        self.entity_hits = 0
        self.type_hits = 0

    def save_all_properties_of_entities(self, entities):
        if not entities:
            return

        all_entity_properties = models.EntityProperty.query.filter(
            models.EntityProperty.entity_id.in_(models.ids(entities))).all()
        all_entity_type_properties = models.EntityTypeProperty.query.filter(
            models.EntityTypeProperty.type_name.in_([e.type_name for e in entities])).all()

        for entity in entities:
            entity_properties_for_entity = [p for p in all_entity_properties if p.entity == entity]
            type_properties_for_entity = [p for p in all_entity_type_properties if p.type == entity.type]
            self.save_entity_properties(entity, entity_properties_for_entity)
            self.save_type_properties(entity.type, type_properties_for_entity)

    def save_entity_properties(self, entity, props):
        self.entity_properties[entity.id] = {prop.name: prop for prop in props}

    def save_type_properties(self, entity_type, props):
        self.type_properties[entity_type.name] = {prop.name: prop for prop in props}

    def get_entity_prop(self, entity, name):
        self.entity_hits += 1
        return self.entity_properties[entity.id].get(name, None)

    def get_type_prop(self, entity_type, name):
        self.type_hits += 1
        return self.type_properties[entity_type.name].get(name, None)

    def entity_cached(self, entity):
        return entity.id in self.entity_properties

    def type_cached(self, entity_type):
        return entity_type.name in self.type_properties
