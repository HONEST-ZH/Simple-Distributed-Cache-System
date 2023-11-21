import flask
from markupsafe import escape
sever = flask.Flask(__name__)
@sever.route("/")
def hello_world():
    return "<p>Hello, World!</p>"