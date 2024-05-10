from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get MongoDB URI from environment variables
mongo_uri = os.getenv("MONGO_URI")

# Create a MongoClient object using the connection string
client = MongoClient(mongo_uri)

# Access the database directly by name
db = client.get_database("clubs-events")  # Replace "your_database_name" with your actual database name

@app.route('/')
def home():
    return 'Hello, SQL! (real)'

@app.route('/env')
def env():
    return os.getenv("STRING")

@app.route('/about')
def about():
    return 'About'

@app.route('/test_post', methods=['POST'])
def test_post():
    # Get data from request body
    data = request.json

    # Insert the data into a collection called 'users'
    db.users.insert_one(data)

    return 'Data inserted successfully!'

@app.route('/test_get', methods=['GET'])
def test_get():
    # Retrieve data from the 'users' collection
    users = db.users.find()

    # Convert MongoDB cursor to list of dictionaries
    user_list = list(users)

    # Convert ObjectId to string for JSON serialization
    for user in user_list:
        user['_id'] = str(user['_id'])

    # Convert list to JSON and return
    return jsonify(user_list)
