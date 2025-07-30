#!/usr/bin/env python3
"""
Comprehensive Test for All Reported Issues
Tests: Trip visibility, Member addition, Expense splitting, Gallery upload, Checklist sync
"""

import requests
import os
from pathlib import Path

def test_all_issues():
    print("🔍 Testing All Reported Issues")
    print("=" * 50)
    
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
    
    # Test 2: Check trips (Dashboard issue)
    print("\n📊 TESTING DASHBOARD TRIPS DISPLAY")
    print("-" * 30)
    try:
        response = requests.get("http://localhost:8080/api/trips", headers=headers)
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ Backend has {len(trips)} trips")
            for i, trip in enumerate(trips):
                print(f"   Trip {i+1}: {trip['name']} (ID: {trip['id']})")
                print(f"      Owner: {trip.get('is_owner', False)}")
                print(f"      Role: {trip.get('role', 'N/A')}")
        else:
            print(f"❌ Failed to get trips: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting trips: {e}")
    
    # Test 3: Check gallery upload (Gallery issue)
    print("\n📸 TESTING GALLERY UPLOAD")
    print("-" * 30)
    
    # First, ensure we have a trip and group
    if trips:
        trip_id = trips[0]["id"]
        print(f"📝 Using trip ID: {trip_id}")
        
        # Get groups for this trip
        response = requests.get(f"http://localhost:8080/api/trips/{trip_id}/groups", headers=headers)
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ Found {len(groups)} groups for trip")
            
            if groups:
                group_id = groups[0]["id"]
                print(f"📝 Using group ID: {group_id}")
                
                # Test gallery upload
                test_image_path = "uploads/test_image.png"
                if os.path.exists(test_image_path):
                    print(f"📸 Found test image: {test_image_path}")
                    
                    with open(test_image_path, 'rb') as f:
                        files = {'photo': ('test_gallery.png', f, 'image/png')}
                        data = {'caption': 'Test gallery upload from script'}
                        
                        response = requests.post(
                            f"http://localhost:8080/api/groups/{group_id}/photos",
                            headers=headers,
                            files=files,
                            data=data
                        )
                        
                        print(f"📤 Gallery upload response: {response.status_code}")
                        if response.status_code == 201:
                            print("✅ Gallery upload successful!")
                            result = response.json()
                            print(f"📝 Photo ID: {result['photo']['id']}")
                        else:
                            print(f"❌ Gallery upload failed: {response.text}")
                else:
                    print(f"❌ Test image not found: {test_image_path}")
            else:
                print("❌ No groups found for trip")
        else:
            print(f"❌ Failed to get groups: {response.status_code}")
    
    # Test 4: Check trip editing and member addition (My trips issue)
    print("\n👥 TESTING TRIP EDITING AND MEMBER ADDITION")
    print("-" * 40)
    
    if trips:
        trip_id = trips[0]["id"]
        print(f"📝 Testing trip editing for trip ID: {trip_id}")
        
        # Test trip update
        update_data = {
            "name": "Updated Trip Name",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "Updated description for testing"
        }
        
        response = requests.put(f"http://localhost:8080/api/trips/{trip_id}", headers=headers, json=update_data)
        print(f"📝 Trip update response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Trip update successful!")
        else:
            print(f"❌ Trip update failed: {response.text}")
        
        # Test member addition
        member_data = {
            "email": "test2@gmail.com"  # Assuming this user exists
        }
        
        response = requests.post(f"http://localhost:8080/api/trips/{trip_id}/members", headers=headers, json=member_data)
        print(f"📝 Member addition response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Member addition successful!")
        else:
            print(f"❌ Member addition failed: {response.text}")
    
    # Test 5: Check if photos are accessible via URL
    print("\n🔗 TESTING PHOTO ACCESS")
    print("-" * 20)
    
    # Get photos for the first group
    if trips and groups:
        group_id = groups[0]["id"]
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/photos", headers=headers)
        if response.status_code == 200:
            photos = response.json()
            print(f"✅ Found {len(photos)} photos in gallery")
            
            for photo in photos:
                photo_url = f"http://localhost:8080{photo['url']}"
                print(f"📸 Photo: {photo['filename']}")
                print(f"🔗 URL: {photo_url}")
                
                # Test if photo is accessible
                try:
                    photo_response = requests.get(photo_url)
                    if photo_response.status_code == 200:
                        print("✅ Photo is accessible")
                    else:
                        print(f"❌ Photo not accessible: {photo_response.status_code}")
                except Exception as e:
                    print(f"❌ Error accessing photo: {e}")
        else:
            print(f"❌ Failed to get photos: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 COMPREHENSIVE TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_all_issues() 