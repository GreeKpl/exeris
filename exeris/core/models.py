import types
import collections
import datetime

from flask.ext.security import UserMixin
from flask.ext.security import RoleMixin
import geoalchemy2 as gis
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import or_
from sqlalchemy.orm import validates

from exeris.core.main import db, Types, Events
from exeris.core.properties_base import P

import sqlalchemy as sql
import sqlalchemy.orm
import sqlalchemy.dialects.postgresql as psql
from .map import MAP_HEIGHT, MAP_WIDTH
from exeris.core import properties_base

# subclasses hierarchy for Entity
ENTITY_BASE = "base"
ENTITY_ITEM = "item"
ENTITY_LOCATION = "location"
ENTITY_ROOT_LOCATION = "root_location"
ENTITY_PASSAGE = "passage"
ENTITY_CHARACTER = "character"
ENTITY_ACTIVITY = "activity"
ENTITY_TERRAIN_AREA = "terrain_area"
ENTITY_GROUP = "group"

TYPE_NAME_MAXLEN = 32
TAG_NAME_MAXLEN = 32
PLAYER_ID_MAXLEN = 24

roles_users = db.Table('player_roles',
                       db.Column('player_id', db.String(PLAYER_ID_MAXLEN), db.ForeignKey('players.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Player(db.Model, UserMixin):
    __tablename__ = "players"

    id = sql.Column(sql.String(PLAYER_ID_MAXLEN), primary_key=True)

    email = sql.Column(sql.String(32), unique=True)
    language = sql.Column(sql.String(2), default="en")
    register_date = sql.Column(sql.DateTime)
    register_game_date = sql.Column(sql.BigInteger)
    password = sql.Column(sql.String)

    active = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('players', lazy='dynamic'))
    confirmed_at = sql.Column(sql.DateTime)

    def __init__(self, id, email, language, password, active=True, register_date=None, register_game_date=None,
                 **kwargs):
        self.id = id
        self.email = email
        self.language = language
        self.password = password

        self.active = active
        self.register_date = register_date if register_date else datetime.datetime.now()

        from exeris.core import general
        self.register_game_date = register_game_date if register_game_date else general.GameDate.now()

    @validates("register_game_date")
    def validate_register_game_date(self, key, register_game_date):
        return register_game_date.game_timestamp

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    @hybrid_property
    def alive_characters(self):
        return Character.query.filter_by(player=self).filter(Character.is_alive).all()

    def get_id(self):
        return self.id


class TranslatedText(db.Model):
    __tablename__ = "translations"

    def __init__(self, name, language, content, form=""):
        self.name = name
        self.language = language
        self.content = content
        self.form = form

    name = sql.Column(sql.String(32), primary_key=True)
    language = sql.Column(sql.String(8), primary_key=True)
    content = sql.Column(sql.String)
    form = sql.Column(sql.String(8))


class EntityType(db.Model):
    __tablename__ = "entity_types"

    name = sql.Column(sql.String(32), primary_key=True)  # no spaces allowed

    def __init__(self, name):
        self.name = name

    properties = sql.orm.relationship("EntityTypeProperty", back_populates="type")

    discriminator_type = sql.Column(sql.String(15))  # discriminator

    @hybrid_property
    def parent_groups(self):
        return [parent_group.parent for parent_group in self._parent_groups_junction]

    @classmethod
    def by_name(cls, type_name):
        return cls.query.get(type_name)

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": discriminator_type,
    }


class TypeGroupElement(db.Model):
    __tablename__ = "entity_group_elements"

    def __init__(self, child, efficiency=1.0):
        self.child = child
        self.efficiency = efficiency

    parent_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey('entity_type_groups.name'), primary_key=True)
    parent = sql.orm.relationship("TypeGroup", foreign_keys=[parent_name], backref="_children_junction")
    child_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey('entity_types.name'), primary_key=True)
    child = sql.orm.relationship("EntityType", foreign_keys=[child_name], backref="_parent_groups_junction")
    efficiency = sql.Column(sql.Float, default=1.0, nullable=False)  # how many of child is 1 unit of parent group


class ItemType(EntityType):
    __tablename__ = "item_types"

    name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("entity_types.name"), primary_key=True)

    def __init__(self, name, unit_weight, portable=True, stackable=False):
        super().__init__(name)
        self.unit_weight = unit_weight
        self.portable = portable
        self.stackable = stackable

    unit_weight = sql.Column(sql.Integer)
    stackable = sql.Column(sql.Boolean)
    portable = sql.Column(sql.Boolean)

    def efficiency(self, entity_type):  # quack quack
        if entity_type == self:
            return 1.0
        raise ValueError

    def get_descending_types(self):
        return [(self, 1.0)]

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class TypeGroup(EntityType):
    __tablename__ = "entity_type_groups"

    name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("entity_types.name"), primary_key=True)

    @hybrid_property
    def children(self):
        return [group_element.child for group_element in self._children_junction]

    def add_to_group(self, child, efficiency=1.0):
        self._children_junction.append(TypeGroupElement(child, efficiency))

    def remove_from_group(self, child):
        self._children_junction.remove(TypeGroupElement.query.filter_by(parent=self, child=child).one())

    def contains(self, entity_type):
        return not not self.get_group_path(entity_type)

    def get_descending_types(self):
        """
        Returns a list of tuples which represent all concrete EntityTypes contained by this group.
        The first element of the pair is EntityType, the second element is float representing its overall efficiency
        """
        result = []
        for type_group_element in self._children_junction:
            if isinstance(type_group_element.child, TypeGroup):
                pairs = type_group_element.child.get_descending_types()
                result += [(type, efficiency * type_group_element.efficiency) for type, efficiency in pairs]
            else:
                result.append((type_group_element.child, type_group_element.efficiency))
        return result

    def get_group_path(self, entity_type):
        """
        Recursively searching for entity_type in groups' children.
        If found, it returns a list of nodes which need to be visited to get from 'self' to 'entity_type'
        If not found, returns an empty list
        """
        if entity_type in self.children:
            return [self, entity_type]
        child_groups = filter(lambda group: type(group) == TypeGroup, self.children)  # TODO, disgusting
        for group in child_groups:
            path = group.get_group_path(entity_type)
            if path:
                return [self] + path
        return []

    def efficiency(self, entity_type):
        lst = self.get_group_path(entity_type)
        pairs = zip(lst[:-1], lst[1:])
        efficiency = 1.0
        for pair in pairs:
            efficiency *= TypeGroupElement.query.filter_by(parent=pair[0], child=pair[1]).one().efficiency
        return efficiency

    def __init__(self, name):
        super().__init__(name)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_GROUP,
    }

    def __repr__(self):
        return "{TypeGroup, name: " + self.name + "}"


