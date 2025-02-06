from flask import Flask

app = Flask(__name__)

from server import auth  # noqa: E402


@app.route("/")
def index():
    with open("src/web/index.html") as file:
        data = file.read()

    return data
