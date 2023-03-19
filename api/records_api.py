import logging
from typing import TYPE_CHECKING

from api.helpers import validate_record_id
from api.exceptions import ResourceNotFound
from entity.record import Record
from service.record import RecordDoesNotExistError

if TYPE_CHECKING:
    from service.record import RecordService

logger = logging.getLogger(__name__)


class API:
    def __init__(self, service: "RecordService") -> None:
        self.service = service

    def get_records(self, id: str) -> Record:
        """Gets record by id."""
        int_id = validate_record_id(id)

        try:
            return self.service.get_record(int_id)
        except RecordDoesNotExistError as e:
            raise ResourceNotFound from e

    def post_records(self, id: str, data: dict[str, str]) -> Record:
        """Gets record by id"""
        int_id = validate_record_id(id)

        try:  # record exists
            record = self.service.get_record(int_id)
            record = self.service.update_record(int_id, data)

        except RecordDoesNotExistError as e:  # record does not exist
            logger.warn(f"Record not found {e}")
            # exclude deletions
            record_map = {k: v for k, v in data.items() if v}

            record = self.service.create_record(Record(int_id, record_map))

        return record