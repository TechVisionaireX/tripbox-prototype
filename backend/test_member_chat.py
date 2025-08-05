import requests
import json

# Test member addition and chat functionality
def test_member_chat():
    base_url = 'https://tripbox-intelliorganizer.onrender.com'
    
    # Step 1: Login as user 1
    print("Step 1: Logging in as user 1...")
    login_response = requests.post(f'{base_url}/api/login', json={
        'email': 'kk@gmail.com',
        'password': 'kk123'
    })
    
    print(f"Login response status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    login_data = login_response.json()
    token1 = login_data['access_token']
    headers1 = {'Authorization': f'Bearer {token1}', 'Content-Type': 'application/json'}
    
    print(f"User 1 logged in: {login_data['user']['name']}")
    
    # Step 2: Get trips for user 1
    print("\nStep 2: Getting trips...")
    trips_response = requests.get(f'{base_url}/api/trips', headers=headers1)
    print(f"Trips response status: {trips_response.status_code}")
    
    if trips_response.status_code != 200:
        print(f"Failed to get trips: {trips_response.text}")
        return
    
    trips_data = trips_response.json()
    if not trips_data:
        print("No trips found")
        return
    
    trip_id = trips_data[0]['id']
    print(f"Using trip ID: {trip_id}")
    
    # Step 3: Add user 2 as member
    print(f"\nStep 3: Adding user 2 as member to trip {trip_id}...")
    member_response = requests.post(f'{base_url}/api/trips/{trip_id}/members', 
                                  headers=headers1, 
                                  json={'email': 'mem@gmail.com'})
    
    print(f"Member addition response status: {member_response.status_code}")
    print(f"Member addition response: {member_response.text}")
    
    if member_response.status_code != 200:
        print("Member addition failed")
        return
    
    # Step 4: Get trip members
    print(f"\nStep 4: Getting trip members...")
    members_response = requests.get(f'{base_url}/api/trips/{trip_id}/members', headers=headers1)
    print(f"Members response status: {members_response.status_code}")
    print(f"Members: {members_response.json()}")
    
    # Step 5: Login as user 2
    print(f"\nStep 5: Logging in as user 2...")
    login2_response = requests.post(f'{base_url}/api/login', json={
        'email': 'mem@gmail.com',
        'password': 'member123'
    })
    
    print(f"User 2 login response status: {login2_response.status_code}")
    if login2_response.status_code != 200:
        print(f"User 2 login failed: {login2_response.text}")
        return
    
    login2_data = login2_response.json()
    token2 = login2_data['access_token']
    headers2 = {'Authorization': f'Bearer {token2}', 'Content-Type': 'application/json'}
    
    print(f"User 2 logged in: {login2_data['user']['name']}")
    
    # Step 6: Get groups for user 2
    print(f"\nStep 6: Getting groups for user 2...")
    groups_response = requests.get(f'{base_url}/api/groups', headers=headers2)
    print(f"Groups response status: {groups_response.status_code}")
    print(f"Groups: {groups_response.json()}")
    
    # Step 7: Send a chat message as user 1
    print(f"\nStep 7: Sending chat message as user 1...")
    # First get the default group for the trip
    trip_groups_response = requests.get(f'{base_url}/api/trips/{trip_id}/groups', headers=headers1)
    print(f"Trip groups response status: {trip_groups_response.status_code}")
    
    if trip_groups_response.status_code == 200:
        trip_groups = trip_groups_response.json()
        if trip_groups:
            group_id = trip_groups[0]['id']
            print(f"Using group ID: {group_id}")
            
            # Send chat message
            chat_response = requests.post(f'{base_url}/api/groups/{group_id}/chat', 
                                        headers=headers1, 
                                        json={'message': 'Hello from user 1!'})
            
            print(f"Chat response status: {chat_response.status_code}")
            print(f"Chat response: {chat_response.text}")
            
            # Step 8: Check notifications for user 2
            print(f"\nStep 8: Checking notifications for user 2...")
            notifications_response = requests.get(f'{base_url}/api/notifications', headers=headers2)
            print(f"Notifications response status: {notifications_response.status_code}")
            print(f"Notifications: {notifications_response.json()}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_member_chat() 