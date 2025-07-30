import requests
import os
from pathlib import Path

def test_gallery_upload():
    print("🔍 Testing Gallery Upload Functionality")
    
    # Test 1: Check if uploads/photos directory exists
    uploads_photos_dir = Path("uploads/photos")
    print(f"📁 Uploads photos directory exists: {uploads_photos_dir.exists()}")
    if not uploads_photos_dir.exists():
        print("📁 Creating uploads/photos directory...")
        uploads_photos_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Created uploads/photos directory")
    
    # Test 2: Check if we can connect to the backend
    try:
        response = requests.get("http://localhost:8080/api/hello")
        print(f"✅ Backend connection: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return
    
    # Test 3: Try to login to get a token
    try:
        login_data = {
            "email": "test@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8080/api/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login successful, got token")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 4: Check if there are any groups
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get("http://localhost:8080/api/trips", headers=headers)
        if response.status_code == 200:
            trips = response.json()
            print(f"✅ Found {len(trips)} trips")
            if trips:
                trip_id = trips[0]["id"]
                print(f"📝 Using trip ID: {trip_id}")
                
                # Get groups for this trip
                response = requests.get(f"http://localhost:8080/api/trips/{trip_id}/groups", headers=headers)
                if response.status_code == 200:
                    groups = response.json()
                    print(f"✅ Found {len(groups)} groups for trip {trip_id}")
                    if groups:
                        group_id = groups[0]["id"]
                        print(f"📝 Using group ID: {group_id}")
                        
                        # Test 5: Try to upload a test image
                        test_image_path = "uploads/trip.avif"
                        if os.path.exists(test_image_path):
                            print(f"📸 Found test image: {test_image_path}")
                            
                            with open(test_image_path, 'rb') as f:
                                files = {'photo': ('test.avif', f, 'image/avif')}
                                data = {'caption': 'Test upload from script'}
                                
                                response = requests.post(
                                    f"http://localhost:8080/api/groups/{group_id}/photos",
                                    headers=headers,
                                    files=files,
                                    data=data
                                )
                                
                                print(f"📤 Upload response: {response.status_code}")
                                if response.status_code == 201:
                                    print("✅ Upload successful!")
                                    print(f"📝 Response: {response.json()}")
                                else:
                                    print(f"❌ Upload failed: {response.text}")
                        else:
                            print(f"❌ Test image not found: {test_image_path}")
                    else:
                        print("❌ No groups found for trip")
                else:
                    print(f"❌ Failed to get groups: {response.status_code}")
            else:
                print("❌ No trips found")
        else:
            print(f"❌ Failed to get trips: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing groups: {e}")

if __name__ == "__main__":
    test_gallery_upload() 