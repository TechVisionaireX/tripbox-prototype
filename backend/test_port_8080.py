#!/usr/bin/env python3
"""
Test Server on Port 8080
"""

import requests
import json

def test_port_8080():
    print("🔍 Testing Server on Port 8080")
    print("📍 Testing against: http://localhost:8080")
    
    # Test 1: Basic connection
    print("\n1. Testing Basic Connection")
    try:
        response = requests.get("http://localhost:8080/api/hello", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is accessible on port 8080")
            print(f"📝 Response: {response.json()}")
        else:
            print(f"❌ Backend returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend on port 8080")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Login endpoint
    print("\n2. Testing Login Endpoint")
    try:
        response = requests.post("http://localhost:8080/api/login", 
                               json={"email": "kk@gmail.com", "password": "kk123"},
                               headers={"Content-Type": "application/json"},
                               timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful on port 8080")
            print(f"📝 Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

if __name__ == "__main__":
    success = test_port_8080()
    if success:
        print("\n" + "="*50)
        print("🎉 PORT 8080 TEST SUCCESSFUL!")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ PORT 8080 TEST FAILED!")
        print("="*50) 