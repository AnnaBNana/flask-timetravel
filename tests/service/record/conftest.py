import pathlib
import sqlite3
from typing import Generator

import pytest

from db import records_sql, revisions_sql, versioned_records_sql


@pytest.fixture
def dbname() -> Generator[str, None, None]:
    """DB name for test runs."""
    yield "test.db"


@pytest.fixture
def conn(dbname: str) -> Generator[sqlite3.Connection, None, None]:
    """Yield db connection and cleanup db after test run."""
    yield sqlite3.connect(dbname)
    pathlib.Path.unlink(dbname)


@pytest.fixture
def cursor(conn: sqlite3.Connection) -> sqlite3.Cursor:
    """Create tables and yield cursor for active db."""
    with conn as c:
        c.row_factory = sqlite3.Row
        cursor = c.cursor()
        cursor.execute(records_sql)
        cursor.execute(versioned_records_sql)
        cursor.execute(revisions_sql)
        yield cursor
