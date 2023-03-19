import pathlib
import sqlite3

import pytest

from db import versioned_records_sql, revisions_sql, records_sql


@pytest.fixture
def dbname():
    yield "test.db"


@pytest.fixture
def conn(dbname):
    yield sqlite3.connect(dbname)
    pathlib.Path.unlink(dbname)


@pytest.fixture
def cursor(conn):
    with conn as c:
        c.row_factory = sqlite3.Row
        cursor = c.cursor()
        cursor.execute(records_sql)
        cursor.execute(versioned_records_sql)
        cursor.execute(revisions_sql)
        yield cursor