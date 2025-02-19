from loguru import logger as log
from flask import Flask, jsonify, request
import uuid
from werkzeug.exceptions import BadRequestKeyError

from main import app

import server.database as db
from server.auth import token_auth
from server.types import User, Token

# TODO. Maybe turn tasks into a class?


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
