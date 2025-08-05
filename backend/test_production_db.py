import requests
import json

def test_production_db():
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
    
    # Test direct group query
    print("\n2. Testing direct group query...")
    groups_response = requests.get(f'{base_url}/api/trips/1/groups', headers=headers)
    print(f"Groups response: {groups_response.status_code}")
    print(f"Groups: {groups_response.text}")
    
    # Test member addition with more debug info
    print(f"\n3. Testing member addition with debug...")
    member_response = requests.post(f'{base_url}/api/trips/1/members', 
                                  headers=headers, 
                                  json={'email': 'mem@gmail.com'})
    
    print(f"Member addition response: {member_response.status_code}")
    print(f"Response body: {member_response.text}")
    
    # Test a different trip
    print(f"\n4. Testing trip 5 (which should have a group)...")
    groups_response_5 = requests.get(f'{base_url}/api/trips/5/groups', headers=headers)
    print(f"Trip 5 groups response: {groups_response_5.status_code}")
    print(f"Trip 5 groups: {groups_response_5.text}")

if __name__ == "__main__":
    test_production_db() 