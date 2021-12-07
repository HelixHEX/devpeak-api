from flask import Flask, session

from pymongo import MongoClient
from bson.objectid import ObjectId
import os

db_url = os.environ.get("DATABASE_URL")
client = MongoClient(host=db_url)
db = client.Devpeak

app = Flask(__name__)

@app.route('/')
def index():
    pass
  
@app.route('/login')
def login():
    pass

@app.route('/signup')
def signup():
    pass
