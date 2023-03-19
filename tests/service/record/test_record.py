import pytest

import jsonpickle

from entity.record import Record
from service.record import SqliteRecordService, RecordDoesNotExistError
from tests.service.record.fixtures import dbname, cursor, conn


@pytest.fixture
def service(dbname):
    service = SqliteRecordService
    service.dbname = dbname
    yield service


def test_create_record(cursor, service):
    record_obj = Record(1, {"name": "Anna"})
    service.create_record(record_obj)

    record = cursor.execute("SELECT * FROM records").fetchone()

    assert jsonpickle.decode(record["data"]) == record_obj.data


def test_get_record(cursor, service):
    record_obj = Record(1, {"name": "Anna", "species": "human"})
    record = service.create_record(record_obj)

    record = service.get_record(record.id)

    assert record.data == record_obj.data


def test_get_record_throws(cursor, service):
    with pytest.raises(RecordDoesNotExistError):
        service.get_record(1)


def test_update_record(cursor, service):
    record_obj = Record(1, {"name": "Anna", "species": "human"})
    record = service.create_record(record_obj) 
    data = {"name": "Anna", "species": None, "language": "english"}

    record = service.update_record(record.id, data)

    assert record.data == {"name": "Anna", "language": "english"}

def test_update_record_throws(cursor, service):
    with pytest.raises(RecordDoesNotExistError):
        service.update_record(1, {"test": "data"})