class Entity(db.Model):
    """
    Abstract base for all entities in the game, like items or locations
    """
    __tablename__ = "entities"

    ROLE_BEING_IN = 1
    ROLE_USED_FOR = 2

    id = sql.Column(sql.Integer, primary_key=True)
    weight = sql.Column(sql.Integer)

    parent_entity_id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), nullable=True)
    parent_entity = sql.orm.relationship(lambda: Entity, primaryjoin=parent_entity_id == id,
                                         foreign_keys=parent_entity_id, remote_side=id, uselist=False)
    role = sql.Column(sql.SmallInteger, nullable=True)

    title = sql.Column(sql.String, nullable=True)
    properties = sql.orm.relationship("EntityProperty", back_populates="entity")

    @hybrid_property
    def being_in(self):
        if self.role != Entity.ROLE_BEING_IN:
            return None
        return self.parent_entity

    @being_in.setter
    def being_in(self, parent_entity):
        self.parent_entity = parent_entity
        self.role = Entity.ROLE_BEING_IN

    @being_in.expression
    def being_in(cls):
        return cls.parent_entity == Entity.id
        # print(select(cls.id).where((cls.role == Item.ROLE_BEING_IN) & (cls.parent_entity == Item)))
        # return select(cls.parent_entity).where((cls.role == Entity.ROLE_BEING_IN) & (cls.parent_entity_id == Entity.id))
        # return case([(cls.role == Entity.ROLE_BEING_IN, cls.parent_entity_id)], else_=-1)
        # return select([cls.parent_entity]).where(cls.role == Entity.ROLE_BEING_IN).as_scalar()
        # return func.IF(cls.role == Entity.ROLE_BEING_IN, Entity.parent_entity, None)

    @hybrid_method
    def is_in(self, parents):
        if not isinstance(parents, collections.Iterable):
            parents = [parents]
        return self.role == Entity.ROLE_BEING_IN and (self.parent_entity in parents)

    @is_in.expression
    def is_in(self, parents):
        if not isinstance(parents, collections.Iterable):
            parents = [parents]
        db.session.flush()  # todo might require more
        return (self.role == Entity.ROLE_BEING_IN) & (
            self.parent_entity_id.in_([p.id for p in parents]) & ~self.discriminator_type.in_([ENTITY_LOCATION,
                                                                                               ENTITY_ROOT_LOCATION]))

    @hybrid_method
    def is_used_for(self, parents):
        if not isinstance(parents, collections.Iterable):
            parents = [parents]
        db.session.flush()  # todo might require more
        return (self.parent_entity_id.in_([p.id for p in parents])) & (self.role == Entity.ROLE_USED_FOR)

    @hybrid_property
    def used_for(self):
        if self.role == Entity.ROLE_BEING_IN:
            return None
        return self.parent_entity

    @used_for.setter
    def used_for(self, parent_entity):
        self.parent_entity = parent_entity
        self.role = Entity.ROLE_USED_FOR

    def __getattr__(self, item):
        try:
            method = properties_base.get_method(item)
            return types.MethodType(method, self)  # return method with updated 'self'
        except KeyError:
            try:
                super().__getattr__(item)
            except AttributeError:
                raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__, item))

    def get_property(self, name):
        props = {}
        ok = False
        type_property = EntityTypeProperty.query.filter_by(type=self.type, name=name).first()
        if type_property:
            props.update(type_property.data)
            ok = True

        entity_property = EntityProperty.query.filter_by(entity=self, name=name).first()
        if entity_property:
            props.update(entity_property.data)
            ok = True

        if not ok:
            return None
        return props

    def has_property(self, name, **kwargs):
        if not kwargs:
            return self.get_property(name) is not None
        else:
            assert len(kwargs) == 1, "Only single key-value pair can be checked for property in this version"
            key, value = next(iter(kwargs.items()))

            prop = self.get_property(name)
            return prop is not None and key in prop and prop[key] == value

    def alter_property(self, name, data=None):
        """
        Creates an EntityProperty for this Entity if it doesn't exist and fills it with provided data
        or REPLACES the data of existing EntityProperty with provided data.
        It doesn't affect any EntityTypeProperty for this Entity's type.
        :param name: name of the property.
        :param data: dict with data for this property
        """
        if not data:
            data = {}
        entity_property = EntityProperty.query.filter_by(name=name).first()
        if entity_property:
            entity_property.data = data
        else:
            self.properties.append(EntityProperty(name, data=data))

    def get_position(self):
        return self.get_root().position

    def get_root(self):
        if type(self) is RootLocation:
            return self
        else:
            return self.being_in.get_root()

    def pyslatize(self, **overwrites):
        pyslatized = dict(entity_type=ENTITY_BASE, entity_id=self.id)
        if self.has_property(P.DYNAMIC_NAMEABLE):
            pyslatized["dynamic_nameable"] = True
        return dict(pyslatized, **overwrites)

    discriminator_type = sql.Column(sql.String(15))  # discriminator

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": discriminator_type,
    }

    @classmethod
    def by_id(cls, entity_id):
        return cls.query.get(entity_id)

    def __repr__(self):
        return str(self.__class__) + str(self.__dict__)


