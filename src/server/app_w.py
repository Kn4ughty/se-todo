from loguru import logger as log
from flask import Flask, jsonify, request, Response
import uuid
from werkzeug.exceptions import BadRequestKeyError

from main import app

import server.database as db
from server.auth import token_auth
from server.types import User, Token


# TODO. Perhapse inline this into add_task()
def add_task_to_db(username: str, text: str, status: bool = False) -> None:
    with app.app_context():
        con = db.get_db()
        cur = con.cursor()

        u = uuid.uuid4().hex
        log.info(f"Task being added to db. username: {username}. uuid: {u}")

        cur.execute(
            """
            INSERT INTO TASKS VALUES (?, ?, ?, ?)
        """,
            [u, username, text, status],
        )
        con.commit()


def get_username_from_uuid(uuid: str) -> str:
    con = db.get_db()
    cur = con.cursor()

    cur.execute(
        """
    SELECT username FROM TASKS WHERE uuid = ?
    """,
        [uuid],
    )

    return cur.fetchone()[0]


@app.post("/tasks")
@token_auth.login_required
def add_task():
    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception
    username = u.username
    text = request.form["text"]
    try:
        status = bool(request.form["status"])
        add_task_to_db(username, text, status)
    except BadRequestKeyError:
        add_task_to_db(username, text)

    return jsonify(), 200


@app.get("/tasks")
@token_auth.login_required
def get_all_tasks():
    con = db.get_db()
    cur = con.cursor()

    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception

    cur.execute(
        """
    SELECT * FROM TASKS WHERE username = ?
    """,
        [u.username],
    )
    results = cur.fetchall()

    a = []
    for task in results:
        d = {}
        d["uuid"] = task[0]
        # Skip username as its not required
        d["text"] = task[2]
        d["status"] = task[3]
        a.append(d)

    return jsonify(a)


@app.post("/updateTaskText")
@token_auth.login_required
def update_task_text():
    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception

    new_text = request.form["text"]
    id = request.form["uuid"]

    if get_username_from_uuid(id) != u.username:
        return jsonify(f"we think u stole this task uuid. NO perms for you"), 401

    con = db.get_db()
    cur = con.cursor()
    cur.execute(
        """
    UPDATE TASKS
    SET text = ?
    WHERE uuid = ?
    """,
        [new_text, id],
    )
    con.commit()

    return jsonify("woah"), 200


@app.post("/updateTaskStatus")
@token_auth.login_required
def update_task_status():
    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception

    raw_stat = request.form["status"]
    # new_status = 0
    if raw_stat == 0 or raw_stat.lower() == "false":
        new_status = 0
    elif raw_stat == 1 or raw_stat.lower() == "true":
        new_status = 1
    else:
        return jsonify("bad status value"), 400

    id = request.form["uuid"]

    if get_username_from_uuid(id) != u.username:
        return jsonify("You stole this task uuid. NO perms for you"), 401

    con = db.get_db()
    cur = con.cursor()
    cur.execute(
        """
    UPDATE TASKS
    SET status = ?
    WHERE uuid = ?
    """,
        [new_status, id],
    )
    con.commit()

    return jsonify("woah"), 200
