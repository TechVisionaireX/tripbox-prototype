from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins="*")

@app.route('/api/hello')
def hello():
    return jsonify(message="TripBox API is running!", version="1.0.0")

@app.route('/health')
def health():
    return jsonify(status="healthy", message="API is working")

@app.route('/api/login', methods=['POST'])
def login():
    return jsonify(success=True, message="Login endpoint working", token="test_token_123")

@app.route('/api/test')
def test():
    return jsonify(success=True, message="Backend API is working properly")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

application = app 