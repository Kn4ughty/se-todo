from flask import request

# This is a circular import. However, flask offically reccomends it
# https://flask.palletsprojects.com/en/stable/patterns/packages/
from main import app


@app.get("/login")
def login_get():
    with open("src/web/login/login.html") as file:
        d = file.read()

    return d


@app.post("/login")
def login_post():
    s = f"u: {request.form['username']} \n p: {request.form['password']}"
    return s
