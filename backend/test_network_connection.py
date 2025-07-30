#!/usr/bin/env python3
"""
Test Network Connection for TripBox
"""

import requests
import json

def test_connection():
    print("🔍 Testing Network Connection")
    print("📍 Testing against: http://localhost:5000")
    
    # Test 1: Basic connection
    print("\n1. Testing Basic Connection")
    try:
        response = requests.get("http://localhost:5000/api/hello", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is accessible")
            print(f"📝 Response: {response.json()}")
        else:
            print(f"❌ Backend returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - server might not be running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: CORS preflight
    print("\n2. Testing CORS Preflight")
    try:
        response = requests.options("http://localhost:5000/api/hello", timeout=5)
        if response.status_code == 200:
            print("✅ CORS preflight successful")
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    # Test 3: Login endpoint
    print("\n3. Testing Login Endpoint")
    try:
        response = requests.post("http://localhost:5000/api/login", 
                               json={"email": "test@example.com", "password": "test123"},
                               timeout=5)
        if response.status_code in [200, 401]:  # 401 is expected for invalid credentials
            print("✅ Login endpoint is accessible")
            print(f"📝 Status: {response.status_code}")
        else:
            print(f"❌ Login endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Login test error: {e}")
    
    # Test 4: Register endpoint
    print("\n4. Testing Register Endpoint")
    try:
        response = requests.post("http://localhost:5000/api/register", 
                               json={"name": "Test User", "email": "test@example.com", "password": "test123"},
                               timeout=5)
        if response.status_code in [200, 400]:  # 400 is expected if user already exists
            print("✅ Register endpoint is accessible")
            print(f"📝 Status: {response.status_code}")
        else:
            print(f"❌ Register endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Register test error: {e}")
    
    print("\n" + "="*50)
    print("🎉 NETWORK CONNECTION TEST COMPLETED!")
    print("="*50)
    return True

if __name__ == "__main__":
    test_connection() 