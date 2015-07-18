import types
import collections
import geoalchemy2 as gis
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import or_
from exeris.core import properties
from exeris.core.main import db
from sqlalchemy.orm import validates
from exeris.core.properties import P
from exeris.core import deferred

__author__ = 'Aleksander Chrabąszcz'

import sqlalchemy as sql
import sqlalchemy.orm
import sqlalchemy.dialects.postgresql as psql
from .map import MAP_HEIGHT, MAP_WIDTH


# subclasses hierarchy for Entity
ENTITY_BASE = 1
ENTITY_ITEM = 2
ENTITY_LOCATION = 3
ENTITY_ROOT_LOCATION = 5
ENTITY_PASSAGE = 6
ENTITY_CHARACTER = 7
ENTITY_ACTIVITY = 8
ENTITY_TERRAIN_AREA = 9
ENTITY_GROUP = 10


class Player(db.Model):
    __tablename__ = "players"

    id = sql.Column(sql.Integer, primary_key=True)

    SEX_MALE = "m"
    SEX_FEMALE = "f"

    login = sql.Column(sql.String(24), unique=True)
    email = sql.Column(sql.String(32), unique=True)
    register_date = sql.Column(sql.DateTime)
    register_game_date = sql.Column(sql.BigInteger)
    password = sql.Column(sql.String)
    sex = sql.Column(sql.Enum(SEX_MALE, SEX_FEMALE, name="sex"))  # used to have correct translations

    @validates("register_game_date")
    def validate_register_game_date(self, key, register_game_date):
        return register_game_date.game_timestamp

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.login


class EntityType(db.Model):
    __tablename__ = "entity_types"

    id = sql.Column(sql.Integer, primary_key=True)

    name = sql.Column(sql.String(32), unique=True)  # no spaces allowed

    def __init__(self, name):
        self.name = name

    type = sql.Column(sql.SmallInteger)  # discriminator

    @hybrid_property
    def parent_groups(self):
        return [parent_group.parent for parent_group in self._parent_groups_junction]

    @classmethod
    def by_id(cls, entity_id):
        return cls.query.get(entity_id)

    @classmethod
    def by_name(cls, type_name):
        return cls.query.filter_by(name=type_name).first()

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": type,
    }


class TypeGroupElement(db.Model):
    __tablename__ = "entity_group_elements"

    def __init__(self, child, multiplier=1.0):
        self.child = child
        self.multiplier = multiplier

    parent_id = sql.Column(sql.Integer, sql.ForeignKey('entity_type_groups.id'), primary_key=True)
    parent = sql.orm.relationship("TypeGroup", foreign_keys=[parent_id], backref="_children_junction")
    child_id = sql.Column(sql.Integer, sql.ForeignKey('entity_types.id'), primary_key=True)
    child = sql.orm.relationship("EntityType", foreign_keys=[child_id], backref="_parent_groups_junction")
    multiplier = sql.Column(sql.Float, default=1.0, nullable=False)  # how many of child is 1 unit of parent group


