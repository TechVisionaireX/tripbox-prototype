#!/usr/bin/env python3
"""
TripBox Startup Script
This script ensures the backend starts properly for deployment
"""

import os
import sys

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory for proper execution
os.chdir(backend_path)

try:
    # Import the Flask app from backend
    from app import app
    
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        print("🚀 TripBox-IntelliOrganizer Starting...")
        print(f"📍 Running on: http://localhost:{port}")
        print("📧 Test Login: test@test.com / test123")
        app.run(host="0.0.0.0", port=port, debug=False)
        
except Exception as e:
    print(f"❌ Failed to start TripBox: {e}")
    print("🔄 Attempting to start simple app...")
    
    # Fallback to simple app if main app fails
    try:
        from simple_app import app
        port = int(os.environ.get('PORT', 5000))
        print("🚀 Simple TripBox Starting...")
        print(f"📍 Running on: http://localhost:{port}")
        print("📧 Test Login: test@test.com / test123")
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e2:
        print(f"❌ Failed to start simple app: {e2}")
        sys.exit(1) 