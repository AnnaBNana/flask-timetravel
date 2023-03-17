from typing import TYPE_CHECKING

from api.exceptions import ResourceNotFound
from api.helpers import validate_record_id
from service.record import SqliteRecordService, RecordDoesNotExistError

if TYPE_CHECKING:
    from entity.record import Record

record_service = SqliteRecordService


def get_records(id: str) -> "Record":
    """Gets record by id."""
    int_id = validate_record_id(id)

    try:
        return record_service.get_record(int_id)
    except RecordDoesNotExistError as e:
        raise ResourceNotFound from e


def get_records_v2(id: str, version: str = "latest") -> "Record":
    """Gets record by id of specified version, defaults to latest"""