from loguru import logger as log
import flask
from flask import Flask
import os

STATIC_DIR = os.path.join(os.path.dirname(__file__), "web")

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    static_url_path=None,
)

# This import is below app = Flask so that modules can access the app var
# Circular import moment :P
# https://flask.palletsprojects.com/en/stable/patterns/packages/
from server import auth, database, tasks  # noqa


# When requesting something from /, go to the static dir and serve that
@app.route("/<path:filename>")
def serve_all_static_files(filename):
    log.info(f"getting static file: {filename}")
    return flask.send_from_directory(STATIC_DIR, filename)


@app.route("/")
def serve_index():
    log.info("Getting index.html from /")
    return flask.send_from_directory(STATIC_DIR, "index.html")


@app.route("/serviceWorker.js")
def serve_serviceWorker():
    log.info("Getting service worker.")
    return flask.send_from_directory(
        STATIC_DIR, "serviceWorker.js", mimetype="application/javascript"
    )