class ItemType(EntityType):
    __tablename__ = "item_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    def __init__(self, name, unit_weight, portable=True, stackable=False):
        super().__init__(name)
        self.unit_weight = unit_weight
        self.portable = portable
        self.stackable = stackable

    unit_weight = sql.Column(sql.Integer)
    stackable = sql.Column(sql.Boolean)
    portable = sql.Column(sql.Boolean)

    def multiplier(self, entity_type):  # quack quack
        if entity_type == self:
            return 1.0
        raise Exception  # TODO!!! NEED A BETTER EXCEPTION

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class TypeGroup(EntityType):
    __tablename__ = "entity_type_groups"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    @hybrid_property
    def children(self):
        return [group_element.child for group_element in self._children_junction]

    def add_to_group(self, child, multiplier=1.0):
        self._children_junction.append(TypeGroupElement(child, multiplier))

    def remove_from_group(self, child):
        self._children_junction.remove(TypeGroupElement.query.filter_by(parent=self, child=child).one())

    def contains(self, entity_type):
        return not not self.get_group_path(entity_type)

    def get_group_path(self, entity_type):
        if entity_type in self.children:
            return [self, entity_type]
        child_groups = filter(lambda group: type(group) == TypeGroup, self.children)  # TODO, disgusting
        for group in child_groups:
            path = group.get_group_path(entity_type)
            if path:
                return [self] + path
        return []

    def multiplier(self, entity_type):
        lst = self.get_group_path(entity_type)
        pairs = zip(lst[:-1], lst[1:])
        multiplier = 1.0
        for pair in pairs:
            multiplier *= TypeGroupElement.query.filter_by(parent=pair[0], child=pair[1]).one().multiplier
        return multiplier

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
    role = sql.id = sql.Column(sql.SmallInteger, nullable=True)

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
        #print(select(cls.id).where((cls.role == Item.ROLE_BEING_IN) & (cls.parent_entity == Item)))
        #return select(cls.parent_entity).where((cls.role == Entity.ROLE_BEING_IN) & (cls.parent_entity_id == Entity.id))
        #return case([(cls.role == Entity.ROLE_BEING_IN, cls.parent_entity_id)], else_=-1)
        #return select([cls.parent_entity]).where(cls.role == Entity.ROLE_BEING_IN).as_scalar()
        #return func.IF(cls.role == Entity.ROLE_BEING_IN, Entity.parent_entity, None)

    @hybrid_method
    def is_in(self, parents):
        if not isinstance(parents, collections.Iterable):
            parents = [parents]
        db.session.flush()  # todo might require more
        return (self.parent_entity_id.in_([p.id for p in parents])) & (self.role == Entity.ROLE_BEING_IN)

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
            method = properties.get_method(item)
            return types.MethodType(method, self)  # return method type with updated self
        except KeyError:
            try:
                super().__getattr__(item)
            except AttributeError:
                raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__, item))

    def get_property(self, name):
        type_property = EntityTypeProperty.query.filter_by(type=self.type, name=name).first()
        props = {}
        if type_property:
            props.update(type_property.data)

        entity_property = EntityProperty.query.filter_by(entity=self, name=name).first()
        if entity_property:
            props.update(entity_property.data)

        return props

    def has_property(self, name, data_kv=None):
        if data_kv is None:
            entities_count = EntityProperty.query.filter_by(entity=self, name=name).count()
            if entities_count > 0:
                return True

            entities_count = EntityTypeProperty.query.filter_by(type=self.type, name=name).count()

            if entities_count > 0:
                return True
        else:
            assert len(data_kv) == 1
            key, value = next(iter(data_kv.items()))

            entities_count = EntityProperty.query.filter_by(entity=self, name=name).\
                filter(EntityProperty.data[key].cast(sql.Boolean) == value).count()
            if entities_count > 0:
                return True

            entities_count = EntityTypeProperty.query.filter_by(type=self.type, name=name).\
                filter(EntityProperty.data[key].cast(sql.Boolean) == value).count()
            if entities_count > 0:
                return True
        return False

    def get_position(self):
        return self.get_root().position

    def get_root(self):
        if type(self) is RootLocation:
            return self
        else:
            return self.being_in.get_root()

    discriminator_type = sql.Column(sql.SmallInteger)  # discriminator

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

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_LOCATION,
    }


class Character(Entity):
    __tablename__ = "characters"

    SEX_MALE = "m"
    SEX_FEMALE = "f"

    STATE_ALIVE = 1
    STATE_DEAD = 2

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    def __init__(self, name, sex, player, spawn_date, spawn_position, being_in):
        super().__init__()
        self.being_in = being_in
        self.name = name
        self.sex = sex
        self.player = player

        self.state = Character.STATE_ALIVE

        self.spawn_position = spawn_position
        self.spawn_date = spawn_date

    name = sql.Column(sql.String)
    sex = sql.Column(sql.Enum(SEX_MALE, SEX_FEMALE, name="sex"))

    state = sql.Column(sql.SmallInteger)

    player_id = sql.Column(sql.Integer, sql.ForeignKey('players.id'))
    player = sql.orm.relationship(Player, uselist=False)

    spawn_date = sql.Column(sql.BigInteger)
    spawn_position = sql.Column(gis.Geometry("POINT"))

    activity_id = sql.Column(sql.Integer, sql.ForeignKey("activities.id"), nullable=True)
    activity = sql.orm.relationship("Activity", primaryjoin="Character.activity_id == Activity.id", uselist=False)

    @validates("spawn_position")
    def validate_position(self, key, spawn_position):  # we assume position is a Polygon
        return from_shape(spawn_position)

    @validates("spawn_date")
    def validate_spawn_date(self, key, spawn_date):
        return spawn_date.game_timestamp

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_CHARACTER,
    }


