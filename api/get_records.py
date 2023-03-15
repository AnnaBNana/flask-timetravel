from typing import TYPE_CHECKING

from api.exceptions import ResourceNotFound
from api.helpers import validate_record_id
from service.record import InMemoryRecordService, RecordDoesNotExistError

if TYPE_CHECKING:
    from entity.record import Record

record_service = InMemoryRecordService


def get_records(id: str) -> "Record":
    """Gets record by id."""
    int_id = validate_record_id(id)

    try:
        return record_service.get_record(int_id)
    except RecordDoesNotExistError as e:
        raise ResourceNotFound from e
