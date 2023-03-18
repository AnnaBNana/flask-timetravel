import sqlite3


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


revisions_sql = """CREATE TABLE IF NOT EXISTS revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                records_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                timestamp DATETIME,
                data TEXT NOT NULL,
                FOREIGN KEY (records_id) REFERENCES records(id)
                );"""


def initialize_db() -> None:
    db_connection = sqlite3.connect("record-service.db")
    cursor = db_connection.cursor()
    cursor.execute(records_sql)
    cursor.execute(versioned_records_sql)
    cursor.execute(revisions_sql)
    db_connection.close()
