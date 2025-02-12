from loguru import logger
import flask
from flask import Flask
import os

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    static_url_path=None,
)

# This import is below app = Flask so that modules can access the app var
# The noqa: tells my lsp to ignore imports being below code
from server import auth, database  # noqa: E402


# When requesting something from /, go to the static dir and serve that
@app.route("/<path:filename>")
def serve_all_static_files(filename):
    return flask.send_from_directory(STATIC_DIR, filename)


@app.route("/")
def serve_index():
    return flask.send_from_directory(STATIC_DIR, "index.html")
