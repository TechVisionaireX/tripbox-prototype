import requests
import json

def debug_group_creation():
    base_url = 'http://localhost:5000'
    
    # Step 1: Login
    print("1. Logging in...")
    login_data = {
        'email': 'test@gmail.com',
        'password': 'password123'
    }
    
    try:
        login_response = requests.post(f'{base_url}/api/login', json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access_token')
            print(f"Login successful. Access token: {access_token[:20]}...")
            
            # Step 2: Create a trip first
            print("\n2. Creating trip...")
            trip_data = {
                'name': 'Debug Trip',
                'start_date': '2024-01-01',
                'end_date': '2024-01-05',
                'description': 'Debugging group creation'
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            trip_response = requests.post(f'{base_url}/api/trips', json=trip_data, headers=headers)
            print(f"Trip creation status: {trip_response.status_code}")
            
            if trip_response.status_code == 200:
                trip_result = trip_response.json()
                trip_id = trip_result.get('trip', {}).get('id')
                print(f"Trip created with ID: {trip_id}")
                
                # Step 3: Create a group
                print("\n3. Creating group...")
                group_data = {
                    'name': 'Debug Group',
                    'trip_id': trip_id
                }
                
                group_response = requests.post(f'{base_url}/api/groups', json=group_data, headers=headers)
                print(f"Group creation status: {group_response.status_code}")
                print(f"Group creation response: {group_response.text}")
                
                if group_response.status_code in [200, 201]:
                    group_result = group_response.json()
                    group_id = group_result.get('group', {}).get('id')
                    print(f"✅ Group created with ID: {group_id}")
                else:
                    print("❌ Group creation failed!")
                    
            else:
                print(f"❌ Trip creation failed: {trip_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_group_creation() 