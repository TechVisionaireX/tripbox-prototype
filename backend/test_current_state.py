#!/usr/bin/env python3
"""
Simple Test to Check Current Application State
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api_call(endpoint, method="GET", data=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        
        return response
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None

def main():
    print("🔍 Checking Current Application State")
    print(f"📍 Testing against: {BASE_URL}")
    
    # Test 1: Backend Connection
    print("\n1. Testing Backend Connection")
    response = test_api_call("/api/hello")
    if response and response.status_code == 200:
        print("✅ Backend is running")
    else:
        print("❌ Backend connection failed")
        return
    
    # Test 2: Login with existing user
    print("\n2. Testing Login")
    login_data = {
        "email": "kk@gmail.com",
        "password": "kk123"
    }
    response = test_api_call("/api/login", method="POST", data=login_data)
    if response and response.status_code == 200:
        print("✅ Login successful")
        login_response = response.json()
        token = login_response.get("access_token")
    else:
        print("❌ Login failed")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 3: Get Trips
    print("\n3. Testing Get Trips")
    response = test_api_call("/api/trips", headers=headers)
    if response and response.status_code == 200:
        trips = response.json()
        print(f"✅ Found {len(trips)} trips")
        for trip in trips:
            print(f"   - {trip['name']} (ID: {trip['id']}) - Owner: {trip.get('is_owner', False)}")
    else:
        print("❌ Failed to get trips")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Test 4: Get Trip Groups (for first trip)
    if trips:
        trip_id = trips[0]['id']
        print(f"\n4. Testing Get Trip Groups for Trip {trip_id}")
        response = test_api_call(f"/api/trips/{trip_id}/groups", headers=headers)
        if response and response.status_code == 200:
            groups = response.json()
            print(f"✅ Found {len(groups)} groups")
            for group in groups:
                print(f"   - {group['name']} (ID: {group['id']}) - Members: {group.get('member_count', 0)}")
        else:
            print("❌ Failed to get trip groups")
            if response:
                print(f"📝 Error: {response.json()}")
    
    # Test 5: Test Member Addition (if user is owner)
    if trips and trips[0].get('is_owner'):
        trip_id = trips[0]['id']
        print(f"\n5. Testing Member Addition for Trip {trip_id}")
        member_data = {
            "email": "test@example.com"
        }
        response = test_api_call(f"/api/trips/{trip_id}/members", method="POST", data=member_data, headers=headers)
        if response and response.status_code == 200:
            print("✅ Member addition successful")
            print(f"📝 Response: {response.json()}")
        else:
            print("❌ Member addition failed")
            if response:
                print(f"📝 Error: {response.json()}")
    else:
        print("\n5. Skipping Member Addition Test (user is not trip owner)")
    
    # Test 6: Test Trip Update (if user is owner)
    if trips and trips[0].get('is_owner'):
        trip_id = trips[0]['id']
        print(f"\n6. Testing Trip Update for Trip {trip_id}")
        update_data = {
            "name": "Updated Trip Name",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "Updated description"
        }
        response = test_api_call(f"/api/trips/{trip_id}", method="PUT", data=update_data, headers=headers)
        if response and response.status_code == 200:
            print("✅ Trip update successful")
            print(f"📝 Response: {response.json()}")
        else:
            print("❌ Trip update failed")
            if response:
                print(f"📝 Error: {response.json()}")
    else:
        print("\n6. Skipping Trip Update Test (user is not trip owner)")
    
    print("\n" + "="*50)
    print("🎉 CURRENT STATE CHECK COMPLETED!")
    print("="*50)

if __name__ == "__main__":
    main() 