from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to call backend

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from backend!")

if __name__ == '__main__':
    app.run(debug=True)
