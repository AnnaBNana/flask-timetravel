from typing import TYPE_CHECKING, Any

from service.record.base import (
    RecordAlreadyExistsError,
    RecordDoesNotExistError,
    RecordService,
)
from service.record.helpers import update_data

if TYPE_CHECKING:
    from entity.record import Record

RECORD_LEDGER: dict[Any, Any] = {}


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
