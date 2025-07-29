#!/usr/bin/env python3
"""
Comprehensive backend test script
"""

import requests
import time
import sys
import os

def test_backend_health():
    """Test if backend is responding"""
    try:
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

def test_register():
    """Test registration functionality"""
    try:
        response = requests.post("http://localhost:5000/api/register", 
                               json={"email": "test2@test.com", "password": "test123", "name": "Test User 2"},
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                print("✅ Registration test passed")
                return True
            else:
                print("❌ Registration failed - no token received")
                return False
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False

def test_create_test_user():
    """Test create test user endpoint"""
    try:
        response = requests.post("http://localhost:5000/api/create-test-user", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "email" in data and data["email"] == "test@test.com":
                print("✅ Create test user endpoint passed")
                return True
            else:
                print("❌ Create test user failed - wrong response")
                return False
        else:
            print(f"❌ Create test user failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Create test user test failed: {e}")
        return False

def main():
    print("🧪 Testing TripBox Backend...")
    print("=" * 50)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Login", test_login),
        ("Registration", test_register),
        ("Create Test User", test_create_test_user)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        print("📧 Test credentials: test@test.com / test123")
        print("🌐 Frontend: Open frontend/index.html in browser")
        return True
    else:
        print("❌ Some tests failed. Please check the backend.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 