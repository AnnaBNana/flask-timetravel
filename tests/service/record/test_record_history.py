import pathlib
import sqlite3

import jsonpickle
import pytest

from entity.record import Record
from service.record import RecordRevisionHistoryService, RecordDoesNotExistError
from tests.service.record.fixtures import dbname, cursor, conn


@pytest.fixture
def service(dbname):
    service = RecordRevisionHistoryService()
    service.dbname = dbname
    yield service


def test_create_record(cursor, service):
    data = {"name": "Anna"}
    record = Record("1", data)
    service.create_record(record)

    record = cursor.execute("SELECT * FROM versioned_records").fetchone()

    assert jsonpickle.decode(record["data"]) == data
    assert record["version"] == 1


def test_get_latest_record_version(cursor, service):
    data = {"name": "Anna", "species": "human"}
    record = Record("1", data)
    service.create_record(record)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()

    record = service.get_record(last_inserted["id"])

    assert record.data == data
    assert record.version == 1


def test_get_raises(cursor, service):
    with pytest.raises(RecordDoesNotExistError):
        service.get_record(1)


def test_get_raises_with_version(cursor, service):
    data = {"name": "Anna", "species": "human"}
    record = Record("1", data)
    service.create_record(record)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()

    with pytest.raises(RecordDoesNotExistError):
        service.get_record(last_inserted["slug"], version=4)


def test_update_record(cursor, service):
    data = {"name": "Anna"}
    record = Record("1", data)
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(record)
    service.update_record(record.slug, data_v2)

    historical = cursor.execute(
        "SELECT * FROM history WHERE records_slug = ?", (record.slug,)
    ).fetchone()
    updated = cursor.execute(
        "SELECT * FROM versioned_records WHERE slug = ?", (record.slug,)
    ).fetchone()

    assert historical["version"] == 1
    assert updated["version"] == 2


def test_update_with_deletions(cursor, service):
    data = {"name": "Anna", "species": "human"}
    record = Record("1", data)
    data_v2 = {"name": "AnnaBNana", "species": None}
    service.create_record(record)
    service.update_record(record.slug, data_v2)

    historical = cursor.execute(
        "SELECT * FROM history WHERE records_slug = ?", (record.slug,)
    ).fetchone()
    updated = cursor.execute(
        "SELECT * FROM versioned_records WHERE slug = ?", (record.slug,)
    ).fetchone()

    assert historical["version"] == 1
    assert jsonpickle.decode(historical["data"]) == data
    assert updated["version"] == 2
    assert jsonpickle.decode(updated["data"]) == {"name": "AnnaBNana"}


def test_get_new_version(cursor, service):
    data = {"name": "Anna"}
    record = Record("1", data)
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(record)
    service.update_record(record.slug, data_v2)

    record = service.get_record(record.slug, version=2)

    assert record.version == 2
    assert record.data == data_v2


def test_get_old_version(cursor, service):
    data = {"name": "Anna"}
    record = Record("1", data)
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(record)
    service.update_record(record.slug, data_v2)

    record = service.get_record(record.slug, version=1)

    assert record.version == 1
    assert record.data == data


def test_get_latest_version(cursor, service):
    data = {"name": "Anna"}
    record = Record("1", data)
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(record)
    service.update_record(record.slug, data_v2)

    record = service.get_record(record.slug, version="latest")

    assert record.version == 2
    assert record.data == data_v2


def test_get_versions(cursor, service):
    data = {"name": "Anna"}
    record = Record("1", data)
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(record)
    service.update_record(record.slug, data_v2)

    versions = service.get_versions(record.slug)

    assert versions == [1, 2]
