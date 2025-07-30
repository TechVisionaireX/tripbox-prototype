import requests
import json

def test_kk_user():
    print("🔍 Testing kk user")
    print("=" * 50)
    
    # Test 1: Login as kk user
    try:
        login_data = {
            "email": "kk@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8080/api/login", json=login_data)
        if response.status_code == 200:
            user_token = response.json()["access_token"]
            print("✅ kk user login successful")
        else:
            print(f"❌ kk user login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ kk user login error: {e}")
        return
    
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test 2: Get trips for kk user
    try:
        response = requests.get("http://localhost:8080/api/trips", headers=user_headers)
        print(f"📝 Get trips response: {response.status_code}")
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ kk user can see {len(trips)} trips")
            for i, trip in enumerate(trips, 1):
                print(f"   Trip {i}: {trip['name']} (ID: {trip['id']})")
                print(f"      Owner: {trip.get('is_owner', 'Unknown')}")
                print(f"      Role: {trip.get('role', 'Unknown')}")
                print(f"      Dates: {trip['start_date']} to {trip['end_date']}")
        else:
            print(f"❌ Failed to get trips: {response.text}")
    except Exception as e:
        print(f"❌ Error getting trips: {e}")
    
    # Test 3: Create a trip for kk user
    try:
        trip_data = {
            "name": "kk's First Trip",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "A test trip for kk user"
        }
        response = requests.post("http://localhost:8080/api/trips", headers=user_headers, json=trip_data)
        print(f"📝 Create trip response: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Created trip: {result['trip']['name']} (ID: {result['trip']['id']})")
        else:
            print(f"❌ Failed to create trip: {response.text}")
    except Exception as e:
        print(f"❌ Error creating trip: {e}")
    
    # Test 4: Get trips again to see if the new trip appears
    try:
        response = requests.get("http://localhost:8080/api/trips", headers=user_headers)
        print(f"📝 Get trips after creation response: {response.status_code}")
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ kk user can now see {len(trips)} trips")
            for i, trip in enumerate(trips, 1):
                print(f"   Trip {i}: {trip['name']} (ID: {trip['id']})")
                print(f"      Owner: {trip.get('is_owner', 'Unknown')}")
                print(f"      Role: {trip.get('role', 'Unknown')}")
        else:
            print(f"❌ Failed to get trips after creation: {response.text}")
    except Exception as e:
        print(f"❌ Error getting trips after creation: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 KK USER TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_kk_user() 