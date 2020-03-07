from db_queries import *
import json

user = {
    "email": "sky@gmail.com",
    "username": "sky",
    "password": "123",
    "queues": [],
    "token": "",
    "refresh": "",
    "ExpiresIn": 0,
}
order = {"orderid": 9876, "name": "order1"}
queue = {"queueid": 12345, "start": True, "orders": [9876]}

user_json = json.loads(json.dumps(user))
order_json = json.loads(json.dumps(order))
queue_json = json.loads(json.dumps(queue))

createUser(user)

createQueue("sky", queue_json)

deleteQueue("sky", 12345)

enqueue(queue_json["queueid"], order_json["orderid"], order_json["name"])

dequeue(12345)

updateUser("sky", "password", "adsfhl")

removeUser("sky")

