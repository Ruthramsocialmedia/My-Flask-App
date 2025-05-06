from pymongo import MongoClient
import gridfs

try:
    client = MongoClient("mongodb+srv://chennaicorprm:biuIvx7I7akjQx1B@cluster0.5y2ndpd.mongodb.net/VirtualTour?retryWrites=true&w=majority", serverSelectionTimeoutMS=5000)
    db = client["VirtualTour"]
    fs = gridfs.GridFS(db)

    # Test connection
    client.server_info()

    # Safely create index
    db.fs.files.create_index([("location", "2dsphere")])

except Exception as e:
    print("Database connection/index error:", e)
    db = None
    fs = None

