from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message="Simple test server is running!")

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from simple test server!")

if __name__ == '__main__':
    print("Starting simple test server on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=False) 