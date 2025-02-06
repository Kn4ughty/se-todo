# This is a circular import. However, flask offically reccomends it
# https://flask.palletsprojects.com/en/stable/patterns/packages/
from main import app


@app.route("/login")
def login_page():
    with open("src/web/login/login.html") as file:
        d = file.read()

    return d
