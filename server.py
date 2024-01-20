from flask import Flask, request, jsonify   # import flask

app = Flask(__name__)             # create an app instance

@app.route("/")
def index():
    return "App is running", 200
