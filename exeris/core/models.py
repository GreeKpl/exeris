__author__ = 'Aleksander Chrabąszcz'

import sqlalchemy as sql
import sqlalchemy.orm
import sqlalchemy.dialects.postgresql as psql
import sqlalchemy.ext.declarative as decl

Base = decl.declarative_base()


class Player(Base):
    __tablename__ = "players"

    id = sql.Column(sql.Integer, primary_key=True)

    SEX_MALE = "m"
    SEX_FEMALE = "f"

    login = sql.Column(sql.String(24), unique=True)
    email = sql.Column(sql.String(32), unique=True)
    register_date = sql.Column(sql.Date)
    password = sql.Column(sql.String)
    sex = sql.Column(sql.Enum(SEX_MALE, SEX_FEMALE))  # used to have correct translations

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.login


class EntityType(Base):
    __tablename__ = "entity_types"

    id = sql.Column(sql.Integer, primary_key=True)

    name = sql.Column(sql.String(32))  # no spaces allowed
    type = sql.Column(sql.SmallInteger)  # discriminator

    ENTITY_BASE = 1

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": type,
    }


class ItemType(EntityType):
    __tablename__ = "item_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    ENTITY_ITEM = 3

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class Entity(Base):
    """
    Abstract base for all entities in the game, like items or locations
    """
    __tablename__ = "entities"

    id = sql.Column(sql.Integer, primary_key=True)
    weight = sql.Column(sql.Integer)
    type = sql.Column(sql.SmallInteger)  # discriminator

    ENTITY_BASE = 1

    __mapper_args__ = {
        "polymorphic_identity": ENTITY_BASE,
        "polymorphic_on": type,
    }


class LocationType(EntityType):
    __tablename__ = "item_types"

    id = sql.Column(sql.Integer, sql.ForeignKey("entity_types.id"), primary_key=True)

    ENTITY_LOCATION = 5

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_LOCATION,
    }


class Character(Entity):
    __tablename__ = "characters"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    SEX_MALE = "m"
    SEX_FEMALE = "f"

    name = sql.Column(sql.String)
    sex = sql.Column(sql.Enum(SEX_MALE, SEX_FEMALE))
    player_id = sql.Column(sql.Integer, sql.ForeignKey('players.id'))
    player = sql.orm.relationship(Player)

    ENTITY_CHARACTER = 2

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_CHARACTER,
    }


class Item(Entity):
    __tablename__ = "items"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    ENTITY_ITEM = 3

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ITEM,
    }


class GameDate(Base):
    __tablename__ = "game_date"

    id = sql.Column(sql.Integer, primary_key=True)
    date = sql.Column(sql.BigInteger)


class EventTypeGroup(Base):
    __tablename__ = "event_type_groups"

    id = sql.Column(sql.Integer, primary_key=True)


class EventType(Base):
    __tablename__ = "events"

    CRITICAL = 10
    IMPORTANT = 6
    NORMAL = 4
    IRRELEVANT = 2

    name = sql.Column(sql.String, primary_key=True)
    severity = sql.Column(sql.SmallInteger)
    group_id = sql.Column(sql.Integer)
    group = sql.orm.relationship(EventTypeGroup)


class Event(Base):
    __tablename__ = "events"

    id = sql.Column(sql.Integer, primary_key=True)
    type_name = sql.Column(sql.String)
    type = sql.orm.relationship(EventType)
    parameters = sql.Column(psql.JSON)
    date = sql.Column(sql.BigInteger)


class EventObserver(Base):
    __tablename__ = "event_observers"

    observer_id = sql.Column(sql.Integer, sql.ForeignKey(Character.id))
    observer = sql.orm.relationship(Character)
    event_id = sql.Column(sql.Integer, sql.ForeignKey(Event.id))
    event = sql.orm.relationship(Event)
    times_seen = sql.Column(sql.Integer)


class TypeProperty(Base):
    __tablename__ = "type_properties"

    value = sql.Column(psql.JSON)
    type_id = sql.Column(sql.Integer, sql.ForeignKey(EntityType.id))
    type = sql.orm.relationship(EntityType)


class EntityProperty(Base):
    __tablename__ = "entity_properties"

    value = sql.Column(psql.JSON)
    entity_id = sql.Column(sql.Integer, sql.ForeignKey(Entity.id))
    entity = sql.orm.relationship(Entity)


class Location(Entity):
    __tablename__ = "locations"

    id = sql.Column(sql.Integer, sql.ForeignKey("entities.id"), primary_key=True)

    ENTITY_LOCATION = 5

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_LOCATION,
    }


class RootLocation(Location):
    __tablename__ = "root_locations"

    id = sql.Column(sql.Integer, sql.ForeignKey("locations.id"), primary_key=True)

    ENTITY_ROOT_LOCATION = 6

    x = sql.Column(sql.Float)
    y = sql.Column(sql.Float)
    is_mobile = sql.Column(sql.Boolean)

    __mapper_args__ = {
        'polymorphic_identity': ENTITY_ROOT_LOCATION,
    }

