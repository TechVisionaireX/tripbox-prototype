#!/usr/bin/env python3
"""
Test script for Live Location feature
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_live_location_feature():
    """Test the live location feature"""
    
    print("🧪 Testing Live Location Feature")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("\n1. Logging in...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get user's groups
    print("\n2. Getting user groups...")
    try:
        response = requests.get(f"{BASE_URL}/api/groups", headers=headers)
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ Found {len(groups)} groups")
            if groups:
                group_id = groups[0]['id']
                print(f"   Using group ID: {group_id}")
            else:
                print("❌ No groups found")
                return
        else:
            print(f"❌ Failed to get groups: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting groups: {e}")
        return
    
    # Step 3: Test location update
    print("\n3. Testing location update...")
    location_data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "accuracy": 10.5,
        "speed": 0.0,
        "heading": 0.0,
        "altitude": 10.0,
        "battery_level": 85.0,
        "location_name": "Test Location - New York"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/groups/{group_id}/live-location/update",
            headers=headers,
            json=location_data
        )
        if response.status_code == 201:
            print("✅ Location update successful")
            location_id = response.json().get('location_id')
            print(f"   Location ID: {location_id}")
        else:
            print(f"❌ Location update failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Error updating location: {e}")
        return
    
    # Step 4: Test getting group locations
    print("\n4. Testing get group locations...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/groups/{group_id}/live-location/members",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            print(f"✅ Found {len(locations)} active locations")
            for loc in locations:
                print(f"   User {loc['user_id']}: {loc['latitude']:.6f}, {loc['longitude']:.6f}")
        else:
            print(f"❌ Failed to get locations: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error getting locations: {e}")
    
    # Step 5: Test location history
    print("\n5. Testing location history...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/groups/{group_id}/live-location/history",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            print(f"✅ Found {len(history)} history points")
        else:
            print(f"❌ Failed to get history: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting history: {e}")
    
    # Step 6: Test distance calculation
    print("\n6. Testing distance calculation...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/groups/{group_id}/live-location/distance",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            distances = data.get('distances', [])
            print(f"✅ Calculated {len(distances)} distances")
            for dist in distances:
                print(f"   User {dist['user1_id']} to User {dist['user2_id']}: {dist['distance_km']} km")
        else:
            print(f"❌ Failed to calculate distances: {response.status_code}")
    except Exception as e:
        print(f"❌ Error calculating distances: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Live Location Feature Test Complete!")
    print("\nTo test the frontend:")
    print("1. Start the backend server: python app.py")
    print("2. Open frontend/live-location.html in your browser")
    print("3. Log in and select a trip group")
    print("4. Click 'Start Sharing Location' to test the feature")

if __name__ == "__main__":
    test_live_location_feature() 