#!/usr/bin/env python3
"""
Test script to check enhanced chat functionality locally
"""

import requests
import json
import time

# Configuration
BASE_URL = 'http://localhost:5000'  # Test locally first

# Test user
OWNER_EMAIL = 'kk@gmail.com'
OWNER_PASSWORD = 'kk123'

def test_api_call(endpoint, method='GET', data=None, headers=None):
    """Make API call and return response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None

def login_user(email, password):
    """Login user and return access token"""
    print(f"🔐 Logging in user: {email}")
    
    login_data = {
        'email': email,
        'password': password
    }
    
    response = test_api_call('/api/login', method='POST', data=login_data)
    
    if response and response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        print(f"✅ Login successful for {email}")
        return access_token
    else:
        print(f"❌ Login failed for {email}: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
        return None

def test_enhanced_chat():
    """Test enhanced chat functionality"""
    
    print("🔍 TESTING ENHANCED CHAT FUNCTIONALITY")
    
    # Step 1: Login owner
    print("\n📋 Step 1: Login Owner")
    owner_token = login_user(OWNER_EMAIL, OWNER_PASSWORD)
    
    if not owner_token:
        print("❌ Failed to login owner. Cannot proceed with test.")
        return
    
    owner_headers = {'Authorization': f'Bearer {owner_token}'}
    
    # Step 2: Get trips
    print("\n📋 Step 2: Get Owner's Trips")
    response = test_api_call('/api/trips', headers=owner_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get owner's trips")
        return
    
    trips = response.json()
    print(f"✅ Owner has {len(trips)} trips")
    
    if not trips:
        print("❌ No trips found. Cannot test enhanced chat.")
        return
    
    # Use the first trip
    trip = trips[0]
    trip_id = trip['id']
    print(f"📝 Using trip: {trip['name']} (ID: {trip_id})")
    
    # Step 3: Get groups for the trip
    print("\n📋 Step 3: Get Trip Groups")
    response = test_api_call(f'/api/trips/{trip_id}/groups', headers=owner_headers)
    if not response or response.status_code != 200:
        print("❌ Failed to get trip groups")
        return
    
    groups = response.json()
    print(f"✅ Found {len(groups)} groups for trip")
    
    if not groups:
        print("❌ No groups found. Cannot test enhanced chat.")
        return
    
    # Use the first group
    group = groups[0]
    group_id = group['id']
    print(f"📝 Using group: {group['name']} (ID: {group_id})")
    
    # Step 4: Test Enhanced Chat
    print("\n📋 Step 4: Test Enhanced Chat Functionality")
    
    # Test enhanced chat endpoint
    print("   📤 Testing enhanced chat...")
    enhanced_chat_data = {
        'message': f'Enhanced test message at {time.strftime("%H:%M:%S")}',
        'type': 'text'
    }
    response = test_api_call(f'/api/groups/{group_id}/chat/enhanced', method='POST', data=enhanced_chat_data, headers=owner_headers)
    
    if response and response.status_code == 201:
        print("✅ Enhanced chat working")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Enhanced chat not working: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Step 5: Test Member Addition
    print("\n📋 Step 5: Test Member Addition")
    
    # Try to add a test member
    print("   👥 Testing member addition...")
    add_member_data = {'email': 'test@example.com'}
    response = test_api_call(f'/api/trips/{trip_id}/members', method='POST', data=add_member_data, headers=owner_headers)
    
    if response and response.status_code == 201:
        print("✅ Member addition working (201 status)")
    elif response and response.status_code == 404:
        print("✅ Member addition working (404 - user not found, which is expected)")
    else:
        print(f"❌ Member addition failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    print("\n✅ Enhanced chat test completed!")

if __name__ == "__main__":
    test_enhanced_chat() 