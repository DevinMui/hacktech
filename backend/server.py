from flask import Flask, render_template, url_for, request, session, redirect

from db import *
import json


name = ""
password = ""
with open("config.json") as json_data_file:
    data = json.load(json_data_file)
    name = data["db"]["user"]
    password = data["db"]["passwd"]


app = Flask(__name__)


atlas = Atlas(
    "mongodb+srv://"+name+":"+password+"1234>@cluster0-u93bv.azure.mongodb.net/test?retryWrites=true&w=majority")

# HTTP REQUEST CODE TO IMPLEMENT:


@app.route("/")
def index():
    if "email" in session:
        return "You are logged in as " + session["email"]
    return "Please login"


# takes login information in json format and checks if user exists in db
@app.route("/login", methods=["POST"])
def login():
    reqData = request.get_json()
    loginUser = atlas.getUser(reqData["_id"])
    if loginUser:
        if reqData["password"] == loginUser["password"]:
            session["email"] = reqData["email"]
            return redirect(url_for("index"))
    raise BadDataException("Invalid email/password combination")


# takes register data and creates a user document in db cluster of the user's info
@app.route("/register", methods=["POST"])
def register():
    reqData = request.get_json()
    session["email"] = reqData["email"]
    return atlas.createUser(reqData)


@app.route("/user", methods=["GET"])
def user():
    reqData = request.get_json()
    return atlas.getUser(reqData["_id"])


@app.route("/order", methods=["GET"])
def order():
    reqData = request.get_json()
    return atlas.getOrder(reqData['_id'])


@app.route("/queue", methods=["GET"])
def queue():
    reqData = request.get_json()
    return atlas.getQueue(reqData['_id'])

# takes order information in json format
@app.route("/enqueue_order", methods=["POST"])
def enqueue_order():
    reqData = request.get_json()
    atlas.enqueue(reqData['_id'], reqData['order'])

# dequeues order information in json format
@app.route("/dequeue_order", methods=["POST", "GET"])
def dequeue_order():
    reqData = request.get_json()
    return atlas.dequeue(reqData['_id'])


@app.route("/create_queue", methods=["POST"])
def create_queue():
    reqData = request.get_json()
    atlas.createQueue(reqData['_id'], reqData['data'])


@app.route("/update_order", methods=["POST"])
def update_order():
    reqData = request.get_json()
    atlas.updateOrder(reqData['_id'], reqData['data'])


if __name__ == "__main__":
    app.secret_key = "secret"
    app.run(debug=True)
