import requests
import json

def test_frontend_connection():
    base_url = 'http://localhost:5000'
    
    print("Testing frontend-backend connection...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f'{base_url}/')
        print(f"✅ Server is running (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return
    
    # Test 2: Login
    print("\n2. Testing login...")
    login_data = {
        'email': 'test@gmail.com',
        'password': 'password123'
    }
    
    try:
        login_response = requests.post(f'{base_url}/api/login', json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access_token')
            print(f"✅ Login successful")
            
            # Test 3: Create trip via API
            print("\n3. Testing trip creation...")
            trip_data = {
                'name': 'Frontend Test Trip',
                'start_date': '2024-01-01',
                'end_date': '2024-01-05',
                'description': 'Testing frontend connection'
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            trip_response = requests.post(f'{base_url}/api/trips', json=trip_data, headers=headers)
            if trip_response.status_code == 200:
                print("✅ Trip creation successful!")
                trip_result = trip_response.json()
                print(f"   Trip ID: {trip_result.get('trip', {}).get('id')}")
                print(f"   Group ID: {trip_result.get('group', {}).get('id')}")
                
                # Test 4: Get trips
                print("\n4. Testing get trips...")
                trips_response = requests.get(f'{base_url}/api/trips', headers=headers)
                if trips_response.status_code == 200:
                    trips_result = trips_response.json()
                    print(f"✅ Retrieved {len(trips_result)} trips")
                    for trip in trips_result:
                        print(f"   - {trip.get('name')} (ID: {trip.get('id')})")
                else:
                    print(f"❌ Failed to get trips: {trips_response.text}")
            else:
                print(f"❌ Trip creation failed: {trip_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_frontend_connection() 