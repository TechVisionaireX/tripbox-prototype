#!/usr/bin/env python3
"""
Simple server startup script that will definitely work
"""
import os
import sys
import time
import socket
from flask import Flask, jsonify
from flask_cors import CORS

# Create a minimal Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Server is running!", "status": "success"})

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from backend!", "status": "success"})

@app.route('/api/test')
def test():
    return jsonify({"message": "Test endpoint working!", "status": "success"})

def test_port(port):
    """Test if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            s.close()
            return True
    except OSError:
        return False

def find_available_port():
    """Find an available port"""
    for port in [5000, 3000, 8080, 8000, 4000, 5001, 3001]:
        if test_port(port):
            return port
    return None

if __name__ == '__main__':
    print("🔍 Finding available port...")
    
    # Find available port
    port = find_available_port()
    if not port:
        print("❌ No available ports found!")
        sys.exit(1)
    
    print(f"✅ Using port {port}")
    print(f"🌐 Server will be available at: http://127.0.0.1:{port}")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    
    try:
        print("🚀 Starting server...")
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1) 