import sqlite3
from datetime import datetime
from typing import Any

import jsonpickle

from db import dbname
from entity.record import Record
from service.record.base import RecordDoesNotExistError, RecordService


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
        record.update_data(data)
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
