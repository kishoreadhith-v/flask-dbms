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
    

# post routes
# Get all posts in a forum
@app.route('/posts', methods=['GET'])
def get_posts():
    forum_id = request.args.get('forum_id')
    if not forum_id:
        return jsonify({"message": "forum_id is required"}), 400
    
    try:
        posts = db.posts.find({"forum_id": ObjectId(forum_id)})
        post_list = list(posts)
        for post in post_list:
            post['_id'] = str(post['_id'])
            post['author_id'] = str(post['author_id'])
            post['forum_id'] = str(post['forum_id'])
        return jsonify(post_list)
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# Create a new post
@app.route('/posts/create', methods=['POST'])
@jwt_required()
def create_post():
    try:
        current_user = get_jwt_identity()
        user = db.users.find_one({"rollno": current_user})
        if user:
            new_post = {
                "content": request.json['content'],
                "post_date": datetime.datetime.now(),
                "forum_id": ObjectId(request.json['forum_id']),
                "author_id": user['_id'],
            }
            post_id = db.posts.insert_one(new_post).inserted_id
            return jsonify({"message": "Post created successfully", "post_id": str(post_id)}), 201
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# Get a specific post by ID
@app.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = db.posts.find_one({"_id": ObjectId(post_id)})
        if post:
            post['_id'] = str(post['_id'])
            post['author_id'] = str(post['author_id'])
            post['forum_id'] = str(post['forum_id'])
            return jsonify(post)
        else:
            return jsonify({"message": "Post not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
# Update a specific post by ID
@app.route('/posts/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    try:
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
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
# Delete a specific post by ID
@app.route('/posts/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
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
    except Exception as e:
        return jsonify({"message": str(e)}), 400



# reply routes
# Get all replies to a post
@app.route('/replies', methods=['GET'])
def get_replies():
    post_id = request.args.get('post_id')
    if not post_id:
        return jsonify({"message": "post_id is required"}), 400
    
    try:
        replies = db.replies.find({"post_id": ObjectId(post_id)})
        reply_list = list(replies)
        for reply in reply_list:
            reply['_id'] = str(reply['_id'])
            reply['author_id'] = str(reply['author_id'])
            reply['post_id'] = str(reply['post_id'])
        return jsonify(reply_list)
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# Create a new reply
@app.route('/replies/create', methods=['POST'])
@jwt_required()
def create_reply():
    try:
        current_user = get_jwt_identity()
        user = db.users.find_one({"rollno": current_user})
        if user:
            new_reply = {
                "content": request.json['content'],
                "reply_date": datetime.datetime.now(),
                "post_id": ObjectId(request.json['post_id']),
                "author_id": user['_id'],
            }
            reply_id = db.replies.insert_one(new_reply).inserted_id
            return jsonify({"message": "Reply created successfully", "reply_id": str(reply_id)}), 201
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
# delete a specific reply by ID
@app.route('/replies/<reply_id>', methods=['DELETE'])
@jwt_required()
def delete_reply(reply_id):
    try:
        current_user = get_jwt_identity()
        user = db.users.find_one({"rollno": current_user})
        if user:
            reply = db.replies.find_one({"_id": ObjectId(reply_id)})
            if reply:
                if reply['author_id'] == user['_id']:
                    db.replies.delete_one({"_id": ObjectId(reply_id)})
                    return jsonify({"message": "Reply deleted successfully"}), 200
                else:
                    return jsonify({"message": "Unauthorized"}), 401
            else:
                return jsonify({"message": "Reply not found"}), 404
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 400



# forum routes
# Get all forums
@app.route('/forums', methods=['GET'])
def get_forums():
    try:
        forums = db.forums.find()
        forum_list = list(forums)
        for forum in forum_list:
            forum['_id'] = str(forum['_id'])
        return jsonify(forum_list)
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# Create a new forum
@app.route('/forums/create', methods=['POST'])
@jwt_required()
def create_forum():
    try:
        current_user = get_jwt_identity()
        user = db.users.find_one({"rollno": current_user})
        if user:
            new_forum = {
                "title": request.json['title'],
                "description": request.json['description'],
                "created_date": datetime.datetime.now(),
                "author_id": user['_id'],
            }
            forum_id = db.forums.insert_one(new_forum).inserted_id
            return jsonify({"message": "Forum created successfully", "forum_id": str(forum_id)}), 201
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
