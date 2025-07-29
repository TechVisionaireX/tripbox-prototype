from flask import Flask, request
import os

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/')
def home():
    return {"message": "Working", "status": "ok"}

@app.route('/health')
def health():
    return {"status": "healthy"}

@app.route('/api/hello')
def hello():
    return {"message": "Hello"}

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return {}
    
    data = request.get_json() if request.is_json else {}
    email = data.get('email', '') if data else ''
    password = data.get('password', '') if data else ''
    
    if email == 'test@test.com' and password == 'test123':
        return {
            "message": "Login successful",
            "token": "test-token",
            "user": {"id": 1, "email": email, "name": "Test User"}
        }
    else:
        return {"error": "Invalid credentials"}, 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# For gunicorn
application = app
