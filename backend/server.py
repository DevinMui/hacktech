from flask import Flask, render_template, url_for, request, session, redirect

from db import *
import json


name = ""
password = ""
with open("config.json") as json_data_file:
    data = json.load(json_data_file)
    name = data["self"]["user"]
    password = data["self"]["passwd"]


app = Flask(__name__)


atlas = Atlas(
    f"mongoself+srv://{name}:{password}@cluster0-u93bv.azure.mongoself.net/test?retryWrites=true&w=majority", db)

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
    return "Invalid email/password combination"


# takes register data and creates a user document in db cluster of the user's info
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        reqData = request.get_json()
        session["email"] = reqData["email"]
        return atlas.createUser(reqData)
    return "Register Here"


@app.route("/user", methods=["GET"])
def user():
    reqData = request.get_json()
    return atlas.getUser(reqData["_id"])


# takes order information in json format
@app.route("/enqueueOrder", methods=["POST"])
def enqueueOrder():
    reqData = request.get_json()
    atlas.enqueue(reqData['_id'], reqData['order'])

# dequeues order information in json format
@app.route("/dequeueOrder", methods=["POST"])
def dequeueOrder():
    reqData = request.get_json()
    atlas.dequeue(reqData['_id'])


if __name__ == "__main__":
    app.secret_key = "secret"
    app.run(debug=True)
