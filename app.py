#!/usr/bin/env python3
"""
TripBox-IntelliOrganizer Main Application Entry Point
This file serves as the main entry point for the TripBox application.
It properly imports and runs the Flask app from the backend directory.
"""

import os
import sys

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory for proper execution
os.chdir(backend_path)

# Import the Flask app from backend
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TripBox-IntelliOrganizer on port {port}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🔗 Backend URL: http://localhost:{port}")
    print(f"🌐 Frontend URL: http://localhost:3000")
    app.run(host="0.0.0.0", port=port, debug=False) 