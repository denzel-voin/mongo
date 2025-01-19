from flask import Flask, jsonify, request
from pymongo import MongoClient
import redis

app = Flask(__name__)

redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

mongo_client = MongoClient('mongodb://mongo1:27017,mongo2:27017/?replicaSet=rs0')
mongo_db = mongo_client['my_database']
mongo_collection = mongo_db['my_collection']

@app.route('/')
def home():
    return jsonify({"message": "Python app is running!"})

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    mongo_collection.insert_one(data)

    redis_client.set(data.get('key'), data.get('value'))

    return jsonify({"message": "Data added successfully!"})

@app.route('/get/<key>', methods=['GET'])
def get_data(key):
    value = redis_client.get(key)

    if value:
        return jsonify({"key": key, "value": value})

    doc = mongo_collection.find_one({"key": key})
    if doc:
        return jsonify({"key": doc['key'], "value": doc['value']})

    return jsonify({"error": "Key not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
