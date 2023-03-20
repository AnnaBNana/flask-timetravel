import logging
from typing import TYPE_CHECKING

from api.exceptions import ResourceNotFound
from entity.record import Record
from service.record import RecordDoesNotExistError

if TYPE_CHECKING:
    from service.record import RecordService

logger = logging.getLogger(__name__)


class API:
    def __init__(self, service: "RecordService") -> None:
        self.service = service

    def get_records(self, id: str, **kwargs) -> "Record":
        """Gets record by id."""
        try:
            return self.service.get_record(id, **kwargs)
        except RecordDoesNotExistError as e:
            raise ResourceNotFound from e

    def post_records(self, id: str, data: dict[str, str], **kwargs) -> None:
        """Gets record by id"""
        try:  # record exists
            record = self.service.get_record(id, **kwargs)
            self.service.update_record(id, data, **kwargs)

        except RecordDoesNotExistError as e:  # record does not exist
            logger.warn(f"Record not found {e}")
            # exclude deletions
            revised_data = {k: v for k, v in data.items() if v}

            self.service.create_record(Record(id, revised_data, **kwargs))
    
    def get_versions(self, id: str, **kwargs) -> list[int]:
        """Gets all versions for id."""
        return self.service.get_versions(id, **kwargs)
