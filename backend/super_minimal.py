#!/usr/bin/env python3
"""
Super minimal Flask app for debugging Render deployment - ULTRA SIMPLE VERSION
"""
import os

print("🚀 Starting super minimal TripBox backend...")

try:
    from flask import Flask, jsonify, request
    print("✅ Flask imported successfully")
except Exception as e:
    print(f"❌ Flask import failed: {e}")
    exit(1)

try:
    from flask_cors import CORS
    print("✅ CORS imported successfully")
except Exception as e:
    print(f"⚠️ CORS import failed, continuing without: {e}")
    CORS = None

# Create the simplest possible Flask app
app = Flask(__name__)

# Enable CORS if available
if CORS:
    CORS(app, origins="*")
    print("✅ CORS enabled")

print("✅ Flask app created successfully")

@app.route('/')
def root():
    return {
        "message": "🎉 TripBox Minimal Backend is WORKING!",
        "status": "success",
        "backend": "super-minimal-v2"
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "message": "Backend is working perfectly!",
        "version": "minimal-v2"
    }

@app.route('/api/hello')
def hello():
    return {
        "message": "Hello from minimal TripBox API!",
        "status": "working"
    }

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # Get JSON data safely
        if request.is_json:
            data = request.get_json()
        else:
            data = {}
        
        email = data.get('email', '') if data else ''
        password = data.get('password', '') if data else ''
        
        print(f"Login attempt - Email: {email}")
        
        # Simple test login
        if email == 'test@test.com' and password == 'test123':
            response = jsonify({
                "message": "✅ Login successful!",
                "token": "test-token-12345",
                "user": {
                    "id": 1,
                    "email": email,
                    "name": "Test User"
                }
            })
        else:
            response = jsonify({
                "error": "❌ Invalid credentials - use test@test.com / test123"
            })
            response.status_code = 401
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Login error: {e}")
        response = jsonify({
            "error": f"Server error: {str(e)}"
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    print(f"🌐 Test login: test@test.com / test123")
    
    # Run with the most basic configuration possible
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False,
        threaded=True
    ) 