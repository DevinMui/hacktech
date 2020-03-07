from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
import json

username = ''
password = ''
with open('config.json') as json_data_file:
    data = json.load(json_data_file)
    username = data['db']['user']
    password = data['db']['passwd']

app = Flask(__name__)

print(username, password)
client = MongoClient('mongodb+srv://'+username+':'+password +
                     '@cluster0-u93bv.azure.mongodb.net/test?retryWrites=true&w=majority')


db = client.ebayBidQueue

'''
#HTTP REQUEST CODE TO IMPLEMENT:

@app.route("/")
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('index.html')

# takes login information in json format and checks if user exists in db, can use either username or email
@app.route('/login', methods=['POST'])
def login():
    user = db.user
    req_data = request.get_json()
    login_user = user.find_one({'username': req_data['username']})
    login_email = user.find_one({'email': req_data['email']})
    if login_user:
        if req_data['password'] == login_user['password']:
            session['username'] = req_data['username']
            return redirect(url_for('index'))
    elif login_email:
        if req_data['password'] == login_email['password']:
            session['email'] = req_data['email']
            return redirect(url_for('index'))
    return 'Invalid username/password combination'

# takes register data and creates a user document in db cluster of the user's info
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        req_data = request.get_json()
        session['username'] = req_data['username']
        return createUser(req_data)
    return render_template('register.html')
'''


def createUser(req_data):
    user = db.user
    existing_user = user.find_one({'username': req_data['username']})
    existing_email = user.find_one({'email': req_data['email']})
    if req_data['username'] == '' or req_data['email'] == '':
        return 'error: empty input'
    if existing_user is None and existing_email is None:
        user.insert(
            {'email': req_data['email'], 'username': req_data['username'], 'password': req_data['password'],
             'queues': req_data['queues'], 'token': req_data['token'], 'refresh': req_data['refresh'], 'ExperiesIn': req_data['ExpiresIn']})
        return 'User: ' + req_data['email'] + ' username: ' + req_data['username'] + ' has signed up'
    return 'Username/email already exists'


def updateUser(username, attributToUpdate, newValue):
    existing_user = db.user.find_one({'username': username})
    if existing_user:
        db.user.update({"username": username}, {
            '$set': {attributToUpdate: newValue}})
    else:
        return 'error: order does not exist'


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


def createOrder(name, ebayID):
    existing_order = db.order.find_one({'orderid': ebayID})
    if name == '':
        return 'error, input empty'
    if existing_order is None:
        db.order.insert(
            {'orderid': ebayID, 'name': name}
        )
    else:
        return 'error: order already exists'


def deleteOrder(orderid):
    existing_order = db.order.find_one({'orderid': orderid})
    if existing_order:
        db.order.delete_one({
            "orderid": orderid
        })
    else:
        return 'error: order does not exist'


def createQueue(username, queue_data):
    existing_user = db.user.find_one({'username': username})
    existing_queue = db.queue.find_one({'queueid': queue_data['queueid']})
    if existing_queue is None:
        if existing_user:
            existing_user['queues'].append(queue_data['queueid'])
            db.user.update({"username": username}, {
                '$set': {'queues': existing_user['queues']}})
            db.queue.insert(
                {'queueid': queue_data['queueid'], 'start': queue_data['start'], 'orders': queue_data['orders']})
        else:
            return 'error: user does not exist'
    else:
        return 'error: queue id already exists'


def dequeue(queueid):
    existing_queue = db.queue.find_one({'queueid': queueid})

    if existing_queue:
        if not len(existing_queue['orders']) == 0:
            to_return = existing_queue['orders'].pop(0)
            deleteOrder(to_return)
            db.queue.update({"queueid": queueid}, {
                '$set': {'orders': existing_queue['orders']}})
            deleteOrder(to_return)
            return to_return
        else:
            'error: queue empty'
    else:
        return 'error: queue does not exist'


def enqueue(queueid, orderid, name):
    existing_queue = db.queue.find_one({'queueid': queueid})
    existing_order = db.order.find_one({'orderid': orderid})
    if existing_order is None:
        createOrder(name, orderid)
        if existing_queue:
            existing_queue['orders'].append(orderid)
            db.queue.update({"queueid": queueid}, {
                '$set': {'orders': existing_queue['orders']}})
        else:
            return 'error: queue does not exist'
    else:
        return 'error: order id already exists'


def deleteQueue(username, queueid):

    existing_user = db.user.find_one({'username': username})
    existing_queue = db.queue.find_one({'queueid': queueid})

    if existing_user:
        for order_id in existing_queue['orders']:
            deleteOrder(order_id)
        db.queue.delete_one({
            "queueid": queueid
        })
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

if __name__ == "__main__":
    app.secret_key = 'secret'
    app.run(debug=True)
