#!/usr/bin/env python3
"""
TripBox Main Startup Script
This script ensures the main backend starts properly for deployment
"""

import os
import sys
import subprocess

def setup_venv():
    """Setup virtual environment if needed"""
    try:
        # Check if we're in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment detected")
            return True
        else:
            print("⚠️ No virtual environment detected, continuing...")
            return False
    except Exception as e:
        print(f"⚠️ Virtual environment check failed: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    print("🚀 TripBox-IntelliOrganizer Starting...")
    print("=" * 50)
    
    # Setup virtual environment
    setup_venv()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
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
        print(f"❌ Failed to start main app: {e}")
        print("🔄 Attempting to start minimal app...")
        
        # Fallback to minimal app if main app fails
        try:
            from minimal_app import app
            port = int(os.environ.get('PORT', 5000))
            print("🚀 Minimal TripBox Starting...")
            print(f"📍 Running on: http://localhost:{port}")
            print("📧 Test Login: test@test.com / test123")
            app.run(host="0.0.0.0", port=port, debug=False)
        except Exception as e2:
            print(f"❌ Failed to start minimal app: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main() 