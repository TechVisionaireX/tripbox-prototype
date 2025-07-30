import requests
import json

def test_trip_creation():
    base_url = 'http://localhost:5000'
    
    # Step 1: Login to get access token
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
            
            # Step 2: Create a trip
            print("\n2. Creating trip...")
            trip_data = {
                'name': 'Test Trip Creation',
                'start_date': '2024-01-01',
                'end_date': '2024-01-05',
                'description': 'Testing trip creation functionality'
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            trip_response = requests.post(f'{base_url}/api/trips', json=trip_data, headers=headers)
            print(f"Trip creation status: {trip_response.status_code}")
            print(f"Trip creation response: {trip_response.text}")
            
            if trip_response.status_code == 200:
                print("✅ Trip creation successful!")
                trip_result = trip_response.json()
                print(f"Created trip ID: {trip_result.get('trip', {}).get('id')}")
                print(f"Created group ID: {trip_result.get('group', {}).get('id')}")
            else:
                print("❌ Trip creation failed!")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_trip_creation() 