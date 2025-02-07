import sqlite3
from typing import List
from pathlib import Path

from server.types import User

# This guide is good
# https://www.geeksforgeeks.org/python-sqlite/

db_file_location = Path("~/.local/share/naught/todo/db.sqlite3")

sql_connection = sqlite3.connect(db_file_location)
cur = sql_connection.cursor()


def init_database():
    list_of_tables = cur.execute(
        """SELECT tableName FROM sqlite_master WHERE type='table'"""
    ).fetchall()

    if "USERS" not in list_of_tables:
        cur.execute(""" CREATE TABLE USERS (
                username VARCHAR(255) NOT NULL,
                password CHAR(60) NOT NULL,
            ); """)


init_database()


def get_users() -> List[User]:
    return []
