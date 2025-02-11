from loguru import logger
from flask import Flask, Response

app = Flask(__name__)

from server import auth, database  # noqa: E402


@app.route("/")
def index():
    with open("src/web/index.html") as file:
        data = file.read()

    return data


@app.get("/index.css")
def index_css():
    with open("src/web/index.css") as file:
        data = file.read()
    return Response(data, mimetype="text/css")
