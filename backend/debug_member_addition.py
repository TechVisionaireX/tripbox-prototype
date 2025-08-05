import requests
import json

def debug_member_addition():
    base_url = 'https://tripbox-intelliorganizer.onrender.com'
    
    # Login as kk
    print("1. Logging in as kk...")
    login_response = requests.post(f'{base_url}/api/login', json={
        'email': 'kk@gmail.com',
        'password': 'kk123'
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print("✅ Login successful")
    
    # Get trips
    print("\n2. Getting trips...")
    trips_response = requests.get(f'{base_url}/api/trips', headers=headers)
    print(f"Trips response: {trips_response.status_code}")
    
    if trips_response.status_code == 200:
        trips = trips_response.json()
        print(f"Found {len(trips)} trips")
        for trip in trips[:3]:  # Show first 3 trips
            print(f"  Trip {trip['id']}: {trip['name']}")
    
    # Test member addition to trip 1
    print(f"\n3. Testing member addition to trip 1...")
    member_response = requests.post(f'{base_url}/api/trips/1/members', 
                                  headers=headers, 
                                  json={'email': 'mem@gmail.com'})
    
    print(f"Member addition response: {member_response.status_code}")
    print(f"Response body: {member_response.text}")
    
    # Test getting trip groups
    print(f"\n4. Testing trip groups for trip 1...")
    groups_response = requests.get(f'{base_url}/api/trips/1/groups', headers=headers)
    print(f"Groups response: {groups_response.status_code}")
    print(f"Groups: {groups_response.text}")

if __name__ == "__main__":
    debug_member_addition() 