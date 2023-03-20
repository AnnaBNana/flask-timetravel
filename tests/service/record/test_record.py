from typing import TYPE_CHECKING, Generator

import jsonpickle
import pytest

from entity.record import Record
from service.record.base import RecordDoesNotExistError
from service.record.v1 import SqliteRecordService

if TYPE_CHECKING:
    from sqlite3 import Cursor


@pytest.fixture
def service(dbname: str) -> Generator[SqliteRecordService, None, None]:
    service = SqliteRecordService()
    service.db_name = dbname
    yield service


def test_create_record(cursor: "Cursor", service: SqliteRecordService) -> None:
    record_obj = Record("1", {"name": "Anna"})
    service.create_record(record_obj)

    record = cursor.execute("SELECT * FROM records").fetchone()

    assert jsonpickle.decode(record["data"]) == record_obj.data


def test_get_record(cursor: "Cursor", service: SqliteRecordService) -> None:
    record_obj = Record("1", {"name": "Anna", "species": "human"})
    service.create_record(record_obj)

    record = service.get_record(record_obj.slug)

    assert record.data == record_obj.data


def test_get_record_throws(cursor: "Cursor", service: SqliteRecordService) -> None:
    with pytest.raises(RecordDoesNotExistError):
        service.get_record("1")


def test_update_record(cursor: "Cursor", service: SqliteRecordService) -> None:
    data = {"name": "Anna", "species": "human"}
    record = Record("1", data)
    service.create_record(record)
    data_v2 = {"name": "Anna", "species": None, "language": "english"}

    service.update_record(record.slug, data_v2)

    updated_record = service.get_record(record.slug)

    assert updated_record.data == {"name": "Anna", "language": "english"}


def test_update_record_throws(cursor: "Cursor", service: SqliteRecordService) -> None:
    with pytest.raises(RecordDoesNotExistError):
        service.update_record("1", {"test": "data"})
