from flask import Flask, render_template, url_for, request, session, redirect

from db_queries import *
import json


app = Flask(__name__)


# HTTP REQUEST CODE TO IMPLEMENT:


@app.route("/")
def index():
    if "username" in session:
        return "You are logged in as " + session["username"]
    return "Please login"


# takes login information in json format and checks if user exists in db, can use either username or email
@app.route("/login", methods=["POST"])
def login():
    req_data = request.get_json()
    login_user = getUser(req_data["username"])
    if login_user:
        if req_data["password"] == login_user["password"]:
            session["username"] = req_data["username"]
            return redirect(url_for("index"))

    return "Invalid username/password combination"


# takes register data and creates a user document in db cluster of the user's info
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        req_data = request.get_json()
        session["username"] = req_data["username"]
        return createUser(req_data)
    return "Register Here"


if __name__ == "__main__":
    app.secret_key = "secret"
    app.run(debug=True)
