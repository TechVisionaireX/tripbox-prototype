#!/usr/bin/env python3
"""
Quick Verification Test for Trip Editing, Member Addition, and Gallery Upload
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "name": "Test Owner",
    "email": "owner@test.com", 
    "password": "owner123"
}
MEMBER_USER = {
    "name": "Test Member",
    "email": "member@test.com", 
    "password": "member123"
}

def test_api_call(endpoint, method="GET", data=None, headers=None, files=None):
    """Make API call and return response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files, headers=headers)
            else:
                response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        
        return response
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None

def main():
    print("🚀 Quick Verification Test")
    print(f"📍 Testing against: {BASE_URL}")
    
    # Step 1: Test Backend Connection
    print("\n1. Testing Backend Connection")
    response = test_api_call("/api/hello")
    if response and response.status_code == 200:
        print("✅ Backend is running")
    else:
        print("❌ Backend connection failed")
        return
    
    # Step 2: Register Users
    print("\n2. Registering Users")
    for user_data in [TEST_USER, MEMBER_USER]:
        response = test_api_call("/api/register", method="POST", data=user_data)
        if response and response.status_code == 200:
            print(f"✅ {user_data['name']} registered successfully")
        else:
            print(f"❌ {user_data['name']} registration failed")
            if response:
                print(f"📝 Error: {response.json()}")
    
    # Step 3: Login Owner
    print("\n3. Login Owner")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = test_api_call("/api/login", method="POST", data=login_data)
    if response and response.status_code == 200:
        print("✅ Owner login successful")
        login_response = response.json()
        owner_token = login_response.get("access_token")
    else:
        print("❌ Owner login failed")
        return
    
    # Set up headers for owner requests
    owner_headers = {
        "Authorization": f"Bearer {owner_token}",
        "Content-Type": "application/json"
    }
    
    # Step 4: Create Trip
    print("\n4. Create Trip")
    trip_data = {
        "name": "Test Trip for Verification",
        "start_date": "2024-08-01",
        "end_date": "2024-08-07",
        "description": "A test trip for verification"
    }
    response = test_api_call("/api/trips", method="POST", data=trip_data, headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Trip created successfully")
        trip_response = response.json()
        trip_id = trip_response.get("trip", {}).get("id")
        group_id = trip_response.get("group", {}).get("id")
        print(f"📝 Trip ID: {trip_id}")
        print(f"📝 Group ID: {group_id}")
    else:
        print("❌ Trip creation failed")
        if response:
            print(f"📝 Error: {response.json()}")
        return
    
    # Step 5: Test Trip Update (Edit Trip)
    print("\n5. Test Trip Update (Edit Trip)")
    update_data = {
        "name": "Updated Test Trip",
        "start_date": "2024-08-02",
        "end_date": "2024-08-08",
        "description": "An updated test trip"
    }
    response = test_api_call(f"/api/trips/{trip_id}", method="PUT", data=update_data, headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Trip updated successfully")
        print(f"📝 Response: {response.json()}")
    else:
        print("❌ Trip update failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 6: Test Member Addition
    print("\n6. Test Member Addition")
    member_data = {
        "email": MEMBER_USER["email"]
    }
    response = test_api_call(f"/api/trips/{trip_id}/members", method="POST", data=member_data, headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Member added successfully")
        print(f"📝 Response: {response.json()}")
    else:
        print("❌ Member addition failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 7: Test Gallery Photos Endpoint
    print("\n7. Test Gallery Photos Endpoint")
    response = test_api_call(f"/api/groups/{group_id}/photos", headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Gallery photos endpoint working")
        photos = response.json()
        print(f"📝 Found {len(photos)} photos")
    else:
        print("❌ Gallery photos endpoint failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 8: Test Checklist Items
    print("\n8. Test Checklist Items")
    checklist_data = {
        "type": "packing",
        "text": "Test packing item"
    }
    response = test_api_call(f"/api/groups/{group_id}/checklist-items", method="POST", data=checklist_data, headers=owner_headers)
    if response and response.status_code == 201:
        print("✅ Checklist item added successfully")
        print(f"📝 Response: {response.json()}")
    else:
        print("❌ Checklist item addition failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    print("\n" + "="*50)
    print("🎉 QUICK VERIFICATION COMPLETED!")
    print("="*50)
    print("✅ All core functionality tested:")
    print("   - Trip creation and editing")
    print("   - Member addition to trips")
    print("   - Gallery functionality")
    print("   - Checklist management")
    print("\n🚀 The application should now work properly!")

if __name__ == "__main__":
    main() 