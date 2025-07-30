import requests
import json

def test_user_trip_display():
    print("🔍 Testing User Trip Display")
    print("=" * 50)
    
    # Test 1: Login as test user (we know this exists)
    try:
        login_data = {
            "email": "test@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8080/api/login", json=login_data)
        if response.status_code == 200:
            user_token = response.json()["access_token"]
            print("✅ Test user login successful")
        else:
            print(f"❌ Test user login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Test user login error: {e}")
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
                print(f"      Description: {trip.get('description', 'No description')}")
        else:
            print(f"❌ Failed to get trips: {response.text}")
    except Exception as e:
        print(f"❌ Error getting trips: {e}")
    
    # Test 3: Check if user has any trips they own
    try:
        owned_trips = [trip for trip in trips if trip.get('is_owner', False)]
        print(f"📊 User owns {len(owned_trips)} trips")
        for i, trip in enumerate(owned_trips, 1):
            print(f"   Owned Trip {i}: {trip['name']} (ID: {trip['id']})")
    except Exception as e:
        print(f"❌ Error analyzing owned trips: {e}")
    
    # Test 4: Check if user is a member of any trips
    try:
        member_trips = [trip for trip in trips if not trip.get('is_owner', False)]
        print(f"📊 User is a member of {len(member_trips)} trips")
        for i, trip in enumerate(member_trips, 1):
            print(f"   Member Trip {i}: {trip['name']} (ID: {trip['id']})")
    except Exception as e:
        print(f"❌ Error analyzing member trips: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 USER TRIP DISPLAY TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_user_trip_display() 