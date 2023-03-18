from typing import TYPE_CHECKING, Any

from api.exceptions import ResourceNotFound
from api.helpers import validate_record_id
from service.record import (
    SqliteRecordService,
    RecordDoesNotExistError,
    RecordRevisionHistoryService,
)

if TYPE_CHECKING:
    from entity.record import Record

record_service = SqliteRecordService
v2_record_service = RecordRevisionHistoryService


def get_records(id: str) -> "Record":
    """Gets record by id."""
    int_id = validate_record_id(id)

    try:
        return record_service.get_record(int_id)
    except RecordDoesNotExistError as e:
        raise ResourceNotFound from e


def get_records_v2(id: str, version: str = "latest") -> dict[str, Any]:
    """Gets record by id of specified version, defaults to latest"""
    int_id = validate_record_id(id)

    try:
        return v2_record_service.get_record(int_id, version)
    except RecordDoesNotExistError as e:
        raise ResourceNotFound from e


def get_versions_v2(id: str) -> list[int]:
    """Gets all versions for id."""
    return v2_record_service.get_versions(id)