class LocationType(EntityType):
    __tablename__ = "location_types"

    name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("entity_types.name"), primary_key=True)

    def __init__(self, name, base_weight):
        super().__init__(name)
        self.base_weight = base_weight

    base_weight = sql.Column(sql.Integer)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_LOCATION,
    }


class Character(Entity):
    __tablename__ = "characters"

    SEX_MALE = "m"
    SEX_FEMALE = "f"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    def __init__(self, name, sex, player, language, spawn_date, spawn_position, being_in):
        super().__init__()
        self.being_in = being_in
        self.name = name
        self.sex = sex
        self.player = player

        self.language = language

        self.spawn_position = spawn_position
        self.spawn_date = spawn_date

        self.type = EntityType.by_name(Types.ALIVE_CHARACTER)

    sex = sql.Column(sql.Enum(SEX_MALE, SEX_FEMALE, name="sex"))

    player_id = sql.Column(sql.String(PLAYER_ID_MAXLEN), sql.ForeignKey('players.id'))
    player = sql.orm.relationship(Player, uselist=False)

    language = sql.Column(sql.String(2))

    spawn_date = sql.Column(sql.BigInteger)
    spawn_position = sql.Column(gis.Geometry("POINT"))

    activity_id = sql.Column(sql.Integer, sql.ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)
    activity = sql.orm.relationship("Activity", primaryjoin="Character.activity_id == Activity.id", uselist=False)

    type_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("entity_types.name"))
    type = sql.orm.relationship(EntityType, uselist=False)

    states = sql.Column(psql.JSONB, default=lambda x: {"modifiers": []})
    eating_queue = sql.Column(psql.JSONB, default=lambda x: {})

    @hybrid_property
    def name(self):
        own_name = ObservedName.query.filter_by(target=self, observer=self).first()
        if own_name:
            return own_name.name
        return "UNNAMED"

    @name.setter
    def name(self, value):
        if self.id is not None:
            observed_name = ObservedName.query.filter_by(target=self, observer=self).first()
            if observed_name:
                observed_name.name = value
                return
        db.session.add(ObservedName(self, self, value))

    def has_access(self, entity, rng=None):
        from exeris.core import general
        if not rng:
            rng = general.InsideRange()
        return rng.is_near(self, entity)

    @hybrid_property
    def is_alive(self):
        return self.type_name == Types.ALIVE_CHARACTER

    @hybrid_property
    def hunger(self):
        return self.states.get("hunger", 0)

    @hunger.setter
    def hunger(self, value):
        self.states = dict(self.states, hunger=max(0, min(value, 1.0)))

    @hybrid_property
    def tiredness(self):
        return self.states.get("tiredness", 0)

    @tiredness.setter
    def tiredness(self, value):
        self.states = dict(self.states, tiredness=max(0, min(value, 1.0)))

    @hybrid_property
    def damage(self):
        return self.states.get("damage", 0)

    @damage.setter
    def damage(self, value):
        self.states = dict(self.states, damage=max(0, min(value, 1.0)))

    FOOD_BASED_ATTR_INITIAL_VALUE = 0.1

    @hybrid_property
    def strength(self):
        return self.states.get("strength", Character.FOOD_BASED_ATTR_INITIAL_VALUE)

    @strength.setter
    def strength(self, value):
        self.states = dict(self.states, strength=max(0, min(value, 1.0)))

    @hybrid_property
    def durability(self):
        return self.states.get("durability", Character.FOOD_BASED_ATTR_INITIAL_VALUE)

    @durability.setter
    def durability(self, value):
        self.states = dict(self.states, durability=max(0, min(value, 1.0)))

    @hybrid_property
    def fitness(self):
        return self.states.get("fitness", Character.FOOD_BASED_ATTR_INITIAL_VALUE)

    @fitness.setter
    def fitness(self, value):
        self.states = dict(self.states, fitness=max(0, min(value, 1.0)))

    @hybrid_property
    def perception(self):
        return self.states.get("perception", Character.FOOD_BASED_ATTR_INITIAL_VALUE)

    @perception.setter
    def perception(self, value):
        self.states = dict(self.states, perception=max(0, min(value, 1.0)))

    @hybrid_property
    def satiation(self):
        return self.states.get("satiation", 0.0)

    @satiation.setter
    def satiation(self, value):
        self.states = dict(self.states, satiation=max(0, min(value, 1.0)))

    @validates("spawn_position")
    def validate_position(self, key, spawn_position):  # we assume position is a Polygon
        return from_shape(spawn_position)

    @validates("spawn_date")
    def validate_spawn_date(self, key, spawn_date):
        return spawn_date.game_timestamp

    def pyslatize(self, **overwrites):
        pyslatized = dict(entity_type=ENTITY_CHARACTER, character_id=self.id, character_gen=self.sex,
                          character_name=self.type_name)
        if self.has_property(P.DYNAMIC_NAMEABLE):
            pyslatized["dynamic_nameable"] = True
        return dict(pyslatized, **overwrites)

    def __repr__(self):
        return "{{Character name={},player={},activity={}}}".format(self.name, self.player_id, self.activity_id)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_CHARACTER,
    }


