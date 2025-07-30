import requests
import os

def test_checklist_member_access():
    print("🔍 Testing Checklist Member Access")
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
            "name": "Checklist Test Trip",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "Testing checklist member access"
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
    
    # Test 5: Add checklist items as owner
    try:
        checklist_items = [
            {"text": "Passport", "type": "packing"},
            {"text": "Book flight tickets", "type": "todo"},
            {"text": "Check weather forecast", "type": "reminder"}
        ]
        
        for item in checklist_items:
            response = requests.post(f"http://localhost:8080/api/groups/{group_id}/checklist-items", 
                                  headers=owner_headers, json=item)
            print(f"📝 Added {item['type']} item: {response.status_code}")
            if response.status_code == 201:
                print(f"✅ Added {item['text']} to {item['type']}")
            else:
                print(f"❌ Failed to add {item['text']}: {response.text}")
    except Exception as e:
        print(f"❌ Error adding checklist items: {e}")
    
    # Test 6: Login as member
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
    
    # Test 7: Check if member can see checklist items
    try:
        # Get packing items
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/packing-items", headers=member_headers)
        if response.status_code == 200:
            packing_items = response.json()
            print(f"✅ Member can see {len(packing_items)} packing items")
            for item in packing_items:
                print(f"   - {item['text']} (completed: {item.get('completed', False)})")
        else:
            print(f"❌ Member cannot see packing items: {response.status_code}")
        
        # Get todo items
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/todo-items", headers=member_headers)
        if response.status_code == 200:
            todo_items = response.json()
            print(f"✅ Member can see {len(todo_items)} todo items")
            for item in todo_items:
                print(f"   - {item['text']} (completed: {item.get('completed', False)})")
        else:
            print(f"❌ Member cannot see todo items: {response.status_code}")
        
        # Get reminder items
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/reminder-items", headers=member_headers)
        if response.status_code == 200:
            reminder_items = response.json()
            print(f"✅ Member can see {len(reminder_items)} reminder items")
            for item in reminder_items:
                print(f"   - {item['text']} (completed: {item.get('completed', False)})")
        else:
            print(f"❌ Member cannot see reminder items: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking member checklist access: {e}")
    
    # Test 8: Test if member can update checklist items
    try:
        # Try to update a packing item (use the first item from the response)
        if packing_items:
            item_id = packing_items[0]['id']
            response = requests.post(f"http://localhost:8080/api/packing-items/{item_id}/toggle-complete", 
                                  headers=member_headers)
            print(f"📝 Member update packing item response: {response.status_code}")
            if response.status_code == 200:
                print("✅ Member can update checklist items")
            else:
                print(f"❌ Member cannot update checklist items: {response.text}")
        else:
            print("⚠️ No packing items to test update")
    except Exception as e:
        print(f"❌ Error testing member checklist update: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 CHECKLIST MEMBER ACCESS TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_checklist_member_access() 