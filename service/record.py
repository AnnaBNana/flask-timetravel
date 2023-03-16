import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity.record import Record


class RecordError(Exception):
    """Raised when there us an error during record transaction"""


class RecordDoesNotExistError(LookupError, RecordError):
    """Raised when record lookup fails."""


class RecordAlreadyExistsError(RecordError):
    """Raised when record exists."""


class RecordService:
    """A base class for record services"""
    @classmethod
    def get_record(self, id: int) -> "Record":
        raise NotImplementedError

    @classmethod
    def create_record(self, record: "Record") -> None:
        raise NotImplementedError

    @classmethod
    def update_record(self, id: int, data: dict[str, str]) -> "Record":
        raise NotImplementedError


class InMemoryRecordService(RecordService):
    """Record service implementation for in-memory storage."""
    data: dict[int, "Record"] = {}

    @classmethod
    def get_record(cls, id: int) -> "Record":
        print(cls.data)
        try:
            record = cls.data[id]
        except KeyError as e:
            raise RecordDoesNotExistError from e

        return record

    @classmethod
    def create_record(cls, record: "Record") -> None:
        if record.id in cls.data:
            raise RecordAlreadyExistsError
        else:
            cls.data[record.id] = record
        
        print(cls.data)

    @classmethod
    def update_record(cls, id: int, data: dict[str, str]) -> "Record":
        entry = cls.data[id]

        for key, value in data.items():
            if value:
                entry.data[key] = value
            else:
                entry.data.pop(key, None)

        return entry


class SqliteRecordService(RecordService):
    """Record service impplementation for Sqlite3."""
    @classmethod
    def _get_cursor(cls):
        return sqlite3.connect("record-service.db")
    
    @classmethod
    def get_record(self, id: int) -> "Record":
        return super().get_record(id)

    @classmethod
    def create_record(self, record: "Record") -> None:
        return super().create_record(record)
    
    @classmethod
    def update_record(self, id: int, data: dict[str, str]) -> "Record":
        return super().update_record(id, data)
