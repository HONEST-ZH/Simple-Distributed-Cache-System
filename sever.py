import flask
from flask import Flask
sever = Flask(__name__)

@sever.route("/")
def hello_world():
    return "<p>Hello, World!</p>"