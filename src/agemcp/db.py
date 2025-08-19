from __future__ import annotations

import json

from collections import UserList
from contextlib import AbstractAsyncContextManager, AsyncContextDecorator, AsyncExitStack
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Self, TypeVar

from sqlalchemy.engine import Row
from sqlalchemy.orm import declarative_base

from agemcp.settings import get_settings


IDENT_PROPERTY = get_settings().age.ident_property

Base = declarative_base()

def decode_record(record: Row) -> dict:
    """
    Decodes a single SQLAlchemy Row object containing AGE agtype strings into a dictionary.

    Iterates through each key-value pair in the Row. If a value is a string containing '::',
    it is assumed to be an agtype string and is decoded using `decode_agtype_string`.
    Otherwise, the value is added as-is.

    Args:
        record (Row): A SQLAlchemy Row object potentially containing agtype strings.

    Returns:
        dict: A dictionary with decoded agtype values where applicable.
    """
    result = {}
    for key, value in record.items():
        if isinstance(value, str) and '::' in value:
            # This is an agtype string, decode it
            value = decode_agtype_string(value)
        result[key] = value
    return result

def decode_agtype_string(agtype_string: str) -> Any:
    """Decodes a single agtype string into a Python object.

    This function attempts to parse the input agtype string as either a JSON object or array.
    If the string does not match these formats, it returns the string itself.

    Args:
        agtype_string (str): The agtype string to decode.

    Returns:
        Any: The decoded Python object, or the original string if decoding is not possible.
    """
    # Placeholder implementation - replace with actual decoding logic
    if agtype_string.startswith('{') and agtype_string.endswith('}'):
        # This looks like a JSON object
        return json.loads(agtype_string)
    elif agtype_string.startswith('[') and agtype_string.endswith(']'):
        # This looks like a JSON array
        return json.loads(agtype_string)
    else:
        # Fallback to returning the string itself
        return agtype_string

def decode_asyncio_agtype_recordset(records: list[Row]) -> list[dict]:
    """Decodes a list of asyncpg.Record objects containing AGE agtype strings.

    Efficiently decodes a list of asyncpg.Record objects containing AGE agtype strings
    into a list of dictionaries, using a single json.loads call on a constructed JSON array.
    This version concatenates all agtype strings with commas, replaces '::vertex' and '::edge' with '',
    and wraps the result in brackets.

    Args:
        records (list[Row]): A list of asyncpg.Record or SQLAlchemy Row objects containing agtype strings.

    Returns:
        list[dict]: A list of dictionaries decoded from the agtype strings. Returns an empty list if no agtype strings are found.
    """
    agtype_strings = [
        value for record in records
        for value in (record._mapping.values() if hasattr(record, '_mapping') else record.values())
        if isinstance(value, str) and '::' in value
    ]
    if not agtype_strings:
        return []

    # Concatenate all objects into one string, separated by commas
    concat = ','.join(agtype_strings)
    # Remove both ::vertex and ::edge suffixes from the string
    concat = concat.replace('::vertex', '')
    concat = concat.replace('::edge',   '')
    # Wrap in brackets to form a JSON array
    json_array = '[' + concat + ']'
    return json.loads(json_array)

@dataclass
class DbRecord:
    """Base class for database records.

    Provides common serialization and deserialization methods for database records,
    including conversion to and from dictionaries and JSON strings.
    """
    
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the record to a dictionary."""
        return asdict(self, dict_factory=dict)
    
    def to_json(self) -> str:
        """Convert the record to a JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_data: str) -> Self:
        """Convert a JSON string into a record."""
        data = json.loads(json_data)
        return cls.from_dict(data)

@dataclass
class AgtypeRecord(DbRecord):
    """Represents an AGE agtype record.

    Used for both vertices and edges in the AGE graph database. Contains label,
    properties, and optional identifiers for vertices and edges.
    """
    label      : str
    properties : Dict[str, Any] = field(default_factory=dict)
    id         : int | None = None
    start_id   : int | None = None
    end_id     : int | None = None


    _type       : Literal['vertex', 'edge'] | None = field(default=None, init=True, repr=False)

    def __post_init__(self):
        if self.label is None:
            raise TypeError("AgtypeRecord requires a 'label' field.")
        if self.properties is None:
            self.properties = {}

    @property
    def type(self) -> Literal['vertex', 'edge']:
        """Determine if this record is a vertex or an edge based on its properties."""
        if self._type is not None:
            return self._type # faster if set.
        return 'edge' if self.start_id is not None and self.end_id is not None else 'vertex'
    
    @property
    def is_vertex(self) -> bool: return self.type == 'vertex'
    
    @property
    def is_edge(self) -> bool: return self.type == 'edge'

    @classmethod
    def from_raw_records(cls, records: List[Row]) -> List[Self]:
        """Convert a list of asyncpg.Record to a list of DbRecord."""
        dicts : List[Dict] = decode_asyncio_agtype_recordset(records)
        return [cls.from_dict(record) for record in dicts]
