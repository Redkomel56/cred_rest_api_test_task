import os

PORT = os.getenv('PORT', 5000)
MONGO_DB_URI = os.getenv('DB_URI')
MONGO_DB_NAME = os.getenv('DB_NAME', 'test-data')