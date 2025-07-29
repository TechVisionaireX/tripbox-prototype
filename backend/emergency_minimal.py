#!/usr/bin/env python3
"""
Emergency minimal Flask backend for TripBox
"""
import os

print("Starting emergency minimal backend...")

# Try to import Flask
try:
    from flask import Flask, request
    print("Flask imported successfully")
except:
    print("Flask not available")
    exit(1)

# Create app
app = Flask(__name__)
print("Flask app created")

# Add manual CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return {
        "message": "TripBox Emergency Backend is Working",
        "status": "success",
        "version": "emergency-v1"
    }

@app.route('/health')
def health():
    return {"status": "healthy", "backend": "emergency"}

@app.route('/api/hello')
def hello():
    return {"message": "Hello from emergency backend"}

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return {'status': 'ok'}
    
    try:
        data = request.get_json() if request.is_json else {}
        email = data.get('email', '') if data else ''
        password = data.get('password', '') if data else ''
        
        print(f"Login attempt for email: {email}")
        
        if email == 'test@test.com' and password == 'test123':
            return {
                "message": "Login successful",
                "token": "emergency-token-123",
                "user": {"id": 1, "email": email, "name": "Test User"}
            }
        else:
            return {"error": "Invalid credentials"}, 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return {"error": "Server error"}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Emergency backend starting on port {port}")
    app.run(host='0.0.0.0', port=port) 