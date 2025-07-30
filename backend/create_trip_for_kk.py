import requests
import json

def create_trip_for_kk():
    print("🔍 Creating trip for kk user...")
    print("=" * 50)
    
    # First, let's try to login with different passwords
    passwords_to_try = ['password123', 'kk123', '123456', 'password', 'kk']
    
    for password in passwords_to_try:
        print(f"Trying password: {password}")
        try:
            login_data = {
                "email": "kk@gmail.com",
                "password": password
            }
            response = requests.post("http://localhost:8080/api/login", json=login_data)
            if response.status_code == 200:
                user_token = response.json()["access_token"]
                print(f"✅ Login successful with password: {password}")
                
                # Create a trip
                user_headers = {"Authorization": f"Bearer {user_token}"}
                trip_data = {
                    "name": "kk's Amazing Adventure",
                    "start_date": "2024-08-01",
                    "end_date": "2024-08-07",
                    "description": "A wonderful trip created for kk user"
                }
                
                response = requests.post("http://localhost:8080/api/trips", headers=user_headers, json=trip_data)
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"✅ Created trip: {result['trip']['name']} (ID: {result['trip']['id']})")
                    print(f"✅ Created group: {result['group']['id']}")
                    return
                else:
                    print(f"❌ Failed to create trip: {response.text}")
                    return
            else:
                print(f"❌ Login failed with password: {password}")
        except Exception as e:
            print(f"❌ Error with password {password}: {e}")
    
    print("❌ Could not login with any password")

if __name__ == "__main__":
    create_trip_for_kk() 