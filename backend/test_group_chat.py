import requests
import json

def test_group_chat():
    print("🔍 Testing Group Chat Functionality")
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
    
    # Test 2: Create a trip and group
    try:
        trip_data = {
            "name": "Chat Test Trip",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "Testing group chat functionality"
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
    
    # Test 3: Add member to the group
    try:
        member_data = {
            "email": "member@gmail.com"
        }
        response = requests.post(f"http://localhost:8080/api/trips/{trip_id}/members", headers=owner_headers, json=member_data)
        print(f"📝 Member addition response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Member added to group successfully")
        else:
            print(f"❌ Member addition failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding member: {e}")
    
    # Test 4: Owner sends a message
    try:
        message_data = {
            "message": "Hello everyone! Welcome to our trip chat!"
        }
        response = requests.post(f"http://localhost:8080/api/groups/{group_id}/chat", headers=owner_headers, json=message_data)
        print(f"📝 Owner send message response: {response.status_code}")
        if response.status_code == 201:
            print("✅ Owner sent message successfully")
        else:
            print(f"❌ Owner send message failed: {response.text}")
    except Exception as e:
        print(f"❌ Error sending owner message: {e}")
    
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
    
    # Test 6: Member sends a message
    try:
        message_data = {
            "message": "Hi! Thanks for adding me to the group!"
        }
        response = requests.post(f"http://localhost:8080/api/groups/{group_id}/chat", headers=member_headers, json=message_data)
        print(f"📝 Member send message response: {response.status_code}")
        if response.status_code == 201:
            print("✅ Member sent message successfully")
        else:
            print(f"❌ Member send message failed: {response.text}")
    except Exception as e:
        print(f"❌ Error sending member message: {e}")
    
    # Test 7: Owner gets all messages
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/chat", headers=owner_headers)
        print(f"📝 Owner get messages response: {response.status_code}")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Owner can see {len(messages)} messages:")
            for i, message in enumerate(messages, 1):
                print(f"   Message {i}: {message['message']} (User ID: {message['user_id']})")
        else:
            print(f"❌ Owner get messages failed: {response.text}")
    except Exception as e:
        print(f"❌ Error getting owner messages: {e}")
    
    # Test 8: Member gets all messages
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/chat", headers=member_headers)
        print(f"📝 Member get messages response: {response.status_code}")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Member can see {len(messages)} messages:")
            for i, message in enumerate(messages, 1):
                print(f"   Message {i}: {message['message']} (User ID: {message['user_id']})")
        else:
            print(f"❌ Member get messages failed: {response.text}")
    except Exception as e:
        print(f"❌ Error getting member messages: {e}")
    
    # Test 9: Test non-member access (should be denied)
    try:
        # Create another user
        non_member_data = {
            "name": "Non Member",
            "email": "nonmember2@gmail.com",
            "password": "nonmember123"
        }
        response = requests.post("http://localhost:8080/api/register", json=non_member_data)
        if response.status_code == 200:
            print("✅ Non-member user created")
        else:
            print(f"⚠️ Non-member user creation: {response.status_code} (might already exist)")
        
        # Login as non-member
        non_member_login_data = {
            "email": "nonmember2@gmail.com",
            "password": "nonmember123"
        }
        response = requests.post("http://localhost:8080/api/login", json=non_member_login_data)
        if response.status_code == 200:
            non_member_token = response.json()["access_token"]
            non_member_headers = {"Authorization": f"Bearer {non_member_token}"}
            
            # Try to access chat
            response = requests.get(f"http://localhost:8080/api/groups/{group_id}/chat", headers=non_member_headers)
            print(f"📝 Non-member get messages response: {response.status_code}")
            if response.status_code == 403:
                print("✅ Non-member correctly denied access to chat")
            else:
                print(f"❌ Non-member should be denied access but got: {response.status_code}")
        else:
            print(f"❌ Non-member login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing non-member access: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 GROUP CHAT TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_group_chat() 