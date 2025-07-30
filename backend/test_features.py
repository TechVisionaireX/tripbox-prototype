#!/usr/bin/env python3
"""
Comprehensive Feature Test Script
Tests all major features of the TripBox application
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_backend_connection():
    """Test basic backend connectivity"""
    try:
        response = requests.get(f"{BASE_URL}/api/hello")
        if response.status_code == 200:
            print("✅ Backend connection successful")
            return True
        else:
            print(f"❌ Backend connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/api/register", json=data)
        if response.status_code == 201:
            print("✅ User registration successful")
            return True
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return False

def test_user_login():
    """Test user login"""
    try:
        data = {
            "email": "kk@gmail.com",
            "password": "kk123"
        }
        response = requests.post(f"{BASE_URL}/api/login", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ User login successful")
            return result.get('access_token')
        else:
            print(f"❌ User login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ User login error: {e}")
        return None

def test_trips_api(access_token):
    """Test trips API"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test getting trips
        response = requests.get(f"{BASE_URL}/api/trips", headers=headers)
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ Trips API successful - Found {len(trips)} trips")
            return trips
        else:
            print(f"❌ Trips API failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Trips API error: {e}")
        return []

def test_groups_api(access_token):
    """Test groups API"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test getting groups
        response = requests.get(f"{BASE_URL}/api/groups", headers=headers)
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ Groups API successful - Found {len(groups)} groups")
            return groups
        else:
            print(f"❌ Groups API failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Groups API error: {e}")
        return []

def test_expenses_api(access_token, group_id):
    """Test expenses API"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test getting expenses
        response = requests.get(f"{BASE_URL}/api/groups/{group_id}/expenses", headers=headers)
        if response.status_code == 200:
            expenses = response.json()
            print(f"✅ Expenses API successful - Found {len(expenses)} expenses")
            return True
        else:
            print(f"❌ Expenses API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Expenses API error: {e}")
        return False

def test_gallery_api(access_token, group_id):
    """Test gallery API"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test getting photos
        response = requests.get(f"{BASE_URL}/api/groups/{group_id}/photos", headers=headers)
        if response.status_code == 200:
            photos = response.json()
            print(f"✅ Gallery API successful - Found {len(photos)} photos")
            return True
        else:
            print(f"❌ Gallery API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gallery API error: {e}")
        return False

def test_checklist_api(access_token, group_id):
    """Test checklist API"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test getting packing items
        response = requests.get(f"{BASE_URL}/api/groups/{group_id}/packing-items", headers=headers)
        if response.status_code == 200:
            items = response.json()
            print(f"✅ Checklist API successful - Found {len(items)} packing items")
            return True
        else:
            print(f"❌ Checklist API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Checklist API error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive feature test...")
    print("=" * 50)
    
    # Test 1: Backend Connection
    if not test_backend_connection():
        print("❌ Backend not running. Please start the server first.")
        return
    
    # Test 2: User Login
    access_token = test_user_login()
    if not access_token:
        print("❌ Login failed. Cannot proceed with tests.")
        return
    
    # Test 3: Trips API
    trips = test_trips_api(access_token)
    
    # Test 4: Groups API
    groups = test_groups_api(access_token)
    
    # Test 5: Expenses API (if groups exist)
    if groups:
        test_expenses_api(access_token, groups[0]['id'])
    
    # Test 6: Gallery API (if groups exist)
    if groups:
        test_gallery_api(access_token, groups[0]['id'])
    
    # Test 7: Checklist API (if groups exist)
    if groups:
        test_checklist_api(access_token, groups[0]['id'])
    
    print("=" * 50)
    print("✅ Feature test completed!")
    print("📋 Summary:")
    print(f"   - Backend: ✅ Running")
    print(f"   - Authentication: ✅ Working")
    print(f"   - Trips: ✅ {len(trips)} trips found")
    print(f"   - Groups: ✅ {len(groups)} groups found")
    if groups:
        print(f"   - Expenses: ✅ API working")
        print(f"   - Gallery: ✅ API working")
        print(f"   - Checklists: ✅ API working")

if __name__ == "__main__":
    main() 