class Item(Entity):
    __tablename__ = "items"

    DAMAGED_LB = 0.7

    def __init__(self, item_type, parent_entity, weight=None, role_being_in=True, amount=None):
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


    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    type_id = sql.Column(sql.Integer, sql.ForeignKey("item_types.id"))
    type = sql.orm.relationship(ItemType, uselist=False)

    visible_parts = sql.Column(psql.JSONB, default=[])  # sorted list of item type ids

    @validates("visible_parts")
    def validate_visible_parts(self, key, visible_parts):
        # turn (optional) item types into ids
        visible_parts = [part if type(part) is int else part.id for part in visible_parts]
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

    # TODO
    '''
        @removal_game_date.expression
        def position(cls):
            return cls._removal_game_date
    '''

    @hybrid_property
    def amount(self):
        if not self.type.stackable:
            return 1
        return int(self.weight / self.type.unit_weight)

    def remove(self, move_contents=True):
        if move_contents:
            items_inside = Item.query.filter(Item.is_in(self)).all()

            for item in items_inside:
                item.being_in = self.being_in  # move outside

        self.being_in = None
        from exeris.core import general
        self.removal_game_date = general.GameDate.now()

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class ActivityType(EntityType):   # TODO!!! Is it needed at all? Activities will be property-based
    __tablename__ = "activity_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ACTIVITY,
    }


class Activity(Entity):
    __tablename__ = "activities"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    def __init__(self, being_in, requirements, ticks_needed, initiator):

        self.being_in = being_in
        self.requirements = requirements
        self.ticks_needed = ticks_needed
        self.ticks_left = ticks_needed
        self.initiator = initiator

    initiator_id = sql.Column(sql.Integer, sql.ForeignKey("characters.id"))
    initiator = sql.orm.relationship("Character", uselist=False, primaryjoin="Activity.initiator_id == Character.id", post_update=True)

    requirements = sql.Column(psql.JSON)  # a list of requirements
    result_actions = sql.Column(psql.JSON)  # a list of serialized constructors of subclasses of AbstractAction
    ticks_needed = sql.Column(sql.Float)
    ticks_left = sql.Column(sql.Float)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ACTIVITY,
    }


class GameDateCheckpoint(db.Model):
    __tablename__ = "game_date"

    id = sql.Column(sql.Integer, primary_key=True)
    game_date = sql.Column(sql.BigInteger, nullable=False)
    real_date = sql.Column(sql.BigInteger, nullable=False)


class EventTypeGroup(db.Model):
    __tablename__ = "event_type_groups"

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(32))


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
    parameters = sql.Column(psql.JSON)
    date = sql.Column(sql.BigInteger)

    def __init__(self, event_type, parameters):
        if type(event_type) is str:
            print(event_type)
            event_type = EventType.query.filter_by(name=event_type).one()
        self.type = event_type
        self.parameters = parameters
        from exeris.core import general
        self.date = general.GameDate.now().game_timestamp


class EventObserver(db.Model):
    __tablename__ = "event_observers"

    observer_id = sql.Column(sql.Integer, sql.ForeignKey(Character.id), primary_key=True)
    observer = sql.orm.relationship(Character, uselist=False)
    event_id = sql.Column(sql.Integer, sql.ForeignKey(Event.id), primary_key=True)
    event = sql.orm.relationship(Event, uselist=False)
    times_seen = sql.Column(sql.Integer)

    def __init__(self, event, observer):
        self.event = event
        self.observer = observer
        self.times_seen = 0

    def __repr__(self):
        return str(self.__class__) + str(self.__dict__)


class EntityTypeProperty(db.Model):
    __tablename__ = "entity_type_properties"

    def __init__(self, type, name, data=None):
        self.type = type
        self.name = name
        self.data = data if data is not None else {}

    type_id = sql.Column(sql.Integer, sql.ForeignKey(EntityType.id), primary_key=True)
    type = sql.orm.relationship(EntityType, uselist=False)

    name = sql.Column(sql.String, primary_key=True)
    data = sql.Column(psql.JSON)


class EntityProperty(db.Model):
    __tablename__ = "entity_properties"

    entity_id = sql.Column(sql.Integer, sql.ForeignKey(Entity.id), primary_key=True)
    entity = sql.orm.relationship(Entity, uselist=False, back_populates="properties")

    def __init__(self, entity, name, data=None):
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


class Location(Entity):
    __tablename__ = "locations"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    def __init__(self, being_in, weight):
        self.being_in = being_in
        self.weight = weight

        if self.being_in is not None:
            db.session.add(Passage(self.being_in, self))

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
        super().__init__(None, 0)
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


    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ROOT_LOCATION,
    }


