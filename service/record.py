import jsonpickle
import sqlite3

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
    def get_record(cls, id: int) -> "Record":
        raise NotImplementedError

    @classmethod
    def create_record(cls, record: "Record") -> "Record":
        raise NotImplementedError

    @classmethod
    def update_record(cls, id: int, data: dict[str, str]) -> "Record":
        raise NotImplementedError


class InMemoryRecordService(RecordService):
    """Record service implementation for in-memory storage."""
    data: dict[int, "Record"] = {}

    @classmethod
    def get_record(cls, id: int) -> "Record":
        try:
            record = cls.data[id]
        except KeyError as e:
            raise RecordDoesNotExistError from e

        return record

    @classmethod
    def create_record(cls, record: "Record") -> "Record":
        if record.id in cls.data:
            raise RecordAlreadyExistsError
        else:
            cls.data[record.id] = record

        return record

    @classmethod
    def update_record(cls, id: int, data: dict[str, str]) -> "Record":
        entry = cls.data[id]
        entry.update_data(data)

        return entry


class SqliteRecordService(RecordService):
    """Record service impplementation for Sqlite3."""

    @classmethod
    def get_record(cls, id: int) -> "Record":
        """Gets record by id or raises error if record does not exist."""
        db_connection = sqlite3.connect('record-service.db')
        db_connection.row_factory = sqlite3.Row
        cursor = db_connection.cursor()
        record = cursor.execute("SELECT * FROM Records WHERE id = ?", (id,)).fetchone()
        db_connection.close()

        try:
            record_obj = Record(record["id"], jsonpickle.decode(record["data"]))
        except TypeError as e:
            raise RecordDoesNotExistError from e
    
        return record_obj

    @classmethod
    def create_record(cls, record: "Record") -> "Record":
        """Create record with data, key is ignored and auto-incremented."""
        db_connection = sqlite3.connect('record-service.db')
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO Records (data) VALUES (?)", (jsonpickle.encode(record.data),))
        record.id = cursor.lastrowid

        db_connection.commit()
        db_connection.close()

        return record
    
    @classmethod
    def update_record(cls, id: int, data: dict[str, str]) -> "Record":
        """Update record with changes to the data dict."""
        record = cls.get_record(id)
        record.update_data(data)
        
        pickled_data = jsonpickle.encode(record.data)

        db_connection = sqlite3.connect('record-service.db')
        cursor = db_connection.cursor()
        cursor.execute("UPDATE Records SET data = ? WHERE id = ?", (pickled_data, id,))

        db_connection.commit()
        db_connection.close()

        return record
