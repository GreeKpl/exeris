import types
import geoalchemy2 as gis
from pygeoif import Point, geometry
from sqlalchemy.ext.hybrid import hybrid_property
from exeris.core import properties
from exeris.core.main import db
from sqlalchemy.orm import validates
from exeris.core.properties import EntityPropertyException

__author__ = 'Aleksander Chrabąszcz'

import sqlalchemy as sql
import sqlalchemy.orm
import sqlalchemy.dialects.postgresql as psql
import sqlalchemy.ext.declarative as decl
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
ENTITY_VISIBILITY_AREA = 10
ENTITY_TRAVERSABILITY_AREA = 11
ENTITY_RESOURCE_AREA = 12


class Player(db.Model):
    __tablename__ = "players"

    id = sql.Column(sql.Integer, primary_key=True)

    SEX_MALE = "m"
    SEX_FEMALE = "f"

    login = sql.Column(sql.String(24), unique=True)
    email = sql.Column(sql.String(32), unique=True)
    register_date = sql.Column(sql.Date)
    password = sql.Column(sql.String)
    sex = sql.Column(sql.Enum(SEX_MALE, SEX_FEMALE, name="sex"))  # used to have correct translations

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

    name = sql.Column(sql.String(32))  # no spaces allowed

    type = sql.Column(sql.SmallInteger)  # discriminator

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": type,
    }


class ItemType(EntityType):
    __tablename__ = "item_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class Entity(db.Model):
    """
    Abstract base for all entities in the game, like items or locations
    """
    __tablename__ = "entities"

    ROLE_CONSISTED = 1
    ROLE_CONTAINED = 2

    id = sql.Column(sql.Integer, primary_key=True)
    weight = sql.Column(sql.Integer)

    being_in_id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), nullable=True)
    being_in = sql.orm.relationship("Entity", uselist=False)
    role = sql.id = sql.Column(sql.SmallInteger, nullable=True)

    def __getattr__(self, item):
        try:
            method = properties.get_method(item)
            return types.MethodType(method, self)  # return method type with updated self
        except KeyError:
            try:
                super().__getattr__(item)
            except AttributeError:
                raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__, item))

    def has_property(self, name):
        entity_property_exists = EntityProperty.query.filter_by(entity=self, name=name).count() > 0

        if entity_property_exists:
            return True

        return EntityTypeProperty.query.filter_by(type=self.type, name=name).count() > 0

    discriminator_type = sql.Column(sql.SmallInteger)  # discriminator

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": discriminator_type,
    }


class LocationType(EntityType):
    __tablename__ = "location_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_LOCATION,
    }


class Character(Entity):
    __tablename__ = "characters"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    SEX_MALE = "m"
    SEX_FEMALE = "f"

    name = sql.Column(sql.String)
    sex = sql.Column(sql.Enum(SEX_MALE, SEX_FEMALE, name="sex"))
    player_id = sql.Column(sql.Integer, sql.ForeignKey('players.id'))
    player = sql.orm.relationship(Player, uselist=False)

    spawn_date = sql.Column(sql.BigInteger)
    spawn_location = sql.Column(gis.Geometry("POINT"))

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_CHARACTER,
    }


class Item(Entity):
    __tablename__ = "items"

    def __init__(self, type, being_in, weight):
        self.type = type
        self.being_in = being_in
        self.weight = weight
        self.role = Entity.ROLE_CONTAINED

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    type_id = sql.Column(sql.Integer, sql.ForeignKey("item_types.id"))
    type = sql.orm.relationship(ItemType, uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class ActivityType(EntityType):
    __tablename__ = "activity_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ACTIVITY,
    }


class Activity(Entity):
    __tablename__ = "activities"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

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
    group_id = sql.Column(sql.Integer, sql.ForeignKey("event_type_groups.id"))
    group = sql.orm.relationship(EventTypeGroup, uselist=False)


class Event(db.Model):
    __tablename__ = "events"

    id = sql.Column(sql.Integer, primary_key=True)
    type_name = sql.Column(sql.String, sql.ForeignKey("event_types.name"))
    type = sql.orm.relationship(EventType, uselist=False)
    parameters = sql.Column(psql.JSON)
    date = sql.Column(sql.BigInteger)


class EventObserver(db.Model):
    __tablename__ = "event_observers"

    observer_id = sql.Column(sql.Integer, sql.ForeignKey(Character.id), primary_key=True)
    observer = sql.orm.relationship(Character, uselist=False)
    event_id = sql.Column(sql.Integer, sql.ForeignKey(Event.id), primary_key=True)
    event = sql.orm.relationship(Event, uselist=False)
    times_seen = sql.Column(sql.Integer)


class EntityTypeProperty(db.Model):
    __tablename__ = "entity_type_properties"

    type_id = sql.Column(sql.Integer, sql.ForeignKey(EntityType.id), primary_key=True)
    type = sql.orm.relationship(EntityType, uselist=False)

    name = sql.Column(sql.String, primary_key=True)
    data = sql.Column(psql.JSON)


class EntityProperty(db.Model):
    __tablename__ = "entity_properties"

    entity_id = sql.Column(sql.Integer, sql.ForeignKey(Entity.id), primary_key=True)
    entity = sql.orm.relationship(Entity, uselist=False)

    name = sql.Column(sql.String, primary_key=True)
    data = sql.Column(psql.JSON)

    type = sql.Column(sql.SmallInteger)

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": type,
    }


class Location(Entity):
    __tablename__ = "locations"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    def __init__(self, weight, being_in):
        self.weight = weight
        self.being_in = being_in
        self.role = Entity.ROLE_CONTAINED

    @hybrid_property
    def neighbours(self):
        neighbours = [passage.left_location for passage in self.right_passages]
        neighbours.extend([passage.right_location for passage in self.left_passages])
        return neighbours

    def get_root(self):
        if type(self) is RootLocation:
            return self
        else:
            return self.being_in.get_root()

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
        super().__init__(0, None)
        self.position = position
        self.is_mobile = is_mobile
        self.direction = direction

    @validates("direction")
    def validate_direction(self, key, direction):
        return direction % 360

    @hybrid_property
    def position(self):
        return geometry.from_wkt(self._position)

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
        self._position = Point(x, y).to_wkt()

    @position.expression
    def position(cls):
        return cls._position


    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ROOT_LOCATION,
    }


class Passage(Entity):
    __tablename__ = "passages"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    left_location_id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"))
    right_location_id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"))

    left_location = sql.orm.relationship(Location, primaryjoin=left_location_id == Location.id,
                                         backref="left_passages", uselist=False)
    right_location = sql.orm.relationship(Location, primaryjoin=right_location_id == Location.id,
                                          backref="right_passages", uselist=False)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_PASSAGE,
    }


class ResourceArea(Entity):
    __tablename__ = "resource_areas"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    resource_type = sql.Column(sql.Integer, sql.ForeignKey("item_types.id"))

    area = sql.Column(gis.Geometry("POLYGON"))

    @validates("area")
    def validate_position(self, key, area):  # we assume position is a Polygon
        return area.to_wkt()

    quality = sql.Column(sql.Integer)  # amount collected per unit of time
    amount = sql.Column(sql.Integer)  # amount collected before the resource becomes unavailable

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_RESOURCE_AREA,
    }


class TerrainType(EntityType):
    __tablename__ = "terrain_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    visibility = sql.Column(sql.Float)
    traversability = sql.Column(sql.Float)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_TERRAIN_AREA,
    }


class TerrainArea(Entity):
    __tablename__ = "terrain_areas"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    area = sql.Column(gis.Geometry("POLYGON"))

    @validates("area")
    def validate_position(self, key, area):  # we assume position is a Polygon
        return area.to_wkt()

    type = sql.Column(sql.Integer, sql.ForeignKey("terrain_types.id"))

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_TERRAIN_AREA,
    }


class VisibilityArea(Entity):
    __tablename__ = "visibility_areas"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    area = sql.Column(gis.Geometry("POLYGONM"))

    @validates("area")
    def validate_position(self, key, area):  # we assume position is a Polygon
        return area.to_wkt()

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_VISIBILITY_AREA,
    }


class TraversabilityArea(Entity):
    __tablename__ = "traversability_areas"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    area = sql.Column(gis.Geometry("POLYGONM"))

    @validates("area")
    def validate_position(self, key, area):  # we assume position is a Polygon
        return area.to_wkt()

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_TRAVERSABILITY_AREA,
    }
