from typing import TYPE_CHECKING

from service.record import InMemoryRecordService, RecordDoesNotExistError
from werkzeug.exceptions import HTTPException

if TYPE_CHECKING:
    from entity.record import Record

record_service = InMemoryRecordService()


class ResourceNotFound(HTTPException):
    code = 404


def get_records(id) -> "Record":
    """Gets record by id"""
    try:
        return record_service.get_record(id)
    except RecordDoesNotExistError as e:
        raise ResourceNotFound from e
