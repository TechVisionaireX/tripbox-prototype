import requests
import os
from pathlib import Path

def test_integration_issues():
    print("🔍 Testing Integration Issues")
    print("=" * 50)
    
    # Test 1: Login as owner
    try:
        login_data = {
            "email": "test@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8080/api/login", json=login_data)
        if response.status_code == 200:
            owner_token = response.json()["access_token"]
            print("✅ Owner login successful")
        else:
            print(f"❌ Owner login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Owner login error: {e}")
        return
    
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    
    # Test 2: Create a test member user
    try:
        member_data = {
            "name": "Test Member",
            "email": "member@gmail.com",
            "password": "member123"
        }
        response = requests.post("http://localhost:8080/api/register", json=member_data)
        if response.status_code == 200:
            print("✅ Member user created")
        else:
            print(f"⚠️ Member user creation: {response.status_code} (might already exist)")
    except Exception as e:
        print(f"❌ Member user creation error: {e}")
    
    # Test 3: Create a trip as owner
    try:
        trip_data = {
            "name": "Integration Test Trip",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "Testing integration issues"
        }
        response = requests.post("http://localhost:8080/api/trips", headers=owner_headers, json=trip_data)
        if response.status_code in [200, 201]:
            result = response.json()
            trip_id = result["trip"]["id"]
            group_id = result["group"]["id"]
            print(f"✅ Created trip: {trip_id}")
            print(f"✅ Created group: {group_id}")
        else:
            print(f"❌ Failed to create trip: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating trip: {e}")
        return
    
    # Test 4: Add member to the trip
    try:
        member_data = {
            "email": "member@gmail.com"
        }
        response = requests.post(f"http://localhost:8080/api/trips/{trip_id}/members", headers=owner_headers, json=member_data)
        print(f"📝 Member addition response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Member added to trip successfully")
        else:
            print(f"❌ Member addition failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding member: {e}")
    
    # Test 5: Login as member and check access
    try:
        member_login_data = {
            "email": "member@gmail.com",
            "password": "member123"
        }
        response = requests.post("http://localhost:8080/api/login", json=member_login_data)
        if response.status_code == 200:
            member_token = response.json()["access_token"]
            print("✅ Member login successful")
        else:
            print(f"❌ Member login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Member login error: {e}")
        return
    
    member_headers = {"Authorization": f"Bearer {member_token}"}
    
    # Test 6: Check if member can see the trip
    try:
        response = requests.get("http://localhost:8080/api/trips", headers=member_headers)
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ Member can see {len(trips)} trips")
            for trip in trips:
                print(f"   - {trip['name']} (Role: {trip.get('role', 'N/A')})")
        else:
            print(f"❌ Member cannot see trips: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking member trips: {e}")
    
    # Test 7: Add expense as owner
    try:
        expense_data = {
            "amount": 150.00,
            "description": "Dinner at restaurant",
            "category": "Food"
        }
        response = requests.post(f"http://localhost:8080/api/groups/{group_id}/expenses", headers=owner_headers, json=expense_data)
        print(f"📝 Expense addition response: {response.status_code}")
        if response.status_code == 201:
            print("✅ Expense added successfully")
            expense_result = response.json()
            print(f"   Amount: ${expense_result['expense']['amount']}")
            print(f"   Split amount: ${expense_result['expense']['split_amount']}")
            print(f"   Member count: {expense_result['expense']['member_count']}")
        else:
            print(f"❌ Expense addition failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding expense: {e}")
    
    # Test 8: Check expense splitting
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/expenses/split", headers=owner_headers)
        if response.status_code == 200:
            split_result = response.json()
            print("✅ Expense splitting working")
            print(f"   Total expense: ${split_result['total_expense']}")
            print(f"   Member count: {split_result['member_count']}")
            print(f"   Split per member: ${split_result['split_per_member']}")
        else:
            print(f"❌ Expense splitting failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking expense splitting: {e}")
    
    # Test 9: Check if member can see expenses
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/expenses", headers=member_headers)
        if response.status_code == 200:
            expenses = response.json()
            print(f"✅ Member can see {len(expenses)} expenses")
            for expense in expenses:
                print(f"   - ${expense['amount']} ({expense['category']}) by {expense['user_name']}")
        else:
            print(f"❌ Member cannot see expenses: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking member expenses: {e}")
    
    # Test 10: Test gallery upload
    try:
        test_image_path = "uploads/test_image.png"
        if os.path.exists(test_image_path):
            with open(test_image_path, 'rb') as f:
                files = {'photo': ('test_integration.png', f, 'image/png')}
                data = {'caption': 'Integration test upload'}
                
                response = requests.post(
                    f"http://localhost:8080/api/groups/{group_id}/photos",
                    headers=owner_headers,
                    files=files,
                    data=data
                )
                
                print(f"📤 Gallery upload response: {response.status_code}")
                if response.status_code == 201:
                    print("✅ Gallery upload successful")
                else:
                    print(f"❌ Gallery upload failed: {response.text}")
        else:
            print("❌ Test image not found")
    except Exception as e:
        print(f"❌ Error testing gallery upload: {e}")
    
    # Test 11: Check if member can see photos
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/photos", headers=member_headers)
        if response.status_code == 200:
            photos = response.json()
            print(f"✅ Member can see {len(photos)} photos")
            for photo in photos:
                print(f"   - {photo['filename']} by {photo['user_name']}")
        else:
            print(f"❌ Member cannot see photos: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking member photos: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 INTEGRATION TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_integration_issues() 