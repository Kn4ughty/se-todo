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
    return jsonify({"token": token.token, "expires": token.token_expiry_time}), 200


@app.post("/tokenValid")
def is_token_valid():
    error = jsonify(0), 400

    headers = request.headers
    bearer = headers.get("Authorization")
    if type(bearer) is not str:
        return jsonify("error")
    token = bearer.split()[1]  # YourTokenHere

    user = db.get_user_from_token(token)

    if type(user) is not User:
        return error
    if type(user.token) is not Token:
        return error

    b = Token.is_token_valid(user.token.token_expiry_time)

    return jsonify(1 * b), 200


@app.post("/refreshToken")
@token_auth.login_required
def refresh_token():
    raise NotImplementedError

    u = token_auth.current_user()
    if type(u) is not User:
        raise Exception

    t = u.get_token()

    return jsonify(t)


@app.post("/signup")
def add_user():
    username = request.form["username"].lower()
    password = request.form["password"]

    log.info(f"User being added via /signup. username: {username}")

    if not username.isalpha():
        return jsonify("Non alpha username"), 400
    if len(username) <= 3:
        return jsonify("Username too short"), 400

    if len(username) >= 255:
        log.info(f"Username input was longer than 255 characters: {username}")
        return jsonify("Username must be shorter than 255 characters"), 400

    if len(password) <= 3:
        return jsonify("Password too short"), 400

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)

    u = User(username, password_hash)

    if type(u) is not User:
        return Response(str(u), status=400)

    db.add_user(u)
    token = u.create_token()
    return jsonify({"token": token.token}), 200
