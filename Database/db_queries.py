from pymongo import MongoClient
import json



username = ''
password = ''
with open('config.json') as json_data_file:
    data = json.load(json_data_file)
    username = data['db']['user']
    password = data['db']['passwd']


client = MongoClient('mongodb+srv://'+username+':'+password +
                     '@cluster0-u93bv.azure.mongodb.net/test?retryWrites=true&w=majority')
db = client.ebayBidQueue


#creates user from req_data in json format
def createUser(req_data):
    user = db.user

    #finds the users with the specified email and username
    existing_user = user.find_one({'username': req_data['username']})
    existing_email = user.find_one({'email': req_data['email']})
    
    #checks if empty input
    if req_data['username'] == '' or req_data['email'] == '':
        return 'error: empty input'

    #if username and email do not exist yet, create user with provided information
    if existing_user is None and existing_email is None:
        user.insert(
            {'email': req_data['email'], 'username': req_data['username'], 'password': req_data['password'],
             'queues': req_data['queues'], 'token': req_data['token'], 'refresh': req_data['refresh'], 'ExperiesIn': req_data['ExpiresIn']})
        return 'User: ' + req_data['email'] + ' username: ' + req_data['username'] + ' has signed up'
    return 'Username/email already exists'

#update data of specified user 
def updateUser(username, attributToUpdate, newValue):
    existing_user = db.user.find_one({'username': username})
    #check if user exists
    if existing_user:
        db.user.update({"username": username}, {
            '$set': {attributToUpdate: newValue}})
    else:
        return 'error: order does not exist'

#returns the user document with specified username if user exists
def getUser(username):
    existing_user = db.user.find_one({'username': username})
    if existing_user:
        return existing_user
    else:
        return 'error: order does not exist'
#removes user with specified user name
def removeUser(username):
    existing_user = db.user.find_one({'username': username})
    if existing_user:
        for queue_id in existing_user['queues']:
            deleteQueue(username, queue_id)
        db.user.delete_one({
            "username": username
        })
    else:
        return 'error: user does not exist'

#creates an order with specified information
def createOrder(name, ebayID, price, quantity):
    existing_order = db.order.find_one({'orderid': ebayID})
    if name == '':
        return 'error, input empty'
    if existing_order is None:
        db.order.insert(
            {'orderid': ebayID, 'name': name, 'price':price, 'quantity': quantity}
        )
    else:
        return 'error: order already exists'

#deletes order of specified orderid
def deleteOrder(orderid):
    existing_order = db.order.find_one({'orderid': orderid})
    if existing_order:
        db.order.delete_one({
            "orderid": orderid
        })
    else:
        return 'error: order does not exist'

#creates a queue for a specific user with queue_data in json format
def createQueue(username, queue_data):
    #checks if user exists and queue does not exist yet
    existing_user = db.user.find_one({'username': username})
    existing_queue = db.queue.find_one({'queueid': queue_data['queueid']})
    if existing_queue is None:
        if existing_user:
            #adds the queueid to the array of queues each user has
            existing_user['queues'].append(queue_data['queueid'])
            db.user.update({"username": username}, {
                '$set': {'queues': existing_user['queues']}})

            #insert create queue with specified queue_data
            db.queue.insert(
                {'queueid': queue_data['queueid'], 'start': queue_data['start'], 'orders': queue_data['orders'], 'cutoff_amt': queue_data['cutoff_amt']})
        else: 
            return 'error: user does not exist'
    else:
        return 'error: queue id already exists'

#dequeues an order from the queue assuming the queue is sorted
def dequeue(queueid):
    existing_queue = db.queue.find_one({'queueid': queueid})
    #checks if queue exists
    if existing_queue:
        #makes sure there are still orders in queue
        if not len(existing_queue['orders']) == 0:
            #pops the first order off the queue
            to_return = existing_queue['orders'].pop(0)

            #deletes the order and updates queue array of orders
            db.queue.update({"queueid": queueid}, {
                '$set': {'orders': existing_queue['orders']}})
            deleteOrder(to_return)

            return to_return
        else:
            'error: queue empty'
    else:
        return 'error: queue does not exist'

#enqueues a order of specified information into specific queue
def enqueue(queueid, orderid, name, price, quantity):
    existing_queue = db.queue.find_one({'queueid': queueid})
    existing_order = db.order.find_one({'orderid': orderid})
    #checks if order already exists
    if existing_order is None:
        #if not create the order and update queue
        if existing_queue:
            createOrder(name, orderid, price, quantity)
            existing_queue['orders'].append(orderid)
            db.queue.update({"queueid": queueid}, {
                '$set': {'orders': existing_queue['orders']}})
        else:
            return 'error: queue does not exist'
    else:
        return 'error: order id already exists'

#deletes a specific queue from specific user
def deleteQueue(username, queueid):

    existing_user = db.user.find_one({'username': username})
    existing_queue = db.queue.find_one({'queueid': queueid})

    #checks if user exists
    if existing_user:

        #deletes each order in the queue
        for order_id in existing_queue['orders']:
            deleteOrder(order_id)

        #deletes the queue
        db.queue.delete_one({
            "queueid": queueid
        })

        #removes the queue from the user
        existing_user['queues'].remove(queueid)
        db.user.update({"username": username}, {
            '$set': {'queues': existing_user['queues']}})
    else:
        return 'error: user does not exist'

'''
#testing code:


user = {"email": "sky@gmail.com", "username": "sky", "password": "123",
        "queues": [], "token": "", "refresh": "", "ExpiresIn": 0}
order = {"orderid": 9876, "name": "order1"}
queue = {"queueid": 12345, "start": True, "orders": [9876]}

user_json = json.loads(json.dumps(user))
order_json = json.loads(json.dumps(order))
queue_json = json.loads(json.dumps(queue))

createUser(user)

createQueue("sky", queue_json)

deleteQueue('sky', 12345)

enqueue(queue_json['queueid'],
              order_json['orderid'], order_json['name'])

dequeue(12345)

updateUser('sky', 'password', 'adsfhl')

removeUser('sky')
'''