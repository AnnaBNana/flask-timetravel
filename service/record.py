import jsonpickle
import sqlite3
from datetime import datetime
from typing import Any, Type

from entity.record import Record
from api.helpers import update_data
from db import dbname


RECORD_LEDGER: dict[Any, Any] = {}


class RecordError(Exception):
    """Raised when there us an error during record transaction"""


class RecordDoesNotExistError(LookupError, RecordError):
    """Raised when record lookup fails."""


class RecordAlreadyExistsError(RecordError):
    """Raised when record exists."""


class RecordService:
    """A base class for record services"""

    record_class: Type[Record]

    def get_record(self, id: int) -> "Record":
        raise NotImplementedError

    def create_record(self, record: "Record") -> "Record":
        raise NotImplementedError

    def update_record(self, id: int, data: dict[str, str]) -> "Record":
        raise NotImplementedError


class InMemoryRecordService(RecordService):
    """Record service implementation for in-memory storage."""

    record_class = Record

    def get_record(self, id: int) -> "Record":
        try:
            record = RECORD_LEDGER[id]
        except KeyError as e:
            raise RecordDoesNotExistError from e

        return record

    def create_record(self, record: "Record") -> "Record":
        if record.id in RECORD_LEDGER:
            raise RecordAlreadyExistsError
        else:
            RECORD_LEDGER[record.id] = record

        return record

    def update_record(self, id: int, data: dict[str, str]) -> "Record":
        entry = RECORD_LEDGER[id]
        update_data(entry.data, data)

        return entry


class SqliteRecordService(RecordService):
    """Record service impplementation for Sqlite3."""

    dbname: str = dbname
    record_class = Record

    def get_record(self, id: int) -> "Record":
        """Gets record by id or raises error if record does not exist."""
        with sqlite3.connect(self.dbname) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            record = cursor.execute(
                "SELECT * FROM records WHERE id = ?", (id,)
            ).fetchone()

        try:
            data = jsonpickle.decode(record["data"])
            record_obj = Record(record["id"], data)
        except TypeError as e:
            raise RecordDoesNotExistError from e

        return record_obj

    def create_record(self, record: "Record") -> "Record":
        """Create record with data, key is ignored and auto-incremented."""
        pickled_data = jsonpickle.encode(record.data)

        with sqlite3.connect(self.dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO records (data, created_at) VALUES (?, ?)",
                (pickled_data, datetime.now()),
            )
            record.id = cursor.lastrowid

        return record

    def update_record(self, id: int, data: dict[str, str]) -> "Record":
        """Update record with changes to the data dict."""
        record = self.get_record(id)
        update_data(record.data, data)
        pickled_data = jsonpickle.encode(record.data)

        with sqlite3.connect(self.dbname) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE records SET data = ?, updated_at = ? WHERE id = ?",
                (
                    pickled_data,
                    datetime.now(),
                    id,
                ),
            )

        return record


class RecordRevisionHistoryService:
    """Stores records in database with versioning."""

    dbname: str = dbname

    @classmethod
    def get_record(cls, id: int, version: str = "latest") -> dict[str, Any]:
        """Get record by id + version, defaults to latest."""
        if version == "latest":
            record = cls._get_latest(id)
        else:
            record = cls._get_version(id, version)

        return record

    @classmethod
    def _get_latest(cls, id: int) -> dict[str, Any]:
        """Get record from versioned records table."""
        with sqlite3.connect(cls.dbname) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT * FROM versioned_records WHERE id = ?"

            record = cursor.execute(query, (id,)).fetchone()

        if not record:
            raise RecordDoesNotExistError

        record = dict(record)
        record["data"] = jsonpickle.decode(record["data"])

        return record

    @classmethod
    def _get_version(cls, record_id: int, version: str) -> dict[str, Any]:
        """Gets record of version from history table."""
        with sqlite3.connect(cls.dbname) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            record_query = (
                "SELECT * FROM versioned_records WHERE id = ? AND version = ?"
            )

            record = cursor.execute(
                record_query,
                (
                    record_id,
                    version,
                ),
            ).fetchone()

            if not record:
                query = "SELECT * FROM history WHERE records_id = ? AND version = ?"

                record = cursor.execute(
                    query,
                    (
                        record_id,
                        version,
                    ),
                ).fetchone()

        if not record:
            raise RecordDoesNotExistError

        record = dict(record)
        record["data"] = jsonpickle.decode(record["data"])

        return record

    @classmethod
    def create_record(cls, data: dict[str, Any]) -> None:
        """Create new record becomes latest with new version."""
        with sqlite3.connect(cls.dbname) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """INSERT INTO versioned_records
                    (data, version, created_at)
                    VALUES (? , ?, ?)
                    """

            cursor.execute(query, (jsonpickle.encode(data), 1, datetime.now()))

    @classmethod
    def update_record(cls, old_version: dict[str, Any], data: dict[str, Any]) -> None:
        """Update record creates new record if version latest, else add new revision."""
        # skip update if data is unuchanged
        if old_version["data"] == data:
            return

        with sqlite3.connect(cls.dbname) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # insert old_record into revision
            insert_revision_query = """INSERT INTO history
                        (records_id, version, timestamp, data)
                        VALUES (?, ?, ?, ?)
                        """
            cursor.execute(
                insert_revision_query,
                (
                    old_version["id"],
                    old_version["version"],
                    old_version["created_at"],
                    jsonpickle.encode(old_version["data"]),
                ),
            )

            update_data(old_version["data"], data)
            # update record
            version = old_version["version"] + 1
            update_record_query = """UPDATE versioned_records
                                SET data = ?, version = ?, created_at = ?
                                WHERE id = ?
                                """
            cursor.execute(
                update_record_query,
                (
                    jsonpickle.encode(old_version["data"]),
                    version,
                    datetime.now(),
                    old_version["id"],
                ),
            )

    @classmethod
    def _get_latest_version(cls, id: int) -> int:
        """Gets revision with highest version history from revision table."""
        query = """SELECT * FROM history where id = ? ORDER BY version"""
        with sqlite3.connect(cls.dbname) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            record = cursor.execute(query, (id,)).fetchone()

        if record:
            version = record.get("version", 0)
        else:
            version = 0

        return version

    @classmethod
    def get_versions(cls, id: int) -> list[int]:
        with sqlite3.connect(cls.dbname) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            current_version_query = """SELECT version FROM versioned_records
                                    WHERE id = ?"""
            historical_versions_query = """SELECT version FROM history
                                        WHERE records_id = ?"""

            current_version = cursor.execute(current_version_query, (id,)).fetchone()
            historical_versions = cursor.execute(
                historical_versions_query, (id,)
            ).fetchall()

        historical_versions.append(current_version)

        return [row["version"] for row in historical_versions]
