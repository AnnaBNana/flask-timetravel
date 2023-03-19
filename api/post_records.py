import logging
from typing import TYPE_CHECKING

from api.helpers import validate_record_id
from service.record import (
    RecordDoesNotExistError,
    RecordRevisionHistoryService,
)


logger = logging.getLogger(__name__)


v2_record_service = RecordRevisionHistoryService


def post_records_v2(id: str, data: dict[str, str], version: str = "latest") -> None:
    """Creates new record by id of specified version, defaults to latest."""
    int_id = validate_record_id(id)

    try:
        record = v2_record_service.get_record(int_id, version)
        v2_record_service.update_record(record, data)

    except RecordDoesNotExistError as e:
        logger.warn(f"Record not found {e}")
        # exclude deletions
        record_map = {k: v for k, v in data.items() if v}

        v2_record_service.create_record(record_map)
