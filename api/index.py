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
    
@app.route('/create_event', methods=['POST'])
@jwt_required()
def create_event():
    current_user = get_jwt_identity()
    user = db.users.find_one({"rollno": current_user})
    if user:
        new_event = {
            "name": request.json['name'],
            "description": request.json['description'],
            "date": request.json['date'],
            "time": request.json['time'],
            "venue": request.json['venue'],
            "departments": request.json['departments'],
            "years": request.json['years'],
            "organisation": request.json['organisation'],
            "organizer": user['name'],
            "organizer_rollno": user['rollno'],
            "poster": request.json['poster'],
        }
        db.events.insert_one(new_event)
        return jsonify({"message": "Event created successfully"}), 201
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/events', methods=['GET'])
@jwt_required()
def events():
    user_roll = get_jwt_identity()
    user = db.users.find_one({"rollno": user_roll})
    events = db.events.find()
    event_list = []
    
    for event in events:
        if user['department'] in event['departments'] and user['year'] in event['years']:
            event['_id'] = str(event['_id'])
            event_list.append({"event_id": event['_id'], "name": event['name'], "date": event['date'], "organization": event['organisation']})
                        
    return jsonify(event_list), 200

@app.route('/event/<event_id>', methods=['GET'])
def event(event_id):
    event = db.events.find_one({"_id": ObjectId(event_id)})
    if event:
        event['_id'] = str(event['_id'])
        return jsonify(event), 200
    else:
        return jsonify({"message": "Event not found"}), 404
    
@app.route('/register_event/<event_id>', methods=['POST'])
@jwt_required()
def register_event(event_id):
    user_roll = get_jwt_identity()
    user = db.users.find_one({"rollno": user_roll})
    event = db.events.find_one({"_id": ObjectId(event_id)})
    if event:
        if user_roll not in event['participants']:
            if user_roll.strip():
                db.events.update_one({"_id": ObjectId(event_id)}, {"$push": {"participants": user_roll}})
                return jsonify({"message": "Registered successfully"}), 200
            else:
                print("User roll number is empty. Not updating the database.")            
        else:
            return jsonify({"message": "Already registered"}), 200
    else:
        return jsonify({"message": "Event not found"}), 404
    
@app.route('/registered_events', methods=['GET'])
@jwt_required()
def registered_events():
    user_roll = get_jwt_identity()
    user = db.users.find_one({"rollno": user_roll})
    events = db.events.find()
    event_list = []
    
    for event in events:
        if user_roll in event['participants']:
            event['_id'] = str(event['_id'])
            event_list.append({"event_id": event['_id'], "name": event['name'], "date": event['date'], "organization": event['organisation']})
                        
    return jsonify(event_list), 200

# post routes

# Get all posts
@app.route('/posts', methods=['GET'])
def get_posts():
    posts = db.posts.find()
    post_list = list(posts)
    for post in post_list:
        post['_id'] = str(post['_id'])
        post['author_id'] = str(post['author_id'])
    return jsonify(post_list)
    

# Create a new post
@app.route('/posts/create', methods=['POST'])
@jwt_required()
def create_post():
    current_user = get_jwt_identity()
    user = db.users.find_one({"rollno": current_user})
    if user:
        new_post = {
            "content": request.json['content'],
            "post_date": datetime.datetime.now(),
   
            "author_id": user['_id'],
            "participants": []
        }
        post_id = db.posts.insert_one(new_post).inserted_id
        return jsonify({"message": "Post created successfully", "post_id": str(post_id)}), 201
    else:
        return jsonify({"message": "User not found"}), 404

# Get a specific post by ID
@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    post = db.posts.find_one({"_id": ObjectId(post_id)})
    if post:
        post['_id'] = str(post['_id'])
        post['author_id'] = str(post['author_id'])
        post['forum_id'] = str(post['forum_id'])
        return jsonify(post)
    else:
        return jsonify({"message": "Post not found"}), 404
    
# Update a specific post by ID
@app.route('/posts/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    current_user = get_jwt_identity()
    user = db.users.find_one({"rollno": current_user})
    if user:
        post = db.posts.find_one({"_id": ObjectId(post_id)})
        if post:
            if post['author_id'] == user['_id']:
                db.posts.update_one({"_id": ObjectId(post_id)}, 
                                    {"$set": {"content": request.json['content']}}
                                    )
                return jsonify({"message": "Post updated successfully"}), 200
            else:
                return jsonify({"message": "Unauthorized"}), 401
        else:
            return jsonify({"message": "Post not found"}), 404
    else:
        return jsonify({"message": "User not found"}), 404
    
# Delete a specific post by ID
@app.route('/posts/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    current_user = get_jwt_identity()
    user = db.users.find_one({"rollno": current_user})
    if user:
        post = db.posts.find_one({"_id": ObjectId(post_id)})
        if post:
            if post['author_id'] == user['_id']:
                db.posts.delete_one({"_id": ObjectId(post_id)})
                return jsonify({"message": "Post deleted successfully"}), 200
            else:
                return jsonify({"message": "Unauthorized"}), 401
        else:
            return jsonify({"message": "Post not found"}), 404
    else:
        return jsonify({"message": "User not found"}), 404
    

@app.route('/part_empty', methods=['GET'])
def part_empty():
    events = db.events.find()
    for event in events:
        if 'participants' not in event:
            db.events.update_one({"_id": event['_id']}, {"$set": {"participants": []}})
    return 'Participants attribute added successfully!'