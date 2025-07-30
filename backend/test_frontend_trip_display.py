import requests
import json

def test_frontend_trip_display():
    print("🔍 Testing Frontend Trip Display")
    print("=" * 50)
    
    # Test 1: Login as the user from the screenshot (kk@gmail.com)
    try:
        login_data = {
            "email": "kk@gmail.com",
            "password": "password123"  # Assuming default password
        }
        response = requests.post("http://localhost:8080/api/login", json=login_data)
        if response.status_code == 200:
            user_token = response.json()["access_token"]
            print("✅ User login successful")
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ User login error: {e}")
        return
    
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test 2: Get trips for this user
    try:
        response = requests.get("http://localhost:8080/api/trips", headers=user_headers)
        print(f"📝 Get trips response: {response.status_code}")
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ User can see {len(trips)} trips")
            for i, trip in enumerate(trips, 1):
                print(f"   Trip {i}: {trip['name']} (ID: {trip['id']})")
                print(f"      Owner: {trip.get('is_owner', 'Unknown')}")
                print(f"      Role: {trip.get('role', 'Unknown')}")
                print(f"      Dates: {trip['start_date']} to {trip['end_date']}")
        else:
            print(f"❌ Failed to get trips: {response.text}")
    except Exception as e:
        print(f"❌ Error getting trips: {e}")
    
    # Test 3: Check if user exists and has trips
    try:
        # Try to get user profile
        response = requests.get("http://localhost:8080/api/profile", headers=user_headers)
        print(f"📝 Get profile response: {response.status_code}")
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ User profile: {profile}")
        else:
            print(f"❌ Failed to get profile: {response.text}")
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
    
    # Test 4: Try with test user to compare
    try:
        test_login_data = {
            "email": "test@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8080/api/login", json=test_login_data)
        if response.status_code == 200:
            test_token = response.json()["access_token"]
            test_headers = {"Authorization": f"Bearer {test_token}"}
            
            response = requests.get("http://localhost:8080/api/trips", headers=test_headers)
            print(f"📝 Test user get trips response: {response.status_code}")
            if response.status_code == 200:
                trips = response.json()
                print(f"✅ Test user can see {len(trips)} trips")
                for i, trip in enumerate(trips[:3], 1):  # Show first 3
                    print(f"   Trip {i}: {trip['name']} (ID: {trip['id']})")
                    print(f"      Owner: {trip.get('is_owner', 'Unknown')}")
                    print(f"      Role: {trip.get('role', 'Unknown')}")
            else:
                print(f"❌ Test user failed to get trips: {response.text}")
        else:
            print(f"❌ Test user login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing with test user: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 FRONTEND TRIP DISPLAY TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_frontend_trip_display() 