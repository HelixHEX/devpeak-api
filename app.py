from flask import Flask, session, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt

host = os.environ.get("DATABASE_URL")
client = MongoClient(host=host)
db = client.Devpeak
users = db.users

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello world"


@app.route('/login', methods=['POST'])
def login():
    content = request.json
    user = users.find_one({'username': content['username']})
    user_password = user['password']
    password = f"{content['password']}"
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user_password):
            return {"success": True, "_id": str(user['_id'])}
        else:
            return {"success": False, "message": "Incorrect username/password"}
    else:
        return {"success": False, "message": "Incorrect username/password"}


@app.route('/signup', methods=['POST'])
def signup():
    content = request.json
    check_username = users.find_one({'username': content['username']})
    check_email = users.find_one({'email': content['email']})
    if check_username:
        return {"success": False, "message": "Username Taken"}
    elif check_email:
        return {"success": False, "message": "Email already in use"}
    else:
        hashed_pwd = bcrypt.hashpw(content['password'].encode('utf8'), bcrypt.gensalt())
        new_user = {
            'name': content['name'],
            'username': content['username'],
            'email': content['email'],
            'password': hashed_pwd
        }
        users.insert_one(new_user)
        return {"success": True}


@app.route('/all-users', methods=['GET'])
def all_users():
    many_users = users.find()
    print(many_users)
    for user in many_users:
        print(user)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
