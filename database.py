from pymongo import MongoClient
from gridfs import GridFS

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.userUploads
fs = GridFS(db)
