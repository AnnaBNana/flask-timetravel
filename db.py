import sqlite3


create_table = """ CREATE TABLE IF NOT EXISTS Records (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               data TEXT NOT NULL
               );"""

def initialize_db() -> None:
    db_connection = sqlite3.connect('record-service.db')
    cursor = db_connection.cursor()
    cursor.execute(create_table)
    db_connection.close()
