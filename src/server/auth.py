import bcrypt
from flask import request, send_file
from loguru import logger as log

# This is a circular import. However, flask offically reccomends it
# https://flask.palletsprojects.com/en/stable/patterns/packages/
from main import app
import server.database as database
from server.types import User

# Bcrypt guide
# https://www.geeksforgeeks.org/hashing-passwords-in-python-with-bcrypt/


@app.get("/login")
def login_get():
    return send_file("web/login/login.html")


@app.post("/login")
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    return username + " " + password


@app.get("/users")
def get_users():
    return database.get_all_users()


def create_user_from_raw(username: str, password: str) -> User | str:
    if len(username) >= 255:
        log.info(f"Username input was longer than 255 characters: {username}")
        return "Username must be shorter than 255 characters"

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return User(username, password_hash)
