#!/usr/bin/env python3
"""
Super minimal Flask app for debugging Render deployment
"""
import os
import json
from datetime import datetime

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    print("✅ Flask imports successful")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    exit(1)

# Create minimal app
app = Flask(__name__)
CORS(app)  # Allow all CORS

print("✅ Minimal Flask app created")

@app.route('/')
def root():
    return jsonify({
        "message": "TripBox Minimal API is WORKING!",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "minimal-1.0"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Minimal backend is working perfectly",
        "timestamp": datetime.now().isoformat(),
        "server": "minimal-backend"
    })

@app.route('/api/hello')
def hello():
    return jsonify({
        "message": "Hello from minimal TripBox API!",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get('email', '')
        password = data.get('password', '')
        
        print(f"Login attempt - Email: {email}")
        
        # Simple test login
        if email == 'test@test.com' and password == 'test123':
            return jsonify({
                "message": "Login successful",
                "token": "minimal-test-token-123",
                "user": {
                    "id": 1,
                    "email": email,
                    "name": "Test User"
                }
            })
        else:
            return jsonify({
                "error": "Invalid credentials"
            }), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            "error": f"Login error: {str(e)}"
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        return jsonify({
            "message": "Registration successful (minimal mode)",
            "user": data
        })
    except Exception as e:
        return jsonify({
            "error": f"Registration error: {str(e)}"
        }), 500

# For debugging
@app.route('/debug')
def debug():
    return jsonify({
        "environment": dict(os.environ),
        "request_headers": dict(request.headers),
        "app_config": {
            "debug": app.debug,
            "testing": app.testing
        }
    })

# For Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 