#!/usr/bin/env python3
"""
EMERGENCY MINIMAL - Absolute simplest Flask app possible
"""
import os

print("🚨 EMERGENCY MINIMAL BACKEND STARTING...")

# Try to import Flask
try:
    from flask import Flask, request
    print("✅ Flask imported")
except:
    print("❌ Flask not available")
    exit(1)

# Create app
app = Flask(__name__)
print("✅ Flask app created")

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
        "message": "🎉 EMERGENCY BACKEND IS WORKING!",
        "status": "success",
        "version": "emergency-v1"
    }

@app.route('/health')
def health():
    return {"status": "healthy", "backend": "emergency"}

@app.route('/api/hello')
def hello():
    return {"message": "Hello from emergency backend!"}

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return {'status': 'ok'}
    
    return {
        "message": "✅ Emergency login works!",
        "token": "emergency-token-123",
        "user": {"id": 1, "email": "test@test.com", "name": "Emergency User"}
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Emergency backend starting on port {port}")
    app.run(host='0.0.0.0', port=port) 