class Passage(Entity):
    __tablename__ = "passages"

    def __init__(self, left_location, right_location):
        self.weight = 0
        self.being_in = None
        self.left_location = left_location
        self.right_location = right_location
        door = EntityType.by_name("door")
        db.session.add(door)
        self.type = door


    @hybrid_method
    def between(self, first_loc, second_loc):
        return or_((self.left_location == first_loc) & (self.right_location == second_loc),
                   (self.right_location == first_loc) & (self.left_location == second_loc))

    def is_accessible(self):
        return self.has_property(P.WINDOW, data_kv={"open": True}) or self.has_property(P.OPEN_PASSAGE)

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    type_id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"))
    type = sql.orm.relationship(EntityType, uselist=False)

    left_location_id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"))
    right_location_id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"))

    left_location = sql.orm.relationship(Location, primaryjoin=left_location_id == Location.id,
                                         backref="left_passages", uselist=False)
    right_location = sql.orm.relationship(Location, primaryjoin=right_location_id == Location.id,
                                          backref="right_passages", uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_PASSAGE,
    }


class ScheduledTask(db.Model):
    __tablename__ = "scheduled_tasks"

    id = sql.Column(sql.Integer, primary_key=True)

    process_data = sql.Column(psql.JSON)
    execution_game_date = sql.Column(sql.BigInteger)
    execution_interval = sql.Column(sql.Integer, nullable=True)

    def __init__(self, process_json, execution_game_date, execution_interval=None):

        self.process_data = process_json
        self.execution_game_date = execution_game_date
        self.execution_interval = execution_interval

    def is_repeatable(self):
        return self.execution_interval is not None


class EntityRecipe(db.Model):
    __tablename__ = "entity_recipes"

    id = sql.Column(sql.Integer, primary_key=True)

    def __init__(self, name_tag, name_parameters, requirements, ticks_needed, build_menu_category,
                 result=None, result_entity=None):
        self.name_tag = name_tag
        self.name_parameters = name_parameters
        self.requirements = requirements
        self.ticks_needed = ticks_needed
        self.build_menu_category = build_menu_category
        self.result = result if result else []
        self.result_entity = result_entity

    name_tag = sql.Column(sql.String)
    name_parameters = sql.Column(psql.JSON)

    requirements = sql.Column(psql.JSON)
    ticks_needed = sql.Column(sql.Float)
    result = sql.Column(psql.JSON)  # a list of serialized Action constructors
    result_entity_id = sql.Column(sql.Integer, sql.ForeignKey(EntityType.id),
                                  nullable=True)  # EntityType being default result of the project
    result_entity = sql.orm.relationship(EntityType, uselist=False)

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

    resource_type = sql.Column(sql.Integer, sql.ForeignKey("item_types.id"))

    area = sql.Column(gis.Geometry("POLYGON"))

    @validates("area")
    def validate_position(self, key, area):  # we assume position is a Polygon
        return from_shape(area)

    quality = sql.Column(sql.Integer)  # amount collected per unit of time
    amount = sql.Column(sql.Integer)  # amount collected before the resource becomes unavailable


class TerrainType(EntityType):
    __tablename__ = "terrain_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    def __init__(self, name, color):
        super().__init__(name)
        self.color = color

    visibility = sql.Column(sql.Float)
    traversability = sql.Column(sql.Float)
    color = sql.Column(sql.SmallInteger)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_TERRAIN_AREA,
    }


class TerrainArea(Entity):
    __tablename__ = "terrain_areas"

    def __init__(self, terrain_poly, terrain_type, priority=1):
        self.terrain = terrain_poly
        self.priority = priority
        self.terrain_type = terrain_type

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    _terrain = sql.Column(gis.Geometry("POLYGON"))
    priority = sql.Column(sql.SmallInteger)
    terrain_type_id = sql.Column(sql.Integer, sql.ForeignKey("terrain_types.id"))
    terrain_type = sql.orm.relationship(TerrainType, uselist=False)


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

    if not EntityType.by_name("door"):
        db.session.merge(EntityType("door"))

    db.session.merge(EventType("event_drop_item_doer"))
    db.session.merge(EventType("event_drop_item_observer"))
    db.session.merge(EventType("event_drop_part_of_item_doer"))
    db.session.merge(EventType("event_drop_part_of_item_observer"))
    db.session.merge(EventType("event_take_item_doer"))
    db.session.merge(EventType("event_take_item_observer"))
    db.session.merge(EventType("event_take_part_of_item_doer"))
    db.session.merge(EventType("event_take_part_of_item_observer"))

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