class Item(Entity):
    __tablename__ = "items"

    DAMAGED_LB = 0.7

    def __init__(self, item_type, parent_entity, *, weight=None, amount=None, role_being_in=True, quality=1.0):
        self.type = item_type

        if role_being_in:
            self.being_in = parent_entity
        else:
            self.used_for = parent_entity

        if weight is not None:
            self.weight = weight
        elif amount is not None:
            self.weight = amount * item_type.unit_weight
        else:
            self.weight = item_type.unit_weight
        self.quality = quality

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    type_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("item_types.name"))
    type = sql.orm.relationship(ItemType, uselist=False)

    visible_parts = sql.Column(psql.JSONB, default=lambda x: [])  # sorted list of item type names

    @validates("visible_parts")
    def validate_visible_parts(self, key, visible_parts):
        if visible_parts is None:
            visible_parts = []
        # turn (optional) item types into names
        visible_parts = [part if type(part) is str else part.name for part in visible_parts]
        return sorted(visible_parts)

    damage = sql.Column(sql.Float, default=0)

    @validates("damage")
    def validate_damage(self, key, damage):
        return max(0.0, min(1.0, damage))  # in range [0, 1]

    _removal_game_date = sql.Column(sql.BigInteger, nullable=True)

    @hybrid_property
    def removal_game_date(self):
        from exeris.core import general
        return None if not self._removal_game_date else general.GameDate(self._removal_game_date)

    @removal_game_date.setter
    def removal_game_date(self, game_date):
        self._removal_game_date = game_date.game_timestamp

    quality = sql.Column(sql.Float, default=1.0)

    @hybrid_property
    def amount(self):
        if not self.type.stackable:
            return 1
        return int(self.weight / self.type.unit_weight)

    @amount.setter
    def amount(self, new_amount):
        if not self.type.stackable:
            raise ValueError("it's impossible to alter amount for non-stackable")
        self.weight = new_amount * self.type.unit_weight

    def remove(self, move_contents=True):
        if move_contents:
            items_inside = Item.query.filter(Item.is_in(self)).all()

            for item in items_inside:
                item.being_in = self.being_in  # move outside

        self.being_in = None
        from exeris.core import general
        self.removal_game_date = general.GameDate.now()

    def pyslatize(self, **overwrites):
        pyslatized = dict(entity_type=ENTITY_ITEM, item_id=self.id, item_name=self.type_name,
                          item_damage=self.damage)
        if self.type.stackable:
            pyslatized["item_amount"] = self.amount
        if self.title:
            pyslatized["item_title"] = self.title
        if self.visible_parts:
            pyslatized["item_parts"] = self.visible_parts
        prop = self.get_property(P.VISIBLE_MATERIAL)
        if prop:
            pyslatized["item_material"] = prop
        prop = self.get_property(P.HAS_DEPENDENT)
        if prop:
            pyslatized["item_dependent"] = prop["name"]
        return dict(pyslatized, **overwrites)

    def __repr__(self):
        return "{{Item id={}, type={}, parent={}, parent_type={}}}" \
            .format(self.id, self.type_name, self.parent_entity.id, self.parent_entity.discriminator_type)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class Activity(Entity):
    __tablename__ = "activities"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    def __init__(self, being_in, name_tag, name_params, requirements, ticks_needed, initiator):
        self.being_in = being_in

        self.name_tag = name_tag
        self.name_params = name_params

        self.requirements = requirements
        self.ticks_needed = ticks_needed
        self.ticks_left = ticks_needed
        self.initiator = initiator

        self.type = EntityType.by_name(Types.ACTIVITY)

    name_tag = sql.Column(sql.String(TAG_NAME_MAXLEN))
    name_params = sql.Column(psql.JSON)

    type_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("entity_types.name"))
    type = sql.orm.relationship(EntityType, uselist=False)

    initiator_id = sql.Column(sql.Integer, sql.ForeignKey("characters.id"))
    initiator = sql.orm.relationship("Character", uselist=False, primaryjoin="Activity.initiator_id == Character.id",
                                     post_update=True)

    requirements = sql.Column(psql.JSON)  # a list of requirements
    result_actions = sql.Column(psql.JSON)  # a list of serialized constructors of subclasses of AbstractAction
    quality_sum = sql.Column(sql.Float, default=0.0)
    quality_ticks = sql.Column(sql.Integer, default=0)
    ticks_needed = sql.Column(sql.Float)
    ticks_left = sql.Column(sql.Float)

    def pyslatize(self, **overwrites):
        pyslatized = dict(entity_type=ENTITY_ACTIVITY, activity_id=self.id,
                          activity_name=self.name_tag, activity_params=self.name_params)
        if self.has_property(P.DYNAMIC_NAMEABLE):
            pyslatized["dynamic_nameable"] = True
        return dict(pyslatized, **overwrites)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ACTIVITY,
    }

    def __repr__(self):
        return "{{Activity name_tag={}, params={}, in={}, ticks={}/{}, req={}}}".format(self.name_tag, self.name_params,
                                                                                        self.being_in, self.ticks_left,
                                                                                        self.ticks_needed,
                                                                                        self.requirements)


