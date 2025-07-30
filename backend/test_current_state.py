#!/usr/bin/env python3
"""
Simple Test to Check Current Application State
"""

import requests
import json

def test_current_state():
    print("🔍 Testing Current Application State")
    
    # Test 1: Login
    try:
        login_data = {
            "email": "test@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8080/api/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 2: Check trips
    try:
        response = requests.get("http://localhost:8080/api/trips", headers=headers)
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ Found {len(trips)} trips")
            for i, trip in enumerate(trips):
                print(f"   Trip {i+1}: {trip['name']} (ID: {trip['id']})")
                print(f"      Dates: {trip['start_date']} to {trip['end_date']}")
                print(f"      Description: {trip.get('description', 'No description')}")
                print(f"      Finalized: {trip.get('finalized', False)}")
        else:
            print(f"❌ Failed to get trips: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting trips: {e}")
    
    # Test 3: Check groups for each trip
    if trips:
        for trip in trips:
            try:
                response = requests.get(f"http://localhost:8080/api/trips/{trip['id']}/groups", headers=headers)
                if response.status_code == 200:
                    groups = response.json()
                    print(f"✅ Trip {trip['name']} has {len(groups)} groups")
                    for group in groups:
                        print(f"   Group: {group['name']} (ID: {group['id']})")
                        
                        # Test 4: Check photos for each group
                        try:
                            response = requests.get(f"http://localhost:8080/api/groups/{group['id']}/photos", headers=headers)
                            if response.status_code == 200:
                                photos = response.json()
                                print(f"      Photos: {len(photos)} photos")
                                for photo in photos:
                                    print(f"         - {photo['filename']} (ID: {photo['id']})")
                            else:
                                print(f"      ❌ Failed to get photos: {response.status_code}")
                        except Exception as e:
                            print(f"      ❌ Error getting photos: {e}")
                else:
                    print(f"❌ Failed to get groups for trip {trip['name']}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error getting groups for trip {trip['name']}: {e}")
    
    # Test 5: Check if there are any photos in the uploads/photos directory
    import os
    photos_dir = "uploads/photos"
    if os.path.exists(photos_dir):
        photos_files = os.listdir(photos_dir)
        print(f"✅ Found {len(photos_files)} files in uploads/photos directory")
        for file in photos_files:
            print(f"   - {file}")
    else:
        print("❌ uploads/photos directory does not exist")

if __name__ == "__main__":
    test_current_state() 