import sqlite3
import logging as log
from typing import List
from pathlib import Path
import os

from server.types import User

# This guide is good
# https://www.geeksforgeeks.org/python-sqlite/


local_share = Path("~/.local/share/").expanduser()
data_dir_name = "naught"

db_file_location = Path("~/.local/share/naught/todo/db.sqlite3")


def setup_data_directory():
    if not os.path.exists(local_share):
        # ERROR
        log.error(
            f"{local_share} folder does not exist? This is strange. \
            Not attempting to recover from this error, fix it manually"
        )
        raise FileExistsError

    if not os.path.exists(os.path.join(local_share, data_dir_name)):
        log.info(f"Creating {data_dir_name} folder in {local_share}")
        os.mkdir(os.path.join(local_share, data_dir_name))


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
