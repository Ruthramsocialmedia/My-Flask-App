from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from database import fs, db
import io
from bson import ObjectId
import os
import Camera_Access  # Import the camera module

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Serve the gallery.html file from the same folder
@app.route('/')
def serve_gallery():
    return send_from_directory(os.getcwd(), "gallery.html")

# API to get all image IDs
@app.route('/images', methods=['GET'])
def get_all_images():
    files = db.fs.files.find({}, {"_id": 1, "username": 1, "email": 1, "likes": 1})
    image_list = [{
        "_id": str(file["_id"]),
        "username": file.get("username", ""),
        "email": file.get("email", ""),
        "likes": len(file.get("likes", []))
    } for file in files]
    return jsonify(image_list)

# Route to upload an image with user details
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Check for required fields
        if 'image' not in request.files:
            return jsonify({"error": "No image file found"}), 400

        image_file = request.files['image']
        username = request.form.get('username')
        email = request.form.get('email')

        if not username or not email:
            return jsonify({"error": "Username and email are required"}), 400

        # Store image and user info in GridFS
        file_id = fs.put(image_file, filename=image_file.filename, username=username, email=email, likes=[])

        return jsonify({
            "message": "Image uploaded successfully",
            "file_id": str(file_id),
            "username": username,
            "email": email
        }), 201

    except Exception as e:
        print("Upload error:", e)
        return jsonify({"error": "Internal server error"}), 500

# Route to retrieve an image by ID
@app.route('/image/<file_id>', methods=['GET'])
def get_image(file_id):
    try:
        image_data = fs.get(ObjectId(file_id))
        return send_file(io.BytesIO(image_data.read()), mimetype="image/jpeg")
    except Exception as e:
        print("Image retrieval error:", e)
        return jsonify({"error": "Image not found"}), 404

# Route to like an image
@app.route('/image/<file_id>/like', methods=['POST'])
def like_image(file_id):
    try:
        user_ip = request.remote_addr  # Capture user IP

        image_data = db.fs.files.find_one({"_id": ObjectId(file_id)})

        if not image_data:
            return jsonify({"error": "Image not found"}), 404

        # Check if user already liked the image
        if user_ip in image_data.get("likes", []):
            return jsonify({"message": "You have already liked this image"}), 400

        # Add user IP to the likes
        db.fs.files.update_one({"_id": ObjectId(file_id)}, {"$push": {"likes": user_ip}})

        return jsonify({"message": "Image liked successfully"}), 200

    except Exception as e:
        print("Like error:", e)
        return jsonify({"error": "Internal server error"}), 500

# Route to start the camera
@app.route('/start-camera', methods=['GET'])
def start_camera():
    result = Camera_Access.open_camera()  # Call the function from the imported module
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(debug=True)
