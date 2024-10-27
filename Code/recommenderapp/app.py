from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_cors import CORS
import json
import os
import pandas as pd
import sys
import time
import requests
import random  # For generating OTP

sys.path.append("../../")
from Code.prediction_scripts.item_based import recommendForNewUser
from search import Search

app = Flask(__name__)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'movierecommenderx@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'Movies@123'  # Replace with your email password or app-specific password
mail = Mail(app)
app.secret_key = "secret key"
CORS(app, resources={r"/*": {"origins": "*"}})

# API keys for OMDB and YouTube Data API
OMDB_API_KEY = 'b726fa05'
YOUTUBE_API_KEY = 'AIzaSyB4FoU4IKFhxAjLu4pgucS0W1HJtVzSyuk'

# Path for storing user credentials
USER_CSV = "users.csv"

# Function to load users from CSV
def load_users():
    if not os.path.exists(USER_CSV) or pd.read_csv(USER_CSV).empty:
        df = pd.DataFrame(columns=["email", "password"])
        df.to_csv(USER_CSV, index=False)
        return {}
    try:
        return pd.read_csv(USER_CSV).set_index("email").to_dict(orient="index")
    except KeyError:
        df = pd.DataFrame(columns=["email", "password"])
        df.to_csv(USER_CSV, index=False)
        return {}

# Save user credentials to CSV
def save_user(email, password):
    df = pd.DataFrame([[email, password]], columns=["email", "password"])
    df.to_csv(USER_CSV, mode="a", index=False, header=not os.path.exists(USER_CSV))

# Load users initially
users = load_users()

# Function to retrieve movie information with YouTube trailer
def get_movie_info(title):
    index = len(title) - 6
    movie_name = title[0:index]
    
    # OMDB API call to get basic movie info
    omdb_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(omdb_url)
    
    if response.status_code == 200:
        res = response.json()
        if res['Response'] == "True":
            trailer_url = get_youtube_trailer(movie_name)
            res['Trailer'] = trailer_url  # Add trailer URL to response
            return res
        else:
            return {
                'Title': title, 
                'imdbRating': "N/A", 
                'Genre': 'N/A', 
                "Poster": "https://default-poster.com/default.jpg",
                'Trailer': "#"
            }
    else:
        return {
            'Title': title, 
            'imdbRating': "N/A", 
            'Genre': 'N/A', 
            "Poster": "https://default-poster.com/default.jpg",
            'Trailer': "#"
        }

# Function to get YouTube trailer URL
def get_youtube_trailer(movie_name):
    youtube_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={movie_name}+trailer&type=video&key={YOUTUBE_API_KEY}"
    response = requests.get(youtube_url)
    if response.status_code == 200:
        video_data = response.json()
        if video_data["items"]:
            video_id = video_data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
    return "#"  # Default if no trailer is found

@app.route("/")
def logsign_page():
    return render_template("logsign.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/landing", methods=["GET"])
def landing_page():
    if 'user' in session:  # Check if user is logged in
        return render_template("landing_page.html")
    return redirect(url_for('logsign_page'))

@app.route("/login", methods=["POST"])
def login():
    data = json.loads(request.data)
    email = data.get('email')
    password = data.get('password')
    
    # Check if the user exists and verify password
    user = users.get(email)
    if user and user['password'] == password:
        session['user'] = email  # Set user session
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = json.loads(request.data)
    email = data.get('email')
    
    # Generate a random OTP
    otp = random.randint(100000, 999999)
    users[email] = {'password': '', 'otp': otp, 'is_verified': False}  # Store user with OTP
    
    # Sending OTP via email
    try:
        msg = Message("Your OTP Code", sender=app.config['movierecommenderx@gmail.com'], recipients=[email])
        msg.body = f"Your OTP code is {otp}. Please enter this code to verify your email."
        mail.send(msg)
        print(f"OTP {otp} sent to {email}")  # Debugging output
        return jsonify({"success": True, "message": "OTP sent to your email!"}), 200
    except Exception as e:
        print(f"Failed to send email: {e}")  # Detailed error message for debugging
        return jsonify({"success": False, "message": "Failed to send OTP. Please try again."}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = json.loads(request.data)
    email = data.get('email')
    otp = data.get('otp')

    user = users.get(email)
    if user and user['otp'] == otp:
        user['is_verified'] = True  # Mark user as verified
        return jsonify({"success": True, "message": "OTP verified! You can now create a password."}), 200
    
    return jsonify({"success": False, "message": "Invalid OTP."}), 401

@app.route("/create-account", methods=["POST"])
def create_account():
    data = json.loads(request.data)
    email = data.get('email')
    password = data.get('password')

    user = users.get(email)
    if user and user['is_verified']:
        user['password'] = password  # Set the user's password
        save_user(email, password)  # Save user to CSV
        return jsonify({"success": True, "message": "Account created successfully! Please login."}), 200
    
    return jsonify({"success": False, "message": "User not verified."}), 401

@app.route("/predict", methods=["POST"])
def predict():
    data = json.loads(request.data)  # contains movies
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        training_data.append(movie_with_rating)
    recommendations = recommendForNewUser(training_data)
    recommendations = recommendations[:10]

    movie_with_rating = {}
    for movie in recommendations:
        movie_info = get_movie_info(movie)
        if movie_info:
            movie_with_rating[movie + "-r"] = movie_info['imdbRating']
            movie_with_rating[movie + "-g"] = movie_info['Genre']
            movie_with_rating[movie + "-p"] = movie_info['Poster']
            movie_with_rating[movie + "-t"] = movie_info.get('Trailer', "#")  # Include trailer link

    resp = {"recommendations": recommendations, "rating": movie_with_rating}
    return resp

@app.route("/search", methods=["POST"])
def search():
    term = request.form["q"]
    search = Search()
    filtered_dict = search.resultsTop10(term)
    resp = jsonify(filtered_dict)
    resp.status_code = 200
    return resp

@app.route("/feedback", methods=["POST"])
def feedback():
    data = json.loads(request.data)
    with open(f"experiment_results/feedback_{int(time.time())}.csv", "w") as f:
        for key in data.keys():
            f.write(f"{key} - {data[key]}\n")
    return data

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
