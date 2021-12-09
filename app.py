from flask import Flask, session, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt
from flask_cors import CORS, cross_origin
from bson.json_util import dumps

host = os.environ.get("DATABASE_URL")
client = MongoClient(host=host)
db = client.Devpeak
users = db.users
posts = db.posts
comments = db.comments

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return "Hello world"


@app.route('/login', methods=['POST'])
# @cross_origin()
def login():
    content = request.json
    user = users.find_one({'username': content['username']})

    if user:
        user_password = user['password']
        password = f"{content['password']}"
        if bcrypt.checkpw(password.encode('utf-8'), user_password):
            return {"success": True, "_id": str(user['_id']), "name": user['name']}
        else:
            return {"success": False, "message": "Incorrect username/password"}
    else:
        return {"success": False, "message": "Incorrect username/password"}


@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    content = request.json
    check_username = users.find_one({'username': content['username']})
    check_email = users.find_one({'email': content['email']})
    if check_username:
        return {"success": False, "message": "Username Taken"}
    elif check_email:
        return {"success": False, "message": "Email already in use"}
    else:
        hashed_pwd = bcrypt.hashpw(
            content['password'].encode('utf8'), bcrypt.gensalt())
        new_user = {
            'name': content['name'],
            'username': content['username'],
            'email': content['email'],
            'password': hashed_pwd,
            'liked_posts': []
        }
        users.insert_one(new_user)
        user = users.find_one({'username': content['username']})
        return {"success": True, "_id": str(user['_id']), "name": user['name']}


@app.route('/all-users', methods=['GET'])
@cross_origin()
def all_users():
    many_users = users.find()
    print(many_users)
    for user in many_users:
        print(user)


@app.route('/post', methods=['POST'])
@cross_origin()
def new_post():
    content = request.json
    print(content['text'])
    if str(content['text']) == "console_default":
        text = "console.log(\"hello world\")"
    else:
        text = content['text']
    text = content['text']
    _id = content['_id']
    user = users.find_one({'_id': ObjectId(_id)})
    if user:
        posts.insert_one({
            "text": text,
            "user_id": _id,
            "username": user['username'],
            "name": user['name'],
            "likes": 0,
            "comments": 0
        })
        return {"success": True}
    else:
        return {"success": False, "message": "User not found"}


@app.route('/all-posts/<_id>', methods=['GET'])
@cross_origin()
def all_posts(_id):
    user = users.find_one({'_id': ObjectId(_id)})
    if user:
        all_posts = dumps(posts.find().sort([['_id', -1]]))
        return {"success": True, "posts": all_posts, "liked_posts": user['liked_posts']}

@app.route('created-posts/<_id>', methods=['GET'])
@cross_origin()
def created_posts(_id):
    user = users.find_one({'_id': ObjectId(_id)})
    if user: 
        all_posts = dumps(posts.find({'user_id': ObjectId(_id)}).sort([['_id', -1]]))
        return {"success": True, "posts": all_posts, "liked_posts": user['liked_posts']}

@app.route('/delete-post/<_id>/<user_id>', methods=['DELETE'])
@cross_origin()
def delete_post(_id, user_id):
    print(user_id)
    user = users.find_one({'_id': ObjectId(user_id)})
    if user:
        post = posts.find_one({'_id': ObjectId(_id)})
        print(f"{user_id} - {post['user_id']}")
        if post:
            if post['user_id'] == user_id:
                posts.delete_one({'_id': ObjectId(_id)})
                return {"success": True}
            else:
                print('invalid access')
                return {"success": False, "message": "Invalid access"}
        else:
            print('post not found')
            return {"success": False, "message": "Post not found"}
    else:
        print('user not found')
        return {"success": False, "message": "User not found"}


@app.route('/update-liked-post/<_id>/<user_id>', methods=['PUT'])
@cross_origin()
def update_liked_posts(_id, user_id):
    user = users.find_one({'_id': ObjectId(user_id)})
    if user:
        global already_liked
        already_liked = False
        liked_posts = list(user['liked_posts'])
        post = posts.find_one({'_id': ObjectId(_id)})
        print(user_id)
        if (post):
            for liked_post in liked_posts:
                if liked_post == _id:
                    already_liked = True
            if already_liked:
                posts.update_one(
                    {'_id': ObjectId(_id)},
                    {'$set': {'likes': post['likes'] - 1}}
                )
                liked_posts.remove(_id)
            else:
                posts.update_one(
                    {'_id': ObjectId(_id)},
                    {'$set': {'likes': post['likes'] + 1}}
                )
                liked_posts.append(_id)

            users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'liked_posts': liked_posts}}
            )
            return {"success": True}
        else:
            return {"success": False, "message": "Post not found"}
    else:
        return {"success": False, "message": "User not found"}


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
