import logging as log
from flask import Flask


app = Flask(__name__)

from server import auth  # noqa: E402

# log.basicConfig(level=log.DEBUG)
log.basicConfig(
    level=log.INFO,
    format="{asctime}-{levelname}: {message}",
    style="{",
    datefmt="%H:%M:%S",
)


@app.route("/")
def index():
    with open("src/web/index.html") as file:
        data = file.read()

    return data
