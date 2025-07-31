from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from backend!")

@app.route('/api/login', methods=['POST'])
def login():
    return jsonify(message="Login endpoint working!")

if __name__ == '__main__':
    print("Starting simple server on port 3000...")
    app.run(host='localhost', port=3000, debug=True) 