from pymongo import MongoClient
from bson.objectid import ObjectId
import json


class BadDataException(Exception):
    pass


class Atlas:
    def __init__(self, url: str):
        self.client = MongoClient(url)
        self.db = self.client.ebayBidQueue
        self.user = self.db.user
        self.order = self.db.order
        self.queue = self.db.queue

    # creates user from req_data in json format
    def createUser(self, data: dict = None):
        if not data:
            raise BadDataException(" email not provided")
        if not (data["email"]):
            raise BadDataException("email not provided")

        # finds the users with the specified email and name
        if self.user.find_one({"email": data["email"]}):
            raise BadDataException("Email taken")

        # sanitize bad input
        data["queues"] = []
        user = self.user.insert(data)
        user = self.user.find({"_id": user}).next()
        return user

    # prob dont need
    def updateUser(self, _id: str, attributToUpdate, newValue):
        existing_user = self.user.find({"_id": ObjectId(_id)}).next()
        # check if user exists
        if existing_user:
            return self.user.update(
                {"_id": ObjectId(_id)}, {"$set": {attributToUpdate: newValue}}
            )
        else:
            raise BadDataException("error: order does not exist")

    # returns the user document with specified name if user exists
    def getUser(self, email: str):
        existing_user = self.user.find_one({"email": email})
        if not existing_user:
            raise BadDataException("Not Found")
        return existing_user

    # returns the order document with specified id if order exists
    def getOrder(self, _id: str):
        existing_order = self.order.find({"_id": ObjectId(_id)}).next()
        if not existing_order:
            raise BadDataException("Not Found")
        return existing_order

    # returns the queue document with specified id if queue exists
    def getQueue(self, _id: str):
        existing_queue = self.queue.find({"_id": ObjectId(_id)}).next()
        if not existing_queue:
            raise BadDataException("Not Found")
        return existing_queue

    # prob dont need
    # removes user with specified user name
    def removeUser(self, _id: str):
        existing_user = self.user.find({"_id": ObjectId(_id)}).next()
        if not existing_user:
            raise BadDataException("Not Found")

        for queue_id in existing_user["queues"]:
            self.deleteQueue(existing_user["_id"], queue_id)
        self.user.delete_one({"_id": ObjectId(_id)})
        return existing_user

    def findOrder(self, _id: str):
        order = self.order.find(ObjectId(_id)).next()
        if not order:
            raise BadDataException("Order not found")
        return order

    # creates an order with specified information
    def createOrder(self, order: dict = None):
        if not order:
            raise BadDataException("Order is empty")
        existing_order = self.order.find_one({"itemId": order["itemId"]})
        if existing_order:
            raise BadDataException("Order has already been placed")
        self.order.insert(order)
        return order

    def updateOrder(self, _id: str, data: dict):
        existing_order = self.user.find({"_id": ObjectId(_id)}).next()
        if existing_order is None:
            raise BadDataException("error: order does not exist")
        self.order.replaceOne({"_id": ObjectId(_id)}, data)
        return existing_order

    # deletes order of specified orderid
    def deleteOrder(self, itemId: str):
        existing_order = self.order.find_one({"itemId": itemId})
        if not existing_order:
            raise BadDataException("Order not found")
        self.order.delete_one({"_id": existing_order["_id"]})
        return existing_order

    def findQueue(self, _id: str):
        queue = self.queue.find(ObjectId(_id)).next()
        if not queue:
            raise BadDataException("Queue not found")
        return queue

    # creates a queue for a specific user with queue_data in json format
    def createQueue(self, _id: str, data: dict):
        # checks if user exists and queue does not exist yet
        existing_user = self.user.find({"_id": ObjectId(_id)}).next()
        if not existing_user:
            raise BadDataException("User not found")

        queue = self.queue.insert(
            {"start": False, "orders": [], "max_bid": data["max_bid"],}
        )
        # adds the queueid to the array of queues each user has
        existing_user["queues"].append(queue["_id"])
        user = self.user.update(
            {"_id": ObjectId(_id)}, {"$set": {"queues": existing_user["queues"]}},
        )
        return user

    # dequeues an order from the queue assuming the queue is sorted
    def dequeue(self, _id):
        existing_queue = self.queue.find({"_id": ObjectId(_id)}).next()
        if not existing_queue:
            raise BadDataException("Queue not found")

        if not existing_queue["orders"]:
            raise BadDataException("No orders in queue")

        # pops the first order off the queue
        to_return = existing_queue["orders"].pop(0)

        # deletes the order and updates queue array of orders
        self.queue.update(
            {"_id": ObjectId(_id)}, {"$set": {"orders": existing_queue["orders"]}}
        )
        self.deleteOrder(to_return)

        return to_return

    # enqueues a order of specified information into specific queue
    def enqueue(self, _id: str, order: dict):
        existing_queue = self.queue.find({"_id": ObjectId(_id)}).next()
        if not existing_queue:
            raise BadDataException("Queue not found")
        existing_queue["orders"].append(order["_id"])
        self.queue.update(
            {"_id": ObjectId(_id)}, {"$set": {"orders": existing_queue["orders"]}}
        )
        return self.createOrder(order)

    # deletes a specific queue from specific user
    def deleteQueue(self, userId: str, queueId: str):
        existing_user = self.user.find({"_id": ObjectId(userId)}).next()
        if not existing_user:
            raise BadDataException("User not found")
        existing_queue = self.queue.find({"_id": ObjectId(queueId)}).next()
        if not existing_queue:
            raise BadDataException("Queue not found")

            # deletes each order in the queue
        for order_id in existing_queue["orders"]:
            self.deleteOrder(order_id)

        # deletes the queue
        self.queue.delete_one({"_id": ObjectId(queueId)})

        # removes the queue from the user
        existing_user["queues"].remove(queueId)
        self.user.update(
            {"_id": ObjectId(userId)}, {"$set": {"queues": existing_user["queues"]}}
        )
        return existing_queue
