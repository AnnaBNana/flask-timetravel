import logging
from typing import TYPE_CHECKING

from api.helpers import validate_record_id
from entity.record import Record
from service.record import SqliteRecordService, RecordDoesNotExistError, RecordRevisionHistoryService

if TYPE_CHECKING:
    from entity.record import Record


logger = logging.getLogger(__name__)


record_service = SqliteRecordService
v2_record_service = RecordRevisionHistoryService


def post_records(id: str, data: dict[str, str]) -> "Record":
    """Gets record by id"""
    int_id = validate_record_id(id)

    try: # record exists
        record = record_service.get_record(int_id)
        record = record_service.update_record(int_id, data)

    except RecordDoesNotExistError as e:  # record does not exist
        logger.warn(f"Record not found {e}")
        # exclude deletions
        record_map = {k: v for k, v in data.items() if v}
        
        record = Record(int_id, record_map)
        record_service.create_record(record)
    
    return record


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

        v2_record_service.create_record(data, version)
