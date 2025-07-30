#!/usr/bin/env python3
"""
Test Frontend Connection Issues
"""

import requests
import json

def test_frontend_requests():
    print("🔍 Testing Frontend Connection Issues")
    print("📍 Testing against: http://localhost:5000")
    
    # Test 1: Simulate frontend login request
    print("\n1. Testing Login Request (Frontend Style)")
    try:
        response = requests.post("http://localhost:5000/api/login", 
                               json={"email": "kk@gmail.com", "password": "kk123"},
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        print(f"📝 Status: {response.status_code}")
        print(f"📝 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful")
            print(f"📝 Response keys: {list(data.keys())}")
            return data.get('access_token')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    
    # Test 2: Test CORS headers
    print("\n2. Testing CORS Headers")
    try:
        response = requests.options("http://localhost:5000/api/login", timeout=5)
        print(f"📝 CORS Status: {response.status_code}")
        print(f"📝 CORS Headers: {dict(response.headers)}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS headers present")
        else:
            print("❌ CORS headers missing")
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    # Test 3: Test with different origins
    print("\n3. Testing Different Origins")
    origins_to_test = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:8000",
        "file://"
    ]
    
    for origin in origins_to_test:
        try:
            response = requests.post("http://localhost:5000/api/login", 
                                   json={"email": "kk@gmail.com", "password": "kk123"},
                                   headers={
                                       "Content-Type": "application/json",
                                       "Origin": origin
                                   },
                                   timeout=5)
            print(f"📝 Origin {origin}: Status {response.status_code}")
        except Exception as e:
            print(f"📝 Origin {origin}: Error {e}")

def test_browser_simulation():
    print("\n" + "="*50)
    print("🌐 BROWSER SIMULATION")
    print("="*50)
    
    # Simulate browser fetch request
    print("\n4. Simulating Browser Fetch Request")
    try:
        response = requests.post("http://localhost:5000/api/login", 
                               json={"email": "kk@gmail.com", "password": "kk123"},
                               headers={
                                   "Content-Type": "application/json",
                                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                   "Accept": "application/json",
                                   "Accept-Language": "en-US,en;q=0.9",
                                   "Accept-Encoding": "gzip, deflate, br",
                                   "Connection": "keep-alive"
                               },
                               timeout=10)
        
        print(f"📝 Browser Simulation Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Browser simulation successful")
            return data.get('access_token')
        else:
            print(f"❌ Browser simulation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Browser simulation error: {e}")
        return None

if __name__ == "__main__":
    token = test_frontend_requests()
    if token:
        print(f"\n✅ Got access token: {token[:20]}...")
    
    browser_token = test_browser_simulation()
    if browser_token:
        print(f"\n✅ Got browser token: {browser_token[:20]}...")
    
    print("\n" + "="*50)
    print("🎉 FRONTEND CONNECTION TEST COMPLETED!")
    print("="*50) 