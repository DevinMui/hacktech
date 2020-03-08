from flask import Flask, render_template, url_for, request, session, redirect, jsonify
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


app = Flask(__name__)


atlas = Atlas(
    url
    # "mongodb+srv://"
    # + name
    # + ":"
    # + password
    # + "1234>@cluster0-u93bv.azure.mongodb.net/test?retryWrites=true&w=majority"
)


@app.route("/")
def index():
    return "hello"


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
    data = request.get_json()
    email = data["email"]
    user = atlas.getUser(email)
    if not user:
        return jsonify({"error": "error"})
    return jsonify(user)


@app.route("/user", methods=["GET"])
def user():
    reqData = request.get_json()
    return atlas.getUser(reqData["email"])


@app.route("/order", methods=["GET"])
def order():
    reqData = request.get_json()
    return atlas.getOrder(reqData["_id"])


@app.route("/queue", methods=["GET"])
def queue():
    reqData = request.get_json()
    return atlas.getQueue(reqData["_id"])


# takes order information in json format
@app.route("/enqueue_order", methods=["POST"])
def enqueue_order():
    reqData = request.get_json()
    return atlas.enqueue(reqData["_id"], reqData["order"])


# dequeues order information in json format
@app.route("/dequeue_order", methods=["POST", "GET"])
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
