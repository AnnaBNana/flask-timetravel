import pathlib
import sqlite3

import jsonpickle
import pytest

from service.record import RecordRevisionHistoryService, RecordDoesNotExistError
from tests.service.record.fixtures import dbname, cursor, conn


@pytest.fixture
def service(dbname):
    service = RecordRevisionHistoryService
    service.dbname = dbname
    yield service


def test_create_record(cursor, service):
    data = {"name": "Anna"}
    service.create_record(data)

    record = cursor.execute("SELECT * FROM versioned_records").fetchone()

    assert jsonpickle.decode(record["data"]) == data
    assert record["version"] == 1


def test_get_latest_record_version(cursor, service):
    data = {"name": "Anna", "species": "human"}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()

    record = service.get_record(last_inserted["id"])

    assert record["data"] == data
    assert record["version"] == 1


def test_get_raises(cursor, service):
    with pytest.raises(RecordDoesNotExistError):
        service.get_record(1)


def test_get_raises_with_version(cursor, service):
    data = {"name": "Anna", "species": "human"}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()

    with pytest.raises(RecordDoesNotExistError):
        service.get_record(last_inserted["id"], 4)


def test_update_record(cursor, service):
    data = {"name": "Anna"}
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()
    old_version = service.get_record(last_inserted["id"])
    service.update_record(old_version, data_v2)

    historical = cursor.execute(
        "SELECT * FROM history WHERE records_id = ?", (last_inserted["id"],)
    ).fetchone()
    updated = cursor.execute(
        "SELECT * FROM versioned_records WHERE id = ?", (last_inserted["id"],)
    ).fetchone()

    assert historical["version"] == 1
    assert updated["version"] == 2


def test_update_with_deletions(cursor, service):
    data = {"name": "Anna", "species": "human"}
    data_v2 = {"name": "AnnaBNana", "species": None}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()
    old_version = service.get_record(last_inserted["id"])
    service.update_record(old_version, data_v2)

    historical = cursor.execute(
        "SELECT * FROM history WHERE records_id = ?", (last_inserted["id"],)
    ).fetchone()
    updated = cursor.execute(
        "SELECT * FROM versioned_records WHERE id = ?", (last_inserted["id"],)
    ).fetchone()

    assert historical["version"] == 1
    assert jsonpickle.decode(historical["data"]) == data
    assert updated["version"] == 2
    assert jsonpickle.decode(updated["data"]) == {"name": "AnnaBNana"}


def test_get_new_version(cursor, service):
    data = {"name": "Anna"}
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()
    old_version = service.get_record(last_inserted["id"])
    service.update_record(old_version, data_v2)

    record = service.get_record(last_inserted["id"], 2)

    assert record["version"] == 2
    assert record["data"] == data_v2


def test_get_old_version(cursor, service):
    data = {"name": "Anna"}
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()
    old_version = service.get_record(last_inserted["id"])
    service.update_record(old_version, data_v2)

    record = service.get_record(last_inserted["id"], 1)

    assert record["version"] == 1
    assert record["data"] == data
    assert record["records_id"] == 1


def test_get_latest_version(cursor, service):
    data = {"name": "Anna"}
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()
    old_version = service.get_record(last_inserted["id"])
    service.update_record(old_version, data_v2)

    record = service.get_record(last_inserted["id"], "latest")

    assert record["version"] == 2
    assert record["data"] == data_v2


def test_get_versions(cursor, service):
    data = {"name": "Anna"}
    data_v2 = {"name": "Anna", "species": "human"}
    service.create_record(data)
    last_inserted = cursor.execute("SELECT * FROM versioned_records").fetchone()
    old_version = service.get_record(last_inserted["id"])
    service.update_record(old_version, data_v2)

    versions = service.get_versions(old_version["id"])

    assert versions == [1, 2]
