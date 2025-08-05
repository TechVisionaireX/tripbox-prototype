import requests
import json

def test_fix_groups():
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
    
    # Call the fix groups endpoint
    print("\n2. Calling fix groups endpoint...")
    fix_response = requests.post(f'{base_url}/api/fix-missing-groups', headers=headers)
    print(f"Fix response: {fix_response.status_code}")
    print(f"Fix response body: {fix_response.text}")
    
    if fix_response.status_code == 200:
        fix_data = fix_response.json()
        print(f"✅ Fixed {len(fix_data.get('fixed_trips', []))} trips")
        
        # Test member addition again
        print(f"\n3. Testing member addition after fix...")
        member_response = requests.post(f'{base_url}/api/trips/1/members', 
                                      headers=headers, 
                                      json={'email': 'mem@gmail.com'})
        
        print(f"Member addition response: {member_response.status_code}")
        print(f"Member addition response: {member_response.text}")
        
        # Test groups endpoint
        print(f"\n4. Testing groups endpoint after fix...")
        groups_response = requests.get(f'{base_url}/api/trips/1/groups', headers=headers)
        print(f"Groups response: {groups_response.status_code}")
        print(f"Groups: {groups_response.text}")

if __name__ == "__main__":
    test_fix_groups() 