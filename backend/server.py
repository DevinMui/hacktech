from flask import (
    Flask,
    render_template,
    url_for,
    request,
    session,
    redirect,
    jsonify,
    Response,
    make_response,
)
from db import *

from api import API

import json


api = None
name = ""
password = ""

with open("config.json") as json_data_file:
    data = json.load(json_data_file)
    name = data["db"]["user"]
    password = data["db"]["passwd"]
    url = data["db"]["url"]
    api = API(
        data["ebay"]["appId"],
        data["ebay"]["certId"],
        data["ebay"]["redirectName"],
        data["ebay"]["scope"],
        "SANDBOX",
    )


def with_cors(response):
    if type(response) != Response:
        response = jsonify(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


app = Flask(__name__)

atlas = Atlas(url)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    return response


@app.route("/")
def index():
    response = jsonify({"email": "email"})
    return redirect(url_for("static", filename="./template/index.html"))


@app.route("/oauth", methods=["GET"])
def oauth():
    code = request.args.get("code")
    token = api.getUserAccessToken(code)
    ebayUser = api.getUser(token)
    # check user email against db
    # return user or register
    user = atlas.getUser(ebayUser["individualAccount"]["email"])
    if not user:
        return jsonify(register(ebayUser))

    return jsonify(user)


def register(ebayUser):
    email = ebayUser["individualAccount"]["email"]
    name = (
        ebayUser["individualAccount"]["firstName"]
        + " "
        + ebayUser["individualAccount"]["lastName"]
    )
    data = {"email": email, "name": name}
    return atlas.createUser(data)


# store _id
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data["email"]
    user = atlas.getUser(email)

    if not user:
        return jsonify({"error": "error"})
    return jsonify(user)


@app.route("/user", methods=["POST"])
def user():
    reqData = request.get_json()
    return atlas.getUser(reqData["email"])


@app.route("/order", methods=["POST"])
def order():
    reqData = request.get_json()
    return atlas.getOrder(reqData["_id"])


@app.route("/queue", methods=["POST"])
def queue():
    reqData = request.get_json()
    return atlas.getQueue(reqData["_id"])


@app.route("/start_queue", methods=["POST"])
def startQueue():
    data = request.get_json()
    return atlas.startQueue(data["_id"])


@app.route("/stop_queue", methods=["POST"])
def stopQueue():
    data = request.get_json()
    return atlas.stopQueue(data["_id"])


# takes order information in json format
@app.route("/enqueue_order", methods=["POST"])
def enqueue_order():
    reqData = request.get_json()
    return atlas.enqueue(reqData["_id"], reqData["order"])


# dequeues order information in json format
@app.route("/dequeue_order", methods=["POST"])
def dequeue_order():
    reqData = request.get_json()
    return atlas.dequeue(reqData["_id"])


@app.route("/create_queue", methods=["POST"])
def create_queue():
    reqData = request.get_json()
    return atlas.createQueue(reqData["_id"], reqData["data"])


@app.route("/update_order", methods=["POST"])
def update_order():
    reqData = request.get_json()
    return atlas.updateOrder(reqData["_id"], reqData["data"])


if __name__ == "__main__":
    app.secret_key = "secret"
    app.run(debug=True)
