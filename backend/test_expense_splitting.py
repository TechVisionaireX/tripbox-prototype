import requests
import json

def test_expense_splitting():
    print("🔍 Testing Expense Splitting and Display")
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
    
    # Test 2: Create a new trip for testing
    try:
        trip_data = {
            "name": "Expense Test Trip",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "Testing expense splitting functionality"
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
    
    # Test 3: Add member to the trip
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
    
    # Test 4: Owner adds an expense
    try:
        expense_data = {
            "amount": 200.0,
            "description": "Hotel booking",
            "category": "Accommodation"
        }
        response = requests.post(f"http://localhost:8080/api/groups/{group_id}/expenses", headers=owner_headers, json=expense_data)
        print(f"📝 Owner expense addition response: {response.status_code}")
        if response.status_code == 201:
            expense_result = response.json()
            print(f"✅ Owner added expense: ${expense_result['expense']['amount']} - {expense_result['expense']['note']}")
            print(f"   Split amount per member: ${expense_result['expense']['split_amount']}")
            print(f"   Total members: {expense_result['expense']['member_count']}")
        else:
            print(f"❌ Owner expense addition failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding owner expense: {e}")
    
    # Test 5: Login as member
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
    
    # Test 6: Member adds an expense
    try:
        expense_data = {
            "amount": 150.0,
            "description": "Food and drinks",
            "category": "Food"
        }
        response = requests.post(f"http://localhost:8080/api/groups/{group_id}/expenses", headers=member_headers, json=expense_data)
        print(f"📝 Member expense addition response: {response.status_code}")
        if response.status_code == 201:
            expense_result = response.json()
            print(f"✅ Member added expense: ${expense_result['expense']['amount']} - {expense_result['expense']['note']}")
            print(f"   Split amount per member: ${expense_result['expense']['split_amount']}")
            print(f"   Total members: {expense_result['expense']['member_count']}")
        else:
            print(f"❌ Member expense addition failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding member expense: {e}")
    
    # Test 7: Check expense summary for owner
    try:
        response = requests.get(f"http://localhost:8080/api/trips/{trip_id}/expenses/summary", headers=owner_headers)
        print(f"📝 Owner expense summary response: {response.status_code}")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Owner expense summary:")
            print(f"   Total expenses: ${summary.get('total_expense', 0)}")
            print(f"   Split per member: ${summary.get('split_per_member', 0)}")
            print(f"   Total members: {summary.get('member_count', 0)}")
        else:
            print(f"❌ Owner expense summary failed: {response.text}")
    except Exception as e:
        print(f"❌ Error getting owner expense summary: {e}")
    
    # Test 8: Check expense summary for member
    try:
        response = requests.get(f"http://localhost:8080/api/trips/{trip_id}/expenses/summary", headers=member_headers)
        print(f"📝 Member expense summary response: {response.status_code}")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Member expense summary:")
            print(f"   Total expenses: ${summary.get('total_expense', 0)}")
            print(f"   Split per member: ${summary.get('split_per_member', 0)}")
            print(f"   Total members: {summary.get('member_count', 0)}")
        else:
            print(f"❌ Member expense summary failed: {response.text}")
    except Exception as e:
        print(f"❌ Error getting member expense summary: {e}")
    
    # Test 9: Check all expenses in group (owner view)
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/expenses", headers=owner_headers)
        print(f"📝 Owner get expenses response: {response.status_code}")
        if response.status_code == 200:
            expenses = response.json()
            print(f"✅ Owner can see {len(expenses)} expenses:")
            for expense in expenses:
                print(f"   - ${expense['amount']} ({expense['category']}) by {expense['user_name']}: {expense['note']}")
        else:
            print(f"❌ Owner get expenses failed: {response.text}")
    except Exception as e:
        print(f"❌ Error getting owner expenses: {e}")
    
    # Test 10: Check all expenses in group (member view)
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/expenses", headers=member_headers)
        print(f"📝 Member get expenses response: {response.status_code}")
        if response.status_code == 200:
            expenses = response.json()
            print(f"✅ Member can see {len(expenses)} expenses:")
            for expense in expenses:
                print(f"   - ${expense['amount']} ({expense['category']}) by {expense['user_name']}: {expense['note']}")
        else:
            print(f"❌ Member get expenses failed: {response.text}")
    except Exception as e:
        print(f"❌ Error getting member expenses: {e}")
    
    # Test 11: Test expense splitting calculation
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/expenses/split", headers=owner_headers)
        print(f"📝 Expense split calculation response: {response.status_code}")
        if response.status_code == 200:
            split_data = response.json()
            print(f"✅ Expense split calculation:")
            print(f"   Total expenses: ${split_data.get('total_expense', 0)}")
            print(f"   Split per member: ${split_data.get('split_per_member', 0)}")
            print(f"   Member count: {split_data.get('member_count', 0)}")
        else:
            print(f"❌ Expense split calculation failed: {response.text}")
    except Exception as e:
        print(f"❌ Error calculating expense split: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 EXPENSE SPLITTING TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_expense_splitting() 