class GameDateCheckpoint(db.Model):
    __tablename__ = "game_date"

    id = sql.Column(sql.Integer, primary_key=True)
    game_date = sql.Column(sql.BigInteger, nullable=False)
    real_date = sql.Column(sql.BigInteger, nullable=False)


class EventTypeGroup(db.Model):
    __tablename__ = "event_type_groups"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(32))


class SkillType(db.Model):
    __tablename__ = "skill_types"

    def __init__(self, name, general_name):
        self.name = name
        self.general_name = general_name

    name = sql.Column(sql.String(20), primary_key=True)
    general_name = sql.Column(sql.String(20))


class EventType(db.Model):
    __tablename__ = "event_types"

    IMPORTANT = 10
    NORMAL = 5
    LOW = 0

    name = sql.Column(sql.String, primary_key=True)
    severity = sql.Column(sql.SmallInteger)
    group_id = sql.Column(sql.Integer, sql.ForeignKey("event_type_groups.id"), nullable=True)
    group = sql.orm.relationship(EventTypeGroup, uselist=False)

    def __init__(self, name, severity=NORMAL, group=None):
        self.name = name
        self.severity = severity
        self.group = group


class Event(db.Model):
    __tablename__ = "events"

    id = sql.Column(sql.Integer, primary_key=True)
    type_name = sql.Column(sql.String, sql.ForeignKey("event_types.name"))
    type = sql.orm.relationship(EventType, uselist=False)
    params = sql.Column(psql.JSON)
    date = sql.Column(sql.BigInteger)

    def __init__(self, event_type, params):
        if isinstance(event_type, str):
            event_type = EventType.query.get(event_type)
        self.type_name = event_type.name  # TODO MAKE SURE IT'S THE BEST WAY TO GO
        self.type = event_type

        self.params = params
        from exeris.core import general
        self.date = general.GameDate.now().game_timestamp

    @hybrid_property
    def observers(self):
        return [junction.observer for junction in self.observers_junction]

    def __repr__(self):
        return "{Event, type=" + self.type_name + ", params=" + str(self.params) + "}"


class EventObserver(db.Model):
    __tablename__ = "event_observers"

    observer_id = sql.Column(sql.Integer, sql.ForeignKey(Character.id), primary_key=True)
    observer = sql.orm.relationship(Character, uselist=False)
    event_id = sql.Column(sql.Integer, sql.ForeignKey(Event.id, ondelete='CASCADE'), primary_key=True)
    event = sql.orm.relationship(Event, uselist=False,
                                 backref=sql.orm.backref("observers_junction", cascade="all,delete-orphan",
                                                         passive_deletes=True))
    times_seen = sql.Column(sql.Integer)

    def __init__(self, event, observer):
        self.event = event
        self.observer = observer
        self.times_seen = 0

    def __repr__(self):
        return str(self.__class__) + str(self.__dict__)


class EntityContentsPreference(db.Model):
    __tablename__ = "entity_contents_preferences"

    character_id = sql.Column(sql.Integer, sql.ForeignKey(Character.id), primary_key=True)
    character = sql.orm.relationship(Character, uselist=False,
                                     primaryjoin="EntityContentsPreference.character_id == Character.id")

    def __init__(self, character, open_entity):
        self.character = character
        self.open_entity = open_entity

    open_entity_id = sql.Column(sql.Integer, sql.ForeignKey(Entity.id), primary_key=True)
    open_entity = sql.orm.relationship(Entity, uselist=False,
                                       primaryjoin="EntityContentsPreference.open_entity_id == Entity.id")


class EntityTypeProperty(db.Model):
    __tablename__ = "entity_type_properties"

    def __init__(self, name, data=None, type=None):
        self.type = type
        self.name = name
        self.data = data if data is not None else {}

    type_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey(EntityType.name), primary_key=True)
    type = sql.orm.relationship(EntityType, uselist=False, back_populates="properties")

    name = sql.Column(sql.String, primary_key=True)
    data = sql.Column(psql.JSON)


class EntityProperty(db.Model):
    __tablename__ = "entity_properties"

    entity_id = sql.Column(sql.Integer, sql.ForeignKey(Entity.id), primary_key=True)
    entity = sql.orm.relationship(Entity, uselist=False, back_populates="properties")

    def __init__(self, name, data=None, entity=None):
        self.entity = entity
        self.name = name
        self.data = data if data is not None else {}

    name = sql.Column(sql.String, primary_key=True)
    data = sql.Column(psql.JSON)

    def __repr__(self):
        return "Property(entity: {}, name: {}, data {}".format(self.entity.id, self.name, self.data)


class PassageToNeighbour:
    def __init__(self, passage, other_side):
        self.passage = passage
        self.other_side = other_side
        self.own_side = passage.left_location
        if passage.left_location == other_side:
            self.own_side = passage.right_location

    @staticmethod
    def get_other_side(passage, own_side):
        if passage.left_location == own_side:
            return passage.right_location
        elif passage.right_location == own_side:
            return passage.left_location

        raise ValueError("location {} is not on any side of passage {}", own_side, passage)


class Location(Entity):
    __tablename__ = "locations"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    def __init__(self, being_in, location_type, passage_type=None, weight=None, title=None):
        self.being_in = being_in
        self.weight = weight
        if not weight:
            self.weight = location_type.base_weight
        self.type = location_type

        if self.being_in is not None:
            db.session.add(Passage(self.being_in, self, passage_type))

        self.title = title

    type_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey(LocationType.name))
    type = sql.orm.relationship(LocationType, uselist=False)

    @hybrid_property
    def neighbours(self):
        neighbours = [passage.left_location for passage in self.right_passages]
        neighbours.extend([passage.right_location for passage in self.left_passages])
        return neighbours

    @hybrid_property
    def passages_to_neighbours(self):
        neighbours = [PassageToNeighbour(passage, passage.left_location) for passage in self.right_passages]
        neighbours.extend([PassageToNeighbour(passage, passage.right_location) for passage in self.left_passages])
        return neighbours

    def get_characters_inside(self):
        return Character.query.filter(Character.is_in(self)).all()

    def get_items_inside(self):
        return Item.query.filter(Item.is_in(self)).all()

    def pyslatize(self, **overwrites):
        pyslatized = dict(entity_type=ENTITY_LOCATION, location_id=self.id,
                          location_name=self.type_name)
        if self.title:
            pyslatized["location_title"] = self.title
        prop = self.get_property(P.VISIBLE_MATERIAL)
        if prop:
            pyslatized["location_material"] = prop
        if self.has_property(P.DYNAMIC_NAMEABLE):
            pyslatized["dynamic_nameable"] = True
        return dict(pyslatized, **overwrites)

    def __repr__(self):
        return "{{Location id={}, title={},type={}}}".format(self.id, self.title, self.type_name)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_LOCATION,
    }


class RootLocation(Location):
    __tablename__ = "root_locations"

    id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"), primary_key=True)

    _position = sql.Column(gis.Geometry("POINT"))
    is_mobile = sql.Column(sql.Boolean)
    direction = sql.Column(sql.Integer)

    def __init__(self, position, is_mobile, direction):
        super().__init__(None, LocationType.by_name(Types.OUTSIDE), 0)
        self.position = position
        self.is_mobile = is_mobile
        self.direction = direction

    @validates("direction")
    def validate_direction(self, key, direction):
        return direction % 360

    @hybrid_property
    def position(self):
        return to_shape(self._position)

    @position.setter
    def position(self, position):  # we assume position is a Point
        x, y = position.x, position.y
        if not (0 <= x < MAP_WIDTH):
            x %= MAP_WIDTH
        if y < 0:
            y = -y
            x = (x + MAP_WIDTH / 2) % MAP_WIDTH
        if y > MAP_HEIGHT:
            y = MAP_HEIGHT - (y - MAP_HEIGHT)
            x = (x + MAP_WIDTH / 2) % MAP_WIDTH
        self._position = from_shape(Point(x, y))

    @position.expression
    def position(cls):
        return cls._position

    def get_terrain_type(self):
        top_terrain = TerrainArea.query.filter(sql.func.ST_CoveredBy(from_shape(self.position), TerrainArea._terrain)). \
            order_by(TerrainArea.priority.desc()).first()
        if not top_terrain:
            return TerrainType.by_name(Types.SEA)
        return top_terrain.type

    def pyslatize(self, **overwrites):
        pyslatized = dict(entity_type=ENTITY_ROOT_LOCATION, location_id=self.id,
                          location_name=self.type_name, location_terrain=self.get_terrain_type().name)
        if self.has_property(P.DYNAMIC_NAMEABLE):
            pyslatized["dynamic_nameable"] = True
        return dict(pyslatized, **overwrites)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ROOT_LOCATION,
    }


class TextContent(db.Model):
    __tablename__ = "text_contents"

    FORMAT_MD = "MD"
    FORMAT_HTML = "HTML"

    def __init__(self, entity, text_format=FORMAT_MD):
        self.entity = entity
        self.format = text_format

    entity_id = sql.Column(sql.Integer, sql.ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True)
    entity = sql.orm.relationship(Entity, uselist=False)

    title = sql.Column(sql.String)
    md_text = sql.Column(sql.String)
    html_text = sql.Column(sql.String)
    format = sql.Column(sql.String(4))


class PassageType(EntityType):
    __tablename__ = "passage_types"

    name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("entity_types.name"), primary_key=True)

    def __init__(self, name, unlimited):
        super().__init__(name)
        self.unlimited = unlimited

    unlimited = sql.Column(sql.Boolean)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_PASSAGE,
    }


class Passage(Entity):
    __tablename__ = "passages"

    def __init__(self, left_location, right_location, passage_type=None):
        self.weight = 0
        self.being_in = None
        self.left_location = left_location
        self.right_location = right_location
        if not passage_type:
            passage_type = EntityType.by_name(Types.DOOR)

        self.type = passage_type

    @hybrid_method
    def between(self, first_loc, second_loc):
        return (self.left_location == first_loc and self.right_location == second_loc) or \
               (self.right_location == first_loc and self.left_location == second_loc)

    @between.expression
    def between(self, first_loc, second_loc):
        return or_((self.left_location == first_loc) & (self.right_location == second_loc),
                   (self.right_location == first_loc) & (self.left_location == second_loc))

    def is_accessible(self, only_through_unlimited=False):
        """
        Checks if the other side of the passage is accessible for any character.
        :return:
        """
        if only_through_unlimited:
            return self.type.unlimited
        return self.type.unlimited or self.is_open()

    def is_open(self):
        return not self.has_property(P.CLOSEABLE, closed=True)

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    type_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("passage_types.name"))
    type = sql.orm.relationship(PassageType, uselist=False)

    left_location_id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"))
    right_location_id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"))

    left_location = sql.orm.relationship(Location, primaryjoin=left_location_id == Location.id,
                                         backref="left_passages", uselist=False)
    right_location = sql.orm.relationship(Location, primaryjoin=right_location_id == Location.id,
                                          backref="right_passages", uselist=False)

    def pyslatize(self, **overwrites):
        pyslatized = dict(entity_type=ENTITY_PASSAGE, passage_id=self.id, passage_name=self.type_name)
        if self.has_property(P.CLOSEABLE):
            pyslatized["closed"] = not self.is_open()
        if self.has_property(P.INVISIBLE_PASSAGE):
            pyslatized["invisible"] = True
        if self.has_property(P.DYNAMIC_NAMEABLE):
            pyslatized["dynamic_nameable"] = True
        return dict(pyslatized, **overwrites)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_PASSAGE,
    }


class ObservedName(db.Model):
    __tablename__ = "observed_names"

    observer_id = sql.Column(sql.Integer, sql.ForeignKey("characters.id"), primary_key=True)
    observer = sql.orm.relationship(Character, uselist=False, foreign_keys=[observer_id])

    target_id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)
    target = sql.orm.relationship(Entity, uselist=False, foreign_keys=[target_id])

    name = sql.Column(sql.String)

    def __init__(self, observer, target, name):
        self.observer = observer
        self.target = target
        self.name = name

    def __repr__(self):
        return "{{ObservedName target={}, by={}, name={}}}".format(self.target, self.observer, self.name)


class Achievement(db.Model):
    __tablename__ = "achievements"

    def __init__(self, achiever, achievement):
        self.achiever = achiever
        self.achievement = achievement

    achiever_id = sql.Column(sql.String(PLAYER_ID_MAXLEN), sql.ForeignKey("players.id"), primary_key=True)
    achiever = sql.orm.relationship(Player, uselist=False, foreign_keys=[achiever_id])

    achievement = sql.Column(sql.String, primary_key=True)


class AchievementCharacterProgress(db.Model):
    __tablename__ = "achievement_character_progress"

    def __init__(self, name, character, details):
        self.name = name
        self.character = character
        self.details = details

    name = sql.Column(sql.String, primary_key=True)

    character_id = sql.Column(sql.Integer, sql.ForeignKey("characters.id"), primary_key=True)
    character = sql.orm.relationship(Character, uselist=False)

    details = sql.Column(psql.JSONB)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = sql.Column(sql.Integer, primary_key=True)

    def __init__(self, title_tag, title_params, text_tag, text_params, stackable=False, character=None, player=None,
                 add_close_option=True):
        self.title_tag = title_tag
        self.title_params = title_params
        self.text_tag = text_tag
        self.text_params = text_params
        self.stackable = stackable
        self.character = character
        self.player = player

        if add_close_option:
            self.add_close_option()

    player_id = sql.Column(sql.String, sql.ForeignKey("players.id"), nullable=True)
    player = sql.orm.relationship(Player, uselist=False)

    character_id = sql.Column(sql.Integer, sql.ForeignKey("characters.id"), nullable=True)
    character = sql.orm.relationship(Character, uselist=False)

    title_tag = sql.Column(sql.String)
    title_params = sql.Column(psql.JSONB, default=lambda: [])

    text_tag = sql.Column(sql.String)
    text_params = sql.Column(psql.JSONB, default=lambda: [])

    stackable = sql.Column(sql.Boolean, default=False)
    icon_name = sql.Column(sql.String, default="undefined.png")
    options = sql.Column(psql.JSON, default=lambda: [])

    def add_close_option(self):
        self.add_option("option_close", {}, "close", {})

    def add_option(self, name_tag, name_params, endpoint, request_params):
        options = list(self.options) if self.options else []
        options.append([name_tag, name_params, endpoint, request_params])
        self.options = options


class ScheduledTask(db.Model):
    __tablename__ = "scheduled_tasks"

    id = sql.Column(sql.Integer, primary_key=True)

    process_data = sql.Column(psql.JSON)
    execution_game_timestamp = sql.Column(sql.BigInteger)
    execution_interval = sql.Column(sql.Integer, nullable=True)

    def __init__(self, process_json, execution_game_timestamp, execution_interval=None):
        self.process_data = process_json
        self.execution_game_timestamp = execution_game_timestamp
        self.execution_interval = execution_interval

    def is_repeatable(self):
        return self.execution_interval is not None


class EntityRecipe(db.Model):
    __tablename__ = "entity_recipes"

    id = sql.Column(sql.Integer, primary_key=True)

    def __init__(self, name_tag, name_params, requirements, ticks_needed, build_menu_category,
                 result=None, result_entity=None, activity_container=None):
        self.name_tag = name_tag
        self.name_params = name_params
        self.requirements = requirements
        self.ticks_needed = ticks_needed
        self.build_menu_category = build_menu_category
        self.result = result if result else []
        self.result_entity = result_entity
        self.activity_container = activity_container

    name_tag = sql.Column(sql.String)
    name_params = sql.Column(psql.JSON)

    requirements = sql.Column(psql.JSON)
    ticks_needed = sql.Column(sql.Float)
    result = sql.Column(psql.JSON)  # a list of serialized Action constructors
    result_entity_id = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey(EntityType.name),
                                  nullable=True)  # EntityType being default result of the project
    result_entity = sql.orm.relationship(EntityType, uselist=False)
    activity_container = sql.Column(psql.JSON, default="entity_specific_item")

    build_menu_category_id = sql.Column(sql.Integer, sql.ForeignKey("build_menu_categories.id"))
    build_menu_category = sql.orm.relationship("BuildMenuCategory", uselist=False)


