import sqlite3

db_name = "record-service.db"

records_sql = """ CREATE TABLE IF NOT EXISTS records (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               data TEXT NOT NULL,
               created_at DATETIME,
               updated_at DATETIME
               );"""


versioned_records_sql = """CREATE TABLE IF NOT EXISTS versioned_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at DATETIME
                    );"""


revisions_sql = """CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                records_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                timestamp DATETIME,
                data TEXT NOT NULL,
                FOREIGN KEY (records_id) REFERENCES records(id)
                );"""


def initialize_db() -> None:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(records_sql)
        cursor.execute(versioned_records_sql)
        cursor.execute(revisions_sql)
