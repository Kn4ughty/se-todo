import bcrypt
from flask import request, Response, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from loguru import logger as log
import json

# This is a circular import. However, flask offically reccomends it
# https://flask.palletsprojects.com/en/stable/patterns/packages/
from main import app
import server.database as db
from server.types import User, Token

# Bcrypt guide
# https://www.geeksforgeeks.org/hashing-passwords-in-python-with-bcrypt/

# flask http thing
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxiii-application-programming-interfaces-apis

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.error_handler
def basic_auth_error(status):
    log.error(f"BASIC AUTH ERROR: {status}")
    return jsonify({"error": "Unauthorized", "message": "Invalid credentials"}), 401


@basic_auth.verify_password
def verify_password(username, password) -> User | None:
    log.debug(f"verify_password run for username: {username}")
    user = db.get_user(username)
    if user is None:
        log.info(f"Verify was run with invalid username. {username}")
        return None

    if user.check_passsword(password.encode("utf-8")):
        log.debug(f"verify_password was correct for username {username}")
        return user
    log.info(f"Verify password had incorrect password, {username}")
    return None


@token_auth.error_handler
def token_auth_error(status):
    log.error(f"TOKEN AUTH ERROR: {status}")
    return jsonify({"error": "Unauthorized", "message": "Invalid credentials"}), 401


@token_auth.verify_token
def verify_token(token: str):
    log.info(f"Verifying token {token}")
    return db.get_user_from_token(token)


@app.post("/tokens")
@basic_auth.login_required
def get_token():
    u = token_auth.current_user()
    log.debug(f"Getting token for user: {u}")
    if type(u) is not User:
        return "ERROR", 400
    token = u.get_token()
    return jsonify({"token": token.token}), 200


@app.post("/tokenValid")
@token_auth.login_required
def refresh_token():
    u = token_auth.current_user()
    if type(u) is not User:
        log.error(f"current_user was not a User. u:{u}")
        return "ERROR", 400
    token = u.get_token()

    Token.is_token_valid(token.token_expiry_time)

    return jsonify(Token.is_token_valid(token.token_expiry_time))


# TODO VERY IMPORTANT
# REMEMBER TO DELETE THIS. (dont want to leak user credentials)


@app.get("/users")
def get_users():
    log.critical("THE DATABASE IS BEING STOLEN VIA THE BACKDOOR I CODED!!!!!")
    user_list = db.get_all_users()

    user_dict = {}
    for user in user_list:
        user_dict[user.username] = str(user.password)

    return json.dumps(user_dict)


@app.post("/signup")
def add_user():
    username = request.form["username"]
    password = request.form["password"]

    log.info(f"User being added via /signup. username: {username}")
    u = create_user_from_raw(username, password)

    if type(u) is not User:
        return Response(str(u), status=400)

    db.add_user(u)
    return Response(status=200)


def create_user_from_raw(username: str, password: str) -> User | str:
    log.info(f"Creating user with username {username}")
    if len(username) >= 255:
        log.info(f"Username input was longer than 255 characters: {username}")
        return "Username must be shorter than 255 characters"

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return User(username, password_hash)
