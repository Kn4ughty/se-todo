from loguru import logger as log
import flask
from flask import Flask, jsonify, request, Response
import uuid
from werkzeug.exceptions import BadRequestKeyError

from main import app

import server.database as db
from server.auth import token_auth
from server.types import User, Token


# TODO. Perhapse inline this into add_task()
def add_task_to_db(username: str, text: str, status: bool = False) -> str:
    with app.app_context():
        con = db.get_db()
        cur = con.cursor()

        u = uuid.uuid4().hex
        log.info(f"Task being added to db. username: {username}. uuid: {u}")

        cur.execute(
            """
            INSERT INTO TASKS VALUES (?, ?, ?, ?, ?)
        """,
            [u, username, text, status, None],
        )
        con.commit()

        return u


def get_username_from_uuid(uuid: str) -> str:
    con = db.get_db()
    cur = con.cursor()

    cur.execute(
        """
    SELECT username FROM TASKS WHERE uuid = ?
    """,
        [uuid],
    )
    result = cur.fetchone()

    return result[0]


@app.post("/tasks")
@token_auth.login_required
def add_task():
    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception
    username = u.username
    log.info(f"Recived data from /tasks POST: {request.form}")
    text = request.form["text"]
    try:
        status = bool(request.form["status"])
        uid = add_task_to_db(username, text, status)
    except BadRequestKeyError:
        uid = add_task_to_db(username, text)

    return jsonify(uid), 200


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
        t = flask.render_template_string("{{t}}", t=task[2])
        log.error(f"Sanitised text, {t}")
        d["text"] = t
        d["status"] = task[3]
        d["order"] = task[4]
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
        return jsonify("we think u stole this task uuid"), 401

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
    id = request.form["uuid"]

    if raw_stat == 0 or raw_stat.lower() == "false":
        new_status = 0
    elif raw_stat == 1 or raw_stat.lower() == "true":
        new_status = 1
    else:
        return jsonify("bad status value"), 400

    if get_username_from_uuid(id) != u.username:
        return jsonify("we think u stole this task uuid"), 401

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


@app.delete("/tasks")
@token_auth.login_required
def delete_task():
    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception

    id = request.form["uuid"]
    if get_username_from_uuid(id) != u.username:
        return jsonify("we think u stole this task uuid"), 401

    log.info(f"Deleting task with id {id}")
    con = db.get_db()
    cur = con.cursor()

    cur.execute(
        """
    DELETE FROM TASKS WHERE uuid = ?
    """,
        [id],
    )
    con.commit()

    return jsonify(), 200


@app.post("/taskOrder")
@token_auth.login_required
def change_task_order():
    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception

    new_order = int(request.form["order"])
    uuid = request.form["uuid"]

    if get_username_from_uuid(uuid) != u.username:
        return jsonify("we think u stole this task uuid"), 401

    con = db.get_db()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE TASKS
        SET item_order = (?)
        WHERE uuid = (?)
    """,
        [new_order, uuid],
    )
    con.commit()

    return jsonify(), 200
