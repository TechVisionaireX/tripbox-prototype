#!/usr/bin/env python3
"""
Test script to verify owner functionality and shared features
"""

import requests
import json
import time

# Configuration
BASE_URL = 'https://tripbox-intelliorganizer.onrender.com'

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

def print_section(title):
    """Print section header"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def test_owner_functionality():
    """Test owner functionality and shared features"""
    
    print_section("OWNER FUNCTIONALITY TEST")
    
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
        print("❌ No trips found. Cannot test shared functionality.")
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
        print("❌ No groups found. Cannot test shared functionality.")
        return
    
    # Use the first group
    group = groups[0]
    group_id = group['id']
    print(f"📝 Using group: {group['name']} (ID: {group_id})")
    
    # Step 4: Test Chat Functionality
    print("\n📋 Step 4: Test Chat Functionality")
    
    # Owner sends a message
    print("   📤 Owner sending message...")
    chat_data = {'message': f'Test message from owner at {time.strftime("%H:%M:%S")}'}
    response = test_api_call(f'/api/groups/{group_id}/chat', method='POST', data=chat_data, headers=owner_headers)
    
    if response and response.status_code == 201:
        print("✅ Owner message sent successfully")
    else:
        print(f"❌ Owner failed to send message: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Owner checks messages
    print("   📥 Owner checking messages...")
    response = test_api_call(f'/api/groups/{group_id}/chat', headers=owner_headers)
    if response and response.status_code == 200:
        messages = response.json()
        print(f"✅ Owner can see {len(messages)} messages")
    else:
        print(f"❌ Owner cannot see messages: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Step 5: Test Expenses Functionality
    print("\n📋 Step 5: Test Expenses Functionality")
    
    # Owner adds an expense
    print("   💰 Owner adding expense...")
    expense_data = {
        'amount': 50.00,
        'category': 'Food',
        'description': 'Lunch expense'
    }
    response = test_api_call(f'/api/groups/{group_id}/expenses', method='POST', data=expense_data, headers=owner_headers)
    
    if response and response.status_code == 201:
        print("✅ Owner expense added successfully")
    else:
        print(f"❌ Owner failed to add expense: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Owner checks expenses
    print("   📊 Owner checking expenses...")
    response = test_api_call(f'/api/groups/{group_id}/expenses', headers=owner_headers)
    if response and response.status_code == 200:
        expenses = response.json()
        print(f"✅ Owner can see {len(expenses)} expenses")
    else:
        print(f"❌ Owner cannot see expenses: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Step 6: Test Checklist Functionality
    print("\n📋 Step 6: Test Checklist Functionality")
    
    # Owner adds a packing item
    print("   📦 Owner adding packing item...")
    checklist_data = {
        'type': 'packing',
        'text': 'Passport and documents'
    }
    response = test_api_call(f'/api/groups/{group_id}/checklist-items', method='POST', data=checklist_data, headers=owner_headers)
    
    if response and response.status_code == 201:
        print("✅ Owner packing item added successfully")
    else:
        print(f"❌ Owner failed to add packing item: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Owner checks packing items
    print("   📦 Owner checking packing items...")
    response = test_api_call(f'/api/groups/{group_id}/packing-items', headers=owner_headers)
    if response and response.status_code == 200:
        items = response.json()
        print(f"✅ Owner can see {len(items)} packing items")
    else:
        print(f"❌ Owner cannot see packing items: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Step 7: Test Enhanced Chat
    print("\n📋 Step 7: Test Enhanced Chat Functionality")
    
    # Test enhanced chat endpoint
    print("   📤 Testing enhanced chat...")
    enhanced_chat_data = {
        'message': f'Enhanced test message at {time.strftime("%H:%M:%S")}',
        'type': 'text'
    }
    response = test_api_call(f'/api/groups/{group_id}/chat/enhanced', method='POST', data=enhanced_chat_data, headers=owner_headers)
    
    if response and response.status_code == 201:
        print("✅ Enhanced chat working")
    else:
        print(f"❌ Enhanced chat not working: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    # Step 8: Test Member Addition
    print("\n📋 Step 8: Test Member Addition")
    
    # Try to add a test member
    print("   👥 Testing member addition...")
    add_member_data = {'email': 'test@example.com'}
    response = test_api_call(f'/api/trips/{trip_id}/members', method='POST', data=add_member_data, headers=owner_headers)
    
    if response and response.status_code == 201:
        print("✅ Member addition endpoint working")
    elif response and response.status_code == 404:
        print("✅ Member addition endpoint working (user not found, which is expected)")
    else:
        print(f"❌ Member addition failed: {response.status_code if response else 'No response'}")
        if response:
            print(f"Response: {response.text}")
    
    print_section("TEST COMPLETE")
    print("✅ Owner functionality test completed!")

if __name__ == "__main__":
    test_owner_functionality() 