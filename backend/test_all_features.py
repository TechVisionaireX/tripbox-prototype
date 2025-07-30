#!/usr/bin/env python3
"""
Comprehensive test script for all TripBox features
Tests: Login, Trips, Groups, Expenses, Gallery, Checklists
"""

import requests
import json
import os

# Configuration
API_BASE = "http://localhost:5000"
TEST_EMAIL = "test@gmail.com"
TEST_PASSWORD = "password123"

def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def test_api_call(endpoint, method="GET", data=None, headers=None):
    """Make API call and return response"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - Is the server running on {API_BASE}?")
        return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_login():
    """Test user login and get access token"""
    print_section("LOGIN TEST")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = test_api_call("/api/login", method="POST", data=login_data)
    
    if not response:
        return None
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        print(f"✅ Login successful - Token: {access_token[:20]}...")
        return access_token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_trips(access_token):
    """Test trip creation and retrieval"""
    print_section("TRIPS TEST")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create a test trip
    trip_data = {
        "name": "Test Trip for Features",
        "start_date": "2024-06-01",
        "end_date": "2024-06-07",
        "description": "Testing all features"
    }
    
    response = test_api_call("/api/trips", method="POST", data=trip_data, headers=headers)
    
    if response and response.status_code == 200:
        data = response.json()
        trip_id = data.get('trip', {}).get('id')
        print(f"✅ Trip created - ID: {trip_id}")
        
        # Get trips
        response = test_api_call("/api/trips", headers=headers)
        if response and response.status_code == 200:
            trips = response.json()
            print(f"✅ Retrieved {len(trips)} trips")
            return trip_id
        else:
            print(f"❌ Failed to get trips: {response.status_code if response else 'No response'}")
    else:
        print(f"❌ Failed to create trip: {response.status_code if response else 'No response'}")
    
    return None

def test_groups(access_token, trip_id):
    """Test group creation and management"""
    print_section("GROUPS TEST")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create a test group
    group_data = {
        "name": "Test Group",
        "trip_id": trip_id
    }
    
    response = test_api_call("/api/groups", method="POST", data=group_data, headers=headers)
    
    if response and response.status_code == 201:
        data = response.json()
        group_id = data.get('group', {}).get('id')
        print(f"✅ Group created - ID: {group_id}")
        
        # Get user's groups
        response = test_api_call("/api/groups", headers=headers)
        if response and response.status_code == 200:
            groups = response.json()
            print(f"✅ Retrieved {len(groups)} groups")
            return group_id
        else:
            print(f"❌ Failed to get groups: {response.status_code if response else 'No response'}")
    else:
        print(f"❌ Failed to create group: {response.status_code if response else 'No response'}")
    
    return None

def test_expenses(access_token, group_id):
    """Test expense creation and management"""
    print_section("EXPENSES TEST")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add an expense
    expense_data = {
        "amount": 25.50,
        "category": "Food",
        "description": "Dinner at Italian restaurant"
    }
    
    response = test_api_call(f"/api/groups/{group_id}/expenses", method="POST", data=expense_data, headers=headers)
    
    if response and response.status_code == 201:
        data = response.json()
        expense_id = data.get('expense', {}).get('id')
        print(f"✅ Expense added - ID: {expense_id}")
        
        # Get expenses
        response = test_api_call(f"/api/groups/{group_id}/expenses", headers=headers)
        if response and response.status_code == 200:
            expenses = response.json()
            print(f"✅ Retrieved {len(expenses)} expenses")
            
            # Get expense split
            response = test_api_call(f"/api/groups/{group_id}/expenses/split", headers=headers)
            if response and response.status_code == 200:
                split_data = response.json()
                print(f"✅ Expense split calculated - Total: ${split_data.get('total_expense', 0)}")
            else:
                print(f"❌ Failed to get expense split: {response.status_code if response else 'No response'}")
        else:
            print(f"❌ Failed to get expenses: {response.status_code if response else 'No response'}")
    else:
        print(f"❌ Failed to add expense: {response.status_code if response else 'No response'}")

def test_gallery(access_token, group_id):
    """Test photo gallery functionality"""
    print_section("GALLERY TEST")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get photos (should be empty initially)
    response = test_api_call(f"/api/groups/{group_id}/photos", headers=headers)
    
    if response and response.status_code == 200:
        photos = response.json()
        print(f"✅ Retrieved {len(photos)} photos from gallery")
    else:
        print(f"❌ Failed to get photos: {response.status_code if response else 'No response'}")

def test_checklists(access_token, group_id):
    """Test checklist functionality"""
    print_section("CHECKLISTS TEST")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add a packing item
    packing_data = {
        "type": "packing",
        "text": "Passport"
    }
    
    response = test_api_call(f"/api/groups/{group_id}/checklist-items", method="POST", data=packing_data, headers=headers)
    
    if response and response.status_code == 201:
        data = response.json()
        item_id = data.get('item', {}).get('id')
        print(f"✅ Packing item added - ID: {item_id}")
        
        # Get packing items
        response = test_api_call(f"/api/groups/{group_id}/packing-items", headers=headers)
        if response and response.status_code == 200:
            items = response.json()
            print(f"✅ Retrieved {len(items)} packing items")
        else:
            print(f"❌ Failed to get packing items: {response.status_code if response else 'No response'}")
    else:
        print(f"❌ Failed to add packing item: {response.status_code if response else 'No response'}")
    
    # Add a todo item
    todo_data = {
        "type": "todo",
        "text": "Book flight tickets"
    }
    
    response = test_api_call(f"/api/groups/{group_id}/checklist-items", method="POST", data=todo_data, headers=headers)
    
    if response and response.status_code == 201:
        data = response.json()
        item_id = data.get('item', {}).get('id')
        print(f"✅ Todo item added - ID: {item_id}")
        
        # Get todo items
        response = test_api_call(f"/api/groups/{group_id}/todo-items", headers=headers)
        if response and response.status_code == 200:
            items = response.json()
            print(f"✅ Retrieved {len(items)} todo items")
        else:
            print(f"❌ Failed to get todo items: {response.status_code if response else 'No response'}")
    else:
        print(f"❌ Failed to add todo item: {response.status_code if response else 'No response'}")

def main():
    """Run all tests"""
    print("🚀 Starting TripBox Feature Tests")
    print(f"📡 API Base: {API_BASE}")
    
    # Test login
    access_token = test_login()
    if not access_token:
        print("❌ Cannot proceed without valid access token")
        return
    
    # Test trips
    trip_id = test_trips(access_token)
    if not trip_id:
        print("❌ Cannot proceed without valid trip")
        return
    
    # Test groups
    group_id = test_groups(access_token, trip_id)
    if not group_id:
        print("❌ Cannot proceed without valid group")
        return
    
    # Test all features
    test_expenses(access_token, group_id)
    test_gallery(access_token, group_id)
    test_checklists(access_token, group_id)
    
    print_section("TEST COMPLETE")
    print("✅ All feature tests completed!")
    print("📝 Check the output above for any errors")

if __name__ == "__main__":
    main() 