import logging
from typing import TYPE_CHECKING, Any

from api.exceptions import ResourceNotFound
from entity.record import Record
from service.record.base import RecordDoesNotExistError

if TYPE_CHECKING:
    from service.record.base import RecordService

logger = logging.getLogger(__name__)


class API:
    """Record API."""

    def __init__(self, service: "RecordService") -> None:
        """Create a Record API instance."""
        self.service = service

    def get_records(self, id: str, **kwargs: Any) -> "Record":
        """Get record by id."""
        try:
            return self.service.get_record(id, **kwargs)
        except RecordDoesNotExistError as e:
            raise ResourceNotFound from e

    def post_records(self, id: str, data: dict[str, str | None], **kwargs: Any) -> None:
        """Create record or update if exists."""
        try:  # record exists
            self.service.get_record(id, **kwargs)
            self.service.update_record(id, data, **kwargs)

        except RecordDoesNotExistError as e:  # record does not exist
            logger.warn(f"Record not found {e}")
            # exclude deletions
            revised_data = {k: v for k, v in data.items() if v}

            self.service.create_record(Record(id, revised_data, **kwargs))

    def get_versions(self, id: str, **kwargs: Any) -> list[int]:
        """Get all versions by id."""
        return self.service.get_versions(id, **kwargs)
