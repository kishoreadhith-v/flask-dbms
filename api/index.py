from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId
import hashlib
import datetime
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity

# Load environment variables from .env file
load_dotenv()


app = Flask(__name__)

jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

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

@app.route('/collections', methods=['GET'])
def get_collections():
    # Get all collections in the database
    collections = db.list_collection_names()

    return jsonify(collections)

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

@app.route('/signup', methods=['POST'])
def signup():
    new_user = {
        "name": request.json['name'],
        "rollno": request.json['rollno'],
        "phone": request.json['phone'],
        "password": request.json['password'],
        "department": request.json['department'],
        "year": request.json['year'],
    }
    new_user['password'] = hashlib.sha256(new_user['password'].encode("utf-8")).hexdigest()
    doc = db.users.find_one({"rollno": new_user['rollno']})
    if not doc:
        db.users.insert_one(new_user)
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"message": "User already exists"}), 400
    
@app.route('/login', methods=['POST'])
def login():
    rollno = request.json['rollno']
    password = request.json['password']
    password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user = db.users.find_one({"rollno": rollno, "password": password})
    if user:
        access_token = create_access_token(identity=rollno)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = db.users.find_one({"rollno": current_user})
    if user:
        user['_id'] = str(user['_id'])
        del user['password']
        return jsonify(user), 200
    else:
        return jsonify({"message": "User not found"}), 404
    
