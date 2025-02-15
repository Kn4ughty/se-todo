import bcrypt
from flask import request, Response
from flask_httpauth import HTTPBasicAuth
from loguru import logger as log
import json

# This is a circular import. However, flask offically reccomends it
# https://flask.palletsprojects.com/en/stable/patterns/packages/
from main import app
import server.database as database
from server.types import User

# Bcrypt guide
# https://www.geeksforgeeks.org/hashing-passwords-in-python-with-bcrypt/

basic_auth = HTTPBasicAuth()


@basic_auth.verify_password
def verify_password(username, password):
    user = database.get_user(username)

    pass


@app.post("/login")
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    # Return some sort of auth token?

    return username + " " + password


# TODO VERY IMPORTANT
# REMEMBER TO DELETE THIS. (dont want to leak user credentials)
@app.get("/users")
def get_users():
    log.critical("THE DATABASE IS BEING STOLEN VIA THE BACKDOOR I CODED!!!!!")
    user_list = database.get_all_users()

    user_dict = {}
    for user in user_list:
        user_dict[user.username] = str(user.password)

    return json.dumps(user_dict)


@app.post("/signup")
def add_user():
    username = request.form["username"]
    password = request.form["password"]

    u = create_user_from_raw(username, password)

    if type(u) is str:
        return Response(u, status=400)

    if type(u) is User:
        database.add_user(u)
        return Response(status=200)
    log.error("WTF HAPPENED")
    return Response(status=400)


def create_user_from_raw(username: str, password: str) -> User | str:
    log.info(f"Creating user with username {username}")
    if len(username) >= 255:
        log.info(f"Username input was longer than 255 characters: {username}")
        return "Username must be shorter than 255 characters"

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return User(username, password_hash)