class BuildMenuCategory(db.Model):
    __tablename__ = "build_menu_categories"

    id = sql.Column(sql.Integer, primary_key=True)

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

    name = sql.Column(sql.String)
    parent_id = sql.Column(sql.Integer, sql.ForeignKey("build_menu_categories.id"), nullable=True)
    parent = sql.orm.relationship("BuildMenuCategory", primaryjoin=parent_id == id,
                                  foreign_keys=parent_id, remote_side=id, backref="child_categories", uselist=False)

    @classmethod
    def get_root_categories(cls):
        return cls.query.filter_by(parent=None).all()

    def get_recipes(self):
        return EntityRecipe.query.filter_by(build_menu_category=self).all()


class ResourceArea(db.Model):
    __tablename__ = "resource_areas"

    id = sql.Column(sql.Integer, primary_key=True)

    resource_type = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("item_types.name"))

    area = sql.Column(gis.Geometry("POLYGON"))

    @validates("area")
    def validate_position(self, key, area):  # we assume position is a Polygon
        return from_shape(area)

    quality = sql.Column(sql.Integer)  # amount collected per unit of time
    amount = sql.Column(sql.Integer)  # amount collected before the resource becomes unavailable


class TerrainType(EntityType):
    __tablename__ = "terrain_types"

    name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("entity_types.name"), primary_key=True)

    def __init__(self, name):
        super().__init__(name)

    visibility = sql.Column(sql.Float)
    traversability = sql.Column(sql.Float)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_TERRAIN_AREA,
    }


class TerrainArea(Entity):
    __tablename__ = "terrain_areas"

    def __init__(self, terrain_poly, terrain_type, priority=1):
        self.terrain = terrain_poly
        self.priority = priority
        self.type = terrain_type

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    _terrain = sql.Column(gis.Geometry("POLYGON"))
    priority = sql.Column(sql.SmallInteger)
    type_name = sql.Column(sql.String(TYPE_NAME_MAXLEN), sql.ForeignKey("terrain_types.name"))
    type = sql.orm.relationship(TerrainType, uselist=False)

    @hybrid_property
    def terrain(self):
        return to_shape(self._terrain)

    @terrain.setter
    def terrain(self, value):
        self._terrain = from_shape(value)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_TERRAIN_AREA,
    }


class ResultantTerrainArea(db.Model):  # no overlays
    __tablename__ = "resultant_terrain_areas"

    id = sql.Column(sql.Integer, sql.ForeignKey("terrain_areas.id"), primary_key=True)

    def __init__(self, _terrain):
        self._terrain = _terrain

    _terrain = sql.Column(gis.Geometry("POLYGON"))

    @hybrid_property
    def terrain(self):
        return self._terrain

    @terrain.setter
    def terrain(self, value):
        self._terrain = from_shape(value)


AREA_KIND_VISIBILITY = 1
AREA_KIND_TRAVERSABILITY = 2


class PropertyArea:
    """
    For example traversability or visibility
    """
    __tablename__ = "property_areas"

    id = sql.Column(sql.Integer)

    terrain_area_id = sql.Column(sql.Integer, sql.ForeignKey("terrain_areas.id"))
    terrain_area = sql.orm.relationship(TerrainArea, uselist=False)

    kind = sql.Column(sql.SmallInteger)
    priority = sql.Column(sql.Integer)
    value = sql.Column(sql.Float)

    _area = sql.Column(gis.Geometry("POLYGON"))

    @hybrid_property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        self._area = from_shape(value)


class ResultantPropertyArea:  # no overlays
    __tablename__ = "resultant_property_areas"

    id = sql.Column(sql.Integer)
    kind = sql.Column(sql.SmallInteger)
    value = sql.Column(sql.Float)

    _area = sql.Column(gis.Geometry("POLYGON"))

    @hybrid_property
    def area(self):
        return self._area

    @area.setter
    def area(self, value):
        self._area = from_shape(value)


def init_database_contents():
    event_types = [type_name for key_name, type_name in Events.__dict__.items() if not key_name.startswith("__")]

    for type_name in event_types:
        db.session.merge(EventType(type_name + "_doer"))
        db.session.merge(EventType(type_name + "_observer"))
        db.session.merge(EventType(type_name + "_target"))

    if not PassageType.by_name(Types.DOOR):
        door_passage = PassageType(Types.DOOR, False)
        door_passage.properties.append(EntityTypeProperty(P.CLOSEABLE, {"closed": False}))
        door_passage.properties.append(EntityTypeProperty(P.ENTERABLE))
        db.session.add(door_passage)
    db.session.merge(EntityType(Types.ALIVE_CHARACTER))
    db.session.merge(EntityType(Types.DEAD_CHARACTER))
    db.session.merge(EntityType(Types.ACTIVITY))
    db.session.merge(LocationType(Types.OUTSIDE, 0))
    db.session.merge(TerrainType("sea"))

    db.session.flush()


def delete_all(seq):
    for element in seq:
        db.session.delete(element)


'''
# low-level functions to maintain ResultantTerrainArea as
@sql.event.listens_for(TerrainArea, "after_insert")
@sql.event.listens_for(TerrainArea, "after_update")
def receive_after_update(mapper, connection, target):

    terrain_envelope = db.session.query(TerrainArea._terrain.ST_Envelope().ST_AsText()).filter_by(id=target.id).first()
    to_be_deleted = ResultantTerrainArea.query.filter(ResultantTerrainArea._terrain.ST_Intersects(terrain_envelope)).all()
    delete_all(to_be_deleted)

    to_transfer = TerrainArea.query.filter(
            TerrainArea._terrain.ST_Intersects(terrain_envelope)
    ).order_by(TerrainArea.priority).all()

    db.session.add_all([ResultantTerrainArea(t._terrain) for t in to_transfer])
    # todo, should make sure these geometries are not intersecting with stuff with smaller priority

    print(ResultantTerrainArea.query.all())
'''
