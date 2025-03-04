import sqlite3
from loguru import logger as log
from typing import List
from pathlib import Path
import os
from flask import g, jsonify

from server.types import User, Token
from main import app

# This guide is good
# https://www.geeksforgeeks.org/python-sqlite/
data_dir_name = "naught"
app_dir = "todo"
local_share = Path("~/.local/share/").expanduser()
self_data_dir = os.path.join(local_share, data_dir_name)
full_data_dir = os.path.join(self_data_dir, app_dir)


def setup_data_directory():
    log.debug(f"local share dir expanded to {local_share}")

    log.debug(f"Full app data dir = {full_data_dir}")

    if os.path.exists(full_data_dir):
        log.info(f"Full data dir directory already found. {full_data_dir}")
        return

    log.info(f"Full Data dir was not found. = {full_data_dir}")

    if os.path.exists(self_data_dir):
        log.info(
            f"Naught data dir was found! \
            Creating app specfic dir. = {self_data_dir}"
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
    exit()


setup_data_directory()

db_file_location = Path(full_data_dir + "/db.sqlite3")
log.info(f"Db location set at {db_file_location}")


def get_db() -> sqlite3.Connection:
    log.debug("Database is being gotten")
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(db_file_location)
    return db


# This automatically closes the db connection at the end of the request
# Its kinda weird https://flask.palletsprojects.com/en/stable/patterns/sqlite3/
@app.teardown_appcontext
def teardown_db(exception):
    log.debug("Automatically closing/teardown the db")
    if exception is not None:
        log.debug(f"Teardown_appcontext exception: {exception}")

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
        log.debug(f"Existing tables found, {list_of_tables}")

        if "USERS" not in list_of_tables:
            log.debug("USERS not found in table list")
            cur.execute("""
            CREATE TABLE USERS (
                username VARCHAR(255) NOT NULL UNIQUE,
                password CHAR(60) NOT NULL,
                PRIMARY KEY (username)
            ) """)
            con.commit()

        if "TOKENS" not in list_of_tables:
            log.debug("TOKENS not found in table list")
            cur.execute("""
            CREATE TABLE TOKENS (
                username VARCHAR(255) NOT NULL,
                token CHAR(16) NOT NULL UNIQUE,
                expire_time FLOAT NOT NULL
            )
            """)

        if "TASKS" not in list_of_tables:
            log.debug("TASKS not found in table list")
            # uuid len comes from "len(uuid.uuid4().hex) == 32"
            cur.execute("""
            CREATE TABLE TASKS (
                uuid CHAR(32) NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL,
                text VARCHAR(255) NOT NULL,
                status BOOL NOT NULL,
                item_order INT,
                PRIMARY KEY (uuid)
            )
            """)


init_database()


def get_all_users() -> List[User]:
    log.debug("Get_all_users function being run")
    cur = get_db().cursor()
    cur.execute("""
    SELECT * FROM USERS
    """)
    raw_list = cur.fetchall()
    log.info(f"data recived from db for user list, {raw_list}")
    # Recieves an List of tupels.

    user_list = []
    for user in raw_list:
        user_list.append(User(user[0], bytes(user[1])))

    log.debug(f"Processed list of all users found in DB: {user_list}")

    return user_list


def get_user(username: str) -> User | None:
    cur = get_db().cursor()
    cur.execute(
        """
    SELECT * FROM USERS WHERE username=?
    """,
        [username],
    )
    data = cur.fetchall()

    if len(data) > 1:
        log.error(
            f"There are multiple users with the same name in the database.\
            data recived: {data} "
        )
        raise Exception
    if len(data) == 0:
        log.debug(f"No user by name {username} was found")
        return None

    u = data[0]

    log.info(f"GET USER {username} RETURNED {data}")
    return User(u[0], bytes(u[1]))


def add_user(u: User) -> None | tuple:
    log.info(f"Adding user to db. u: {u}")

    con = get_db()
    cur = con.cursor()

    if get_user(u.username) is not None:
        log.error("Tried creating user with username that already exists")
        return jsonify("User with that name already exists"), 400

    cur.execute(
        """
    INSERT INTO USERS VALUES (?, ?)
    """,
        [u.username, u.password],
    )
    con.commit()
    return


def add_token(u: User) -> None:
    log.info(f"Adding user token to db. u: {u}")

    if not u.token:
        log.error(
            f"Add token db method was given user without Token set\n\
        User: {u}"
        )
        raise Exception

    if u.token.token_expiry_time is None:
        log.error(f"BROKEN TOKEN DETECTED. user: {u}")
        raise Exception

    con = get_db()
    cur = con.cursor()

    cur.execute(
        """
    INSERT INTO TOKENS VALUES (?, ?, ?)
    """,
        [u.username, u.token.token, u.token.token_expiry_time],
    )
    con.commit()


def get_user_from_token(token: str) -> None | User:
    log.info(f"Getting user from token: {token}")
    # Check if token exista.token
    con = get_db()
    cur = con.cursor()
    cur.execute(
        """
    SELECT * FROM TOKENS WHERE token=?
    """,
        [token],
    )
    result = cur.fetchall()

    if len(result) != 1:
        if len(result) > 1:
            log.error(f"Duplicicate token found. {token}")
            raise Exception
        return None

    # If it exists, check expiry and delete accordingly
    item = result[0]
    username = item[0]
    db_token = item[1]
    token_expiry_time = item[2]

    if not Token.is_token_valid(token_expiry_time=token_expiry_time):
        revoke_token(Token(token, token_expiry_time))
        return None

    # Then get the user for that token.
    user = get_user(username)
    if user is None:
        log.error(
            f"Token found with username that doesnt exist. \
        username:{username}. Token:{token}"
        )
        raise Exception
    user.token = Token(db_token, token_expiry_time)

    return user


def get_token_from_user(u: User) -> None | Token:
    log.debug(f"Getting token from user: {u}")
    # Check if token exists
    con = get_db()
    cur = con.cursor()
    cur.execute(
        """
    SELECT token, expire_time FROM TOKENS WHERE username=?
    """,
        [u.username],
    )
    result = cur.fetchall()

    if len(result) != 1:
        if len(result) > 1:
            log.error(f"Mutliple tokens for username found. user: {u}")
            raise Exception
        return None

    return Token(result[0][0], result[0][1])


def revoke_token(token: Token):
    log.debug(f"Revoking token: {token}")
    con = get_db()
    cur = con.cursor()
    log.info(f"Revoking token {token}")
    cur.execute(
        """
    DELETE FROM TOKENS WHERE token == ?
    """,
        [token.token],
    )
    con.commit()
