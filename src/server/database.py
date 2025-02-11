import sqlite3
from loguru import logger as log
from typing import List
from pathlib import Path
import os
from flask import g

from server.types import User
from main import app

# This guide is good
# https://www.geeksforgeeks.org/python-sqlite/


def setup_data_directory():
    data_dir_name = "naught"
    app_dir = "todo"
    local_share = Path("~/.local/share/").expanduser()
    log.debug(f"local share dir expanded to {local_share}")

    self_data_dir = os.path.join(local_share, data_dir_name)
    full_data_dir = os.path.join(self_data_dir, app_dir)
    log.debug(f"Full app data dir = {full_data_dir}")

    if os.path.exists(full_data_dir):
        log.info(f"Full data dir directory already found. {full_data_dir}")
        return

    log.info(f"Full Data dir was not found. = {full_data_dir}")

    if os.path.exists(self_data_dir):
        log.info(
            f"Naught data dir was found! Creating app specfic dir. = {
                self_data_dir}"
        )
        os.mkdir(full_data_dir)
        return

    if os.path.exists(local_share):
        log.info("Naught dir was not found, Creating folder now.")
        os.mkdir(self_data_dir)
        return

    log.error(
        f"{local_share} directory was not found. This is strange.\
    Make the directory manually to continue"
    )


setup_data_directory()

# this should be based on all the fancy path planning used in the above func
db_file_location = Path("~/.local/share/naught/todo/db.sqlite3").expanduser()
# conn = sqlite3.connect(db_file_location)
# cur = conn.cursor()


def get_db() -> sqlite3.Connection:
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(db_file_location)
    return db


@app.teardown_appcontext
def close_connection(exception):
    log.error(f"Teardown_appcontext error {exception}")
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_database():
    with app.app_context():
        con = get_db()
        cur = con.cursor()

        list_of_tables = cur.execute(
            """SELECT name FROM sqlite_master WHERE type='table'"""
        )
        list_of_tables = [row[0] for row in cur.fetchall()]

        if "USERS" not in list_of_tables:
            cur.execute(""" CREATE TABLE USERS (
                    username VARCHAR(255) NOT NULL,
                    password CHAR(60) NOT NULL
                ); """)
            con.commit()


init_database()


def get_all_users() -> List[User]:
    cur = get_db().cursor()
    cur.execute("""
    SELECT * FROM USERS
    """)

    raw_list_of_users = [row for row in cur.fetchall()]
    log.debug(f"List of all users found in DB: {raw_list_of_users}")

    return raw_list_of_users


# get_all_users()


def add_user(u: User) -> None:
    con = get_db()
    cur = con.cursor()
    cur.execute(
        """
    INSERT INTO USERS VALUES ('?', '?')
    """,
        (u.username, u.password),
    )
    con.commit()
    return


# add_user(conn, cur, au)
