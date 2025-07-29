#!/usr/bin/env python3
"""
Test script to verify deployment configuration
"""

import requests
import time
import sys

def test_backend():
    """Test if backend is responding"""
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_login():
    """Test login functionality"""
    try:
        response = requests.post("http://localhost:5000/api/login", 
                               json={"email": "test@test.com", "password": "test123"},
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                print("✅ Login test passed")
                return True
            else:
                print("❌ Login failed - no token received")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def main():
    print("🧪 Testing TripBox Deployment Configuration...")
    print("=" * 50)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    # Test backend
    if not test_backend():
        print("❌ Backend test failed")
        return False
    
    # Test login
    if not test_login():
        print("❌ Login test failed")
        return False
    
    print("=" * 50)
    print("🎉 All tests passed! Deployment configuration is correct.")
    print("📧 Test credentials: test@test.com / test123")
    print("🌐 Frontend: Open frontend/index.html in browser")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 