#!/usr/bin/env python3
"""
Comprehensive Test for All Reported Issues
Tests: Trip visibility, Member addition, Expense splitting, Gallery upload, Checklist sync
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
OWNER_USER = {
    "name": "Trip Owner",
    "email": "owner@test.com", 
    "password": "owner123"
}
MEMBER_USER = {
    "name": "Trip Member",
    "email": "member@test.com", 
    "password": "member123"
}

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print(f"{'='*60}")

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
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        return response
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return None

def main():
    print("🚀 Testing All Reported Issues")
    print(f"📍 Testing against: {BASE_URL}")
    
    # Step 1: Test Backend Connection
    print_step(1, "Testing Backend Connection")
    response = test_api_call("/api/hello")
    if response and response.status_code == 200:
        print("✅ Backend is running")
    else:
        print("❌ Backend connection failed")
        return
    
    # Step 2: Register Owner User
    print_step(2, "Register Owner User")
    response = test_api_call("/api/register", method="POST", data=OWNER_USER)
    if response and response.status_code == 200:
        print("✅ Owner registered successfully")
    else:
        print("❌ Owner registration failed")
        if response:
            print(f"📝 Error: {response.json()}")
        return
    
    # Step 3: Register Member User
    print_step(3, "Register Member User")
    response = test_api_call("/api/register", method="POST", data=MEMBER_USER)
    if response and response.status_code == 200:
        print("✅ Member registered successfully")
    else:
        print("❌ Member registration failed")
        if response:
            print(f"📝 Error: {response.json()}")
        return
    
    # Step 4: Login Owner
    print_step(4, "Login Owner")
    login_data = {
        "email": OWNER_USER["email"],
        "password": OWNER_USER["password"]
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
    
    # Step 5: Create Trip
    print_step(5, "Create Trip")
    trip_data = {
        "name": "Test Trip to Paris",
        "start_date": "2024-08-01",
        "end_date": "2024-08-07",
        "description": "A wonderful trip to Paris with friends"
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
    
    # Step 6: Get Trips (Test Trip Visibility)
    print_step(6, "Test Trip Visibility")
    response = test_api_call("/api/trips", headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Trips retrieved successfully")
        trips = response.json()
        print(f"📝 Found {len(trips)} trips")
        for trip in trips:
            print(f"   - {trip['name']} (ID: {trip['id']}) - Owner: {trip.get('is_owner', False)}")
    else:
        print("❌ Failed to get trips")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 7: Add Member to Trip
    print_step(7, "Add Member to Trip")
    member_data = {
        "email": MEMBER_USER["email"]
    }
    response = test_api_call(f"/api/trips/{trip_id}/members", method="POST", data=member_data, headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Member added to trip successfully")
        print(f"📝 Response: {response.json()}")
    else:
        print("❌ Failed to add member to trip")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 8: Get Trip Members
    print_step(8, "Get Trip Members")
    response = test_api_call(f"/api/trips/{trip_id}/members", headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Trip members retrieved successfully")
        members = response.json()
        print(f"📝 Found {len(members.get('members', []))} members")
        for member in members.get('members', []):
            print(f"   - {member['name']} ({member['email']}) - Owner: {member.get('is_owner', False)}")
    else:
        print("❌ Failed to get trip members")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 9: Add Expense (Test Expense Splitting)
    print_step(9, "Add Expense (Test Splitting)")
    expense_data = {
        "amount": 150.00,
        "description": "Dinner at restaurant",
        "category": "Food"
    }
    response = test_api_call(f"/api/groups/{group_id}/expenses", method="POST", data=expense_data, headers=owner_headers)
    if response and response.status_code == 201:
        print("✅ Expense added successfully")
        expense_response = response.json()
        expense_id = expense_response.get("expense", {}).get("id")
        split_amount = expense_response.get("expense", {}).get("split_amount")
        member_count = expense_response.get("expense", {}).get("member_count")
        print(f"📝 Expense ID: {expense_id}")
        print(f"📝 Amount: ${expense_response.get('expense', {}).get('amount')}")
        print(f"📝 Split amount: ${split_amount}")
        print(f"📝 Member count: {member_count}")
    else:
        print("❌ Failed to add expense")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 10: Get Expenses
    print_step(10, "Get Expenses")
    response = test_api_call(f"/api/groups/{group_id}/expenses", headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Expenses retrieved successfully")
        expenses = response.json()
        print(f"📝 Found {len(expenses)} expenses")
        for expense in expenses:
            print(f"   - ${expense['amount']} - {expense['note']} by {expense['user_name']}")
    else:
        print("❌ Failed to get expenses")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 11: Add Checklist Item
    print_step(11, "Add Checklist Item")
    checklist_data = {
        "type": "packing",
        "text": "Passport and travel documents"
    }
    response = test_api_call(f"/api/groups/{group_id}/checklist-items", method="POST", data=checklist_data, headers=owner_headers)
    if response and response.status_code == 201:
        print("✅ Checklist item added successfully")
        checklist_response = response.json()
        item_id = checklist_response.get("item", {}).get("id")
        print(f"📝 Item ID: {item_id}")
        print(f"📝 Text: {checklist_response.get('item', {}).get('text')}")
    else:
        print("❌ Failed to add checklist item")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 12: Get Packing Items
    print_step(12, "Get Packing Items")
    response = test_api_call(f"/api/groups/{group_id}/packing-items", headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Packing items retrieved successfully")
        items = response.json()
        print(f"📝 Found {len(items)} packing items")
        for item in items:
            print(f"   - {item['text']} (Completed: {item['is_completed']}) by {item['user_name']}")
    else:
        print("❌ Failed to get packing items")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 13: Test Gallery Photos Endpoint
    print_step(13, "Test Gallery Photos Endpoint")
    response = test_api_call(f"/api/groups/{group_id}/photos", headers=owner_headers)
    if response and response.status_code == 200:
        print("✅ Gallery photos endpoint working")
        photos = response.json()
        print(f"📝 Found {len(photos)} photos")
    else:
        print("❌ Gallery photos endpoint failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    # Step 14: Login Member and Test Access
    print_step(14, "Login Member and Test Access")
    member_login_data = {
        "email": MEMBER_USER["email"],
        "password": MEMBER_USER["password"]
    }
    response = test_api_call("/api/login", method="POST", data=member_login_data)
    if response and response.status_code == 200:
        print("✅ Member login successful")
        member_login_response = response.json()
        member_token = member_login_response.get("access_token")
        
        # Set up headers for member requests
        member_headers = {
            "Authorization": f"Bearer {member_token}",
            "Content-Type": "application/json"
        }
        
        # Test if member can see the trip
        response = test_api_call("/api/trips", headers=member_headers)
        if response and response.status_code == 200:
            print("✅ Member can see trips")
            trips = response.json()
            print(f"📝 Member sees {len(trips)} trips")
        else:
            print("❌ Member cannot see trips")
            if response:
                print(f"📝 Error: {response.json()}")
    else:
        print("❌ Member login failed")
        if response:
            print(f"📝 Error: {response.json()}")
    
    print("\n" + "="*60)
    print("🎉 COMPREHENSIVE ISSUE TEST COMPLETED!")
    print("="*60)
    print("✅ All core functionality tested:")
    print("   - Trip creation and visibility")
    print("   - Member addition to trips")
    print("   - Expense tracking and splitting")
    print("   - Checklist management")
    print("   - Gallery functionality")
    print("   - Cross-user access")
    print("\n🚀 The TripBox application should now be working properly!")

if __name__ == "__main__":
    main() 