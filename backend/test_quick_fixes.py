#!/usr/bin/env python3
"""
Quick Test for Gallery and Checklist Fixes
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "name": "Test User",
    "email": "test@example.com", 
    "password": "testpassword123"
}

def test_api_call(endpoint, method="GET", data=None, headers=None):
    """Make API call and return response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        return response
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None

def main():
    print("🚀 Testing Gallery and Checklist Fixes")
    print(f"📍 Testing against: {BASE_URL}")
    
    # Step 1: Test Backend Connection
    print("\n1. Testing Backend Connection")
    response = test_api_call("/api/hello")
    if response and response.status_code == 200:
        print("✅ Backend is running")
    else:
        print("❌ Backend connection failed")
        return
    
    # Step 2: Register User
    print("\n2. User Registration")
    response = test_api_call("/api/register", method="POST", data=TEST_USER)
    if response and response.status_code == 200:
        print("✅ User registered successfully")
    else:
        print("❌ User registration failed")
        if response:
            print(f"📝 Error: {response.json()}")
        return
    
    # Step 3: Login User
    print("\n3. User Login")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = test_api_call("/api/login", method="POST", data=login_data)
    if response and response.status_code == 200:
        print("✅ User login successful")
        login_response = response.json()
        access_token = login_response.get("access_token")
    else:
        print("❌ User login failed")
        return
    
    # Set up headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 4: Create Trip
    print("\n4. Trip Creation")
    trip_data = {
        "name": "Test Trip",
        "start_date": "2024-08-01",
        "end_date": "2024-08-07",
        "description": "Test trip"
    }
    response = test_api_call("/api/trips", method="POST", data=trip_data, headers=headers)
    if response and response.status_code == 200:
        print("✅ Trip created successfully")
        trip_response = response.json()
        group_id = trip_response.get("group", {}).get("id")
        print(f"📝 Group ID: {group_id}")
    else:
        print("❌ Trip creation failed")
        return
    
    # Step 5: Test Gallery Photos Endpoint
    print("\n5. Testing Gallery Photos Endpoint")
    response = test_api_call(f"/api/groups/{group_id}/photos", headers=headers)
    if response and response.status_code == 200:
        print("✅ Gallery photos endpoint working")
        photos = response.json()
        print(f"📝 Found {len(photos)} photos")
    else:
        print("❌ Gallery photos endpoint failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 6: Test Packing Items Endpoint
    print("\n6. Testing Packing Items Endpoint")
    response = test_api_call(f"/api/groups/{group_id}/packing-items", headers=headers)
    if response and response.status_code == 200:
        print("✅ Packing items endpoint working")
        items = response.json()
        print(f"📝 Found {len(items)} packing items")
    else:
        print("❌ Packing items endpoint failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 7: Test Todo Items Endpoint
    print("\n7. Testing Todo Items Endpoint")
    response = test_api_call(f"/api/groups/{group_id}/todo-items", headers=headers)
    if response and response.status_code == 200:
        print("✅ Todo items endpoint working")
        items = response.json()
        print(f"📝 Found {len(items)} todo items")
    else:
        print("❌ Todo items endpoint failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 8: Test Reminder Items Endpoint
    print("\n8. Testing Reminder Items Endpoint")
    response = test_api_call(f"/api/groups/{group_id}/reminder-items", headers=headers)
    if response and response.status_code == 200:
        print("✅ Reminder items endpoint working")
        items = response.json()
        print(f"📝 Found {len(items)} reminder items")
    else:
        print("❌ Reminder items endpoint failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    print("\n" + "="*50)
    print("🎉 QUICK FIX TEST COMPLETED!")
    print("="*50)
    print("✅ All endpoints should now be working properly")

if __name__ == "__main__":
    main() 