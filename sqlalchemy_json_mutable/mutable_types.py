import sqlalchemy
from sqlalchemy.ext import mutable
import sqlalchemy.dialects.postgresql as psql

from . import tracked_impl


class NestedMutableDict(mutable.MutableDict, tracked_impl.TrackedDict):
    """SQLAlchemy `mutable` extension dictionary with nested change tracking."""

    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionary to NestedMutableDict."""
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(value)
        return super(NestedMutableDict, cls).coerce(key, value)


class NestedMutableList(mutable.MutableList, tracked_impl.TrackedList):
    """SQLAlchemy `mutable` extension list with nested change tracking."""

    @classmethod
    def coerce(cls, key, value):
        """Convert plain list to NestedMutableList."""
        if isinstance(value, cls):
            return value
        if isinstance(value, list):
            return cls(value)
        return super(NestedMutableList, cls).coerce(key, value)


class _JsonTypeDecorator(sqlalchemy.TypeDecorator):
    impl = psql.JSONB

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value


class ShallowJsonDict(_JsonTypeDecorator):
    """JSON-based type with change tracking as base level"""


class JsonDict(_JsonTypeDecorator):
    """JSON dict type for SQLAlchemy with nested change tracking"""


class ShallowJsonList(_JsonTypeDecorator):
    """JSON-based list type with change tracking as base level"""


class JsonList(_JsonTypeDecorator):
    """JSON list type for SQLAlchemy with nested change tracking"""


mutable.MutableDict.associate_with(ShallowJsonDict)
NestedMutableDict.associate_with(JsonDict)

mutable.MutableList.associate_with(ShallowJsonList)
NestedMutableList.associate_with(JsonList)
