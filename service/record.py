import sqlite3
from datetime import datetime
from typing import Any

import jsonpickle

from api.helpers import update_data
from db import dbname
from entity.record import Record

RECORD_LEDGER: dict[Any, Any] = {}


class RecordError(Exception):
    """Raised when there us an error during record transaction."""


class RecordDoesNotExistError(LookupError, RecordError):
    """Raised when record lookup fails."""


class RecordAlreadyExistsError(RecordError):
    """Raised when record exists."""


class RecordService:
    """A base class for record services."""

    def get_record(self, slug: str, **kwargs: Any) -> "Record":
        """Get record by unique slug."""
        raise NotImplementedError

    def create_record(self, record: "Record", **kwargs: Any) -> None:
        """Create record from record data."""
        raise NotImplementedError

    def update_record(self, slug: str, data: dict[str, Any], **kwargs: Any) -> "Record":
        """Update record data according to data values."""
        raise NotImplementedError

    def get_versions(self, slug: str, **kwargs: Any) -> list[int]:
        """Get versions for slug."""
        raise NotImplementedError


class InMemoryRecordService(RecordService):
    """Record service implementation for in-memory storage."""

    def get_record(self, slug: str, **kwargs: Any) -> "Record":
        """Get in-memory record."""
        try:
            record = RECORD_LEDGER[slug]
        except KeyError as e:
            raise RecordDoesNotExistError from e

        return record

    def create_record(self, record: "Record", **kwargs: Any) -> None:
        """Create in-memory record."""
        if record.slug in RECORD_LEDGER:
            raise RecordAlreadyExistsError
        else:
            RECORD_LEDGER[record.slug] = record

    def update_record(self, slug: str, data: dict[str, Any], **kwargs: Any) -> "Record":
        """Update in-memory record."""
        entry = RECORD_LEDGER[slug]
        update_data(entry.data, data)

        return entry


class SqliteRecordService(RecordService):
    """Record service impplementation for Sqlite3."""

    db_name: str = dbname

    def get_record(self, slug: str, **kwargs: Any) -> "Record":
        """Get record by slug or raises error if record does not exist."""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            record = cursor.execute(
                "SELECT * FROM records WHERE slug = ?", (slug,)
            ).fetchone()

        try:
            data = jsonpickle.decode(record["data"])
            record_obj = Record(record["slug"], data)
        except TypeError as e:
            raise RecordDoesNotExistError from e

        return record_obj

    def create_record(self, record: "Record", **kwargs: Any) -> None:
        """Create record with data, key is ignored and auto-incremented."""
        pickled_data = jsonpickle.encode(record.data)

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO records (slug, data, created_at) VALUES (?, ?, ?)",
                (record.slug, pickled_data, record.timestamp),
            )

    def update_record(self, slug: str, data: dict[str, Any], **kwargs: Any) -> "Record":
        """Update record with changes to the data dict."""
        record = self.get_record(slug)
        update_data(record.data, data)
        pickled_data = jsonpickle.encode(record.data)

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE records SET data = ?, updated_at = ? WHERE slug = ?",
                (
                    pickled_data,
                    datetime.now(),
                    slug,
                ),
            )

        return record


class RecordRevisionHistoryService(RecordService):
    """Stores records in database with versioning."""

    db_name: str = dbname

    def get_record(self, slug: str, **kwargs: Any) -> "Record":
        """Get record by slug + version, defaults to latest."""
        version = kwargs.get("version", "latest")
        if version == "latest":
            record = self._get_latest(slug)
        else:
            record = self._get_version(slug, version)

        return record

    def _get_latest(self, slug: str) -> "Record":
        """Get record from versioned records table."""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT * FROM versioned_records WHERE slug = ?"

            record = cursor.execute(query, (slug,)).fetchone()

        if not record:
            raise RecordDoesNotExistError

        return Record(
            record["slug"],
            jsonpickle.decode(record["data"]),
            version=record["version"],
            timestamp=record["created_at"],
        )

    def _get_version(self, record_slug: str, version: str) -> "Record":
        """Get record of version from history table."""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            record_query = (
                "SELECT * FROM versioned_records WHERE slug = ? AND version = ?"
            )

            record = cursor.execute(
                record_query,
                (
                    record_slug,
                    version,
                ),
            ).fetchone()

            if not record:
                query = """SELECT records_slug as slug, version, timestamp as created_at, data
                        FROM history WHERE records_slug = ? AND version = ?"""

                record = cursor.execute(
                    query,
                    (
                        record_slug,
                        version,
                    ),
                ).fetchone()

        if not record:
            raise RecordDoesNotExistError

        return Record(
            record["slug"],
            jsonpickle.decode(record["data"]),
            version=record["version"],
            timestamp=record["created_at"],
        )

    def create_record(self, record: "Record", **kwargs: Any) -> None:
        """Create new record becomes latest with new version."""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """INSERT INTO versioned_records
                    (slug, data, version, created_at)
                    VALUES (?, ? , ?, ?)
                    """

            cursor.execute(
                query,
                (
                    record.slug,
                    jsonpickle.encode(record.data),
                    1,
                    record.timestamp,
                ),
            )

    def update_record(self, slug: str, data: dict[str, Any], **kwargs: Any) -> "Record":
        """Update record creates new record if version latest, else add new revision."""
        record = self.get_record(slug, **kwargs)

        if record.data == data:
            return record

        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # insert old_record into revision
            insert_revision_query = """INSERT INTO history
                        (records_slug, version, timestamp, data)
                        VALUES (?, ?, ?, ?)
                        """
            cursor.execute(
                insert_revision_query,
                (
                    record.slug,
                    record.version,
                    record.timestamp,
                    jsonpickle.encode(record.data),
                ),
            )

            update_data(record.data, data)
            # update record
            record.version += 1
            record.timestamp = datetime.now()
            update_record_query = """UPDATE versioned_records
                                SET data = ?, version = ?, created_at = ?
                                WHERE slug = ?
                                """
            cursor.execute(
                update_record_query,
                (
                    jsonpickle.encode(record.data),
                    record.version,
                    record.timestamp,
                    record.slug,
                ),
            )

        return record

    def get_versions(self, slug: str, **kwargs: Any) -> list[int]:
        """Get version numbers for slug."""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            current_version_query = """SELECT version FROM versioned_records
                                    WHERE slug = ?"""
            historical_versions_query = """SELECT version FROM history
                                        WHERE records_slug = ?"""

            current_version = cursor.execute(current_version_query, (slug,)).fetchone()
            historical_versions = cursor.execute(
                historical_versions_query, (slug,)
            ).fetchall()

        historical_versions.append(current_version)

        return [row["version"] for row in historical_versions]
