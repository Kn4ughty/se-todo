import bcrypt
from flask import request

# This is a circular import. However, flask offically reccomends it
# https://flask.palletsprojects.com/en/stable/patterns/packages/
from main import app
import server.database as database

# Bcrypt guide
# https://www.geeksforgeeks.org/hashing-passwords-in-python-with-bcrypt/


print(database.get_users())


@app.get("/login")
def login_get():
    with open("src/web/login/login.html") as file:
        d = file.read()

    return d


@app.post("/login")
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    return username + " " + password
