import requests
import json

def test_groups_direct():
    base_url = 'http://localhost:5000'
    
    # Login
    login_data = {
        'email': 'test@gmail.com',
        'password': 'password123'
    }
    
    login_response = requests.post(f'{base_url}/api/login', json=login_data)
    access_token = login_response.json()['access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Create trip
    trip_data = {
        'name': 'Direct Test Trip',
        'start_date': '2024-01-01',
        'end_date': '2024-01-05',
        'description': 'Direct test'
    }
    
    trip_response = requests.post(f'{base_url}/api/trips', json=trip_data, headers=headers)
    trip_id = trip_response.json()['trip']['id']
    
    # Create group
    group_data = {
        'name': 'Direct Test Group',
        'trip_id': trip_id
    }
    
    group_response = requests.post(f'{base_url}/api/groups', json=group_data, headers=headers)
    
    print(f"Status Code: {group_response.status_code}")
    print(f"Response Headers: {dict(group_response.headers)}")
    print(f"Response Text: {group_response.text}")
    
    try:
        response_json = group_response.json()
        print(f"Response JSON: {json.dumps(response_json, indent=2)}")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")

if __name__ == "__main__":
    test_groups_direct() 