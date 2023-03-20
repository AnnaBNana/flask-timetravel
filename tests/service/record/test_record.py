import pytest

import jsonpickle

from entity.record import Record
from service.record import SqliteRecordService, RecordDoesNotExistError
from tests.service.record.fixtures import dbname, cursor, conn


@pytest.fixture
def service(dbname):
    service = SqliteRecordService()
    service.dbname = dbname
    yield service


def test_create_record(cursor, service):
    record_obj = Record(1, {"name": "Anna"})
    service.create_record(record_obj)

    record = cursor.execute("SELECT * FROM records").fetchone()

    assert jsonpickle.decode(record["data"]) == record_obj.data


def test_get_record(cursor, service):
    record_obj = Record("1", {"name": "Anna", "species": "human"})
    service.create_record(record_obj)

    record = service.get_record(record_obj.slug)

    assert record.data == record_obj.data


def test_get_record_throws(cursor, service):
    with pytest.raises(RecordDoesNotExistError):
        service.get_record(1)


def test_update_record(cursor, service):
    data = {"name": "Anna", "species": "human"}
    record = Record("1", data)
    service.create_record(record) 
    data_v2 = {"name": "Anna", "species": None, "language": "english"}

    service.update_record(record.slug, data_v2)

    updated_record = service.get_record(record.slug)

    assert updated_record.data == {"name": "Anna", "language": "english"}

def test_update_record_throws(cursor, service):
    with pytest.raises(RecordDoesNotExistError):
        service.update_record(1, {"test": "data"})
