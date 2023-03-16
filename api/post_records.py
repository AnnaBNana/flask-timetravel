import logging
from typing import TYPE_CHECKING

from api.helpers import validate_record_id
from entity.record import Record
from service.record import SqliteRecordService, RecordDoesNotExistError

if TYPE_CHECKING:
    from entity.record import Record


logger = logging.getLogger(__name__)


record_service = SqliteRecordService


def post_records(id: str, data: dict[str, str]) -> "Record":
    """Gets record by id"""
    int_id = validate_record_id(id)

    try: # record exists
        record = record_service.get_record(int_id)
        record = record_service.update_record(int_id, data)

    except RecordDoesNotExistError as e:  # record does not exist
        logger.warn(f"Record not found {e}")
        # exclude deletions
        record_map = {}
        for key, value in data.items():
            if value:
                record_map[key] = value
        
        record = Record(int_id, record_map)
        record_service.create_record(record)
    
    return record
