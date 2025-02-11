from loguru import logger
from flask import Flask, send_file

app = Flask(__name__)

from server import auth, database  # noqa: E402


@app.route("/")
def index():
    return send_file("web/index.html")


@app.get("/index.css")
def index_css():
    return send_file("web/index.css", mimetype="text/css")


@app.get("/snow.JPEG")
def snow():
    return send_file("web/snow.JPEG", mimetype="image/jpeg")
