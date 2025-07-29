#!/usr/bin/env python3
"""
TripBox-IntelliOrganizer Complete Startup Script
This script handles the complete setup and startup of the TripBox application.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    TripBox-IntelliOrganizer                  ║
    ║                        Complete Setup                         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Setup database and create tables"""
    print("\n🗄️  Setting up database...")
    try:
        # Change to backend directory
        original_dir = os.getcwd()
        os.chdir("backend")
        
        # Import and setup database
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
        
        # Change back to root
        os.chdir(original_dir)
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_backend():
    """Test if backend is working"""
    print("\n🧪 Testing backend...")
    try:
        # Start backend in background
        backend_process = subprocess.Popen([sys.executable, "app.py"], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
        
        # Wait for backend to start
        time.sleep(3)
        
        # Test health endpoint
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running successfully")
            backend_process.terminate()
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            backend_process.terminate()
            return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def create_test_user():
    """Create a test user for login"""
    print("\n👤 Creating test user...")
    try:
        response = requests.post("http://localhost:5000/api/create-test-user", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test user created: {data.get('email')} / {data.get('password')}")
            return True
        else:
            print(f"❌ Failed to create test user: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test user creation failed: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    # Test backend
    if not test_backend():
        return False
    
    # Create test user
    if not create_test_user():
        return False
    
    print("\n" + "="*60)
    print("🎉 TripBox-IntelliOrganizer Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Start the backend: python app.py")
    print("2. Open frontend/index.html in your browser")
    print("3. Login with: test@test.com / test123")
    print("\n🔗 URLs:")
    print("   Backend: http://localhost:5000")
    print("   Frontend: file:///path/to/frontend/index.html")
    print("\n📝 For deployment:")
    print("   - Backend: Deploy to Render/Heroku")
    print("   - Frontend: Deploy to Netlify/Vercel")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 