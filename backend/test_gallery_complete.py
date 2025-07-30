import requests
import os
from pathlib import Path

def test_gallery_complete():
    print("🔍 Testing Complete Gallery Upload Workflow")
    
    # Test 1: Check if uploads/photos directory exists
    uploads_photos_dir = Path("uploads/photos")
    print(f"📁 Uploads photos directory exists: {uploads_photos_dir.exists()}")
    if not uploads_photos_dir.exists():
        print("📁 Creating uploads/photos directory...")
        uploads_photos_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Created uploads/photos directory")
    
    # Test 2: Login to get token
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
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Create a trip
    try:
        trip_data = {
            "name": "Test Trip for Gallery",
            "start_date": "2024-01-15",
            "end_date": "2024-01-20",
            "description": "Testing gallery upload functionality"
        }
        response = requests.post("http://localhost:8080/api/trips", headers=headers, json=trip_data)
        if response.status_code in [200, 201]:
            result = response.json()
            trip = result["trip"]
            trip_id = trip["id"]
            group_id = result["group"]["id"]
            print(f"✅ Created trip: {trip_id}")
            print(f"✅ Created group: {group_id}")
        else:
            print(f"❌ Failed to create trip: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating trip: {e}")
        return
    
    # Test 4: Group already created with trip, using group_id from above
    
    # Test 5: Try to upload a test image
    test_image_path = "uploads/test_image.png"
    if os.path.exists(test_image_path):
        print(f"📸 Found test image: {test_image_path}")
        
        try:
            with open(test_image_path, 'rb') as f:
                files = {'photo': ('test.png', f, 'image/png')}
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
                    result = response.json()
                    print(f"📝 Photo ID: {result['photo']['id']}")
                    print(f"📝 Filename: {result['photo']['filename']}")
                    print(f"📝 URL: {result['photo']['url']}")
                    
                    # Test 6: Try to get the uploaded photos
                    response = requests.get(f"http://localhost:8080/api/groups/{group_id}/photos", headers=headers)
                    if response.status_code == 200:
                        photos = response.json()
                        print(f"✅ Retrieved {len(photos)} photos from gallery")
                        for photo in photos:
                            print(f"   - Photo {photo['id']}: {photo['filename']}")
                    else:
                        print(f"❌ Failed to get photos: {response.status_code}")
                        
                else:
                    print(f"❌ Upload failed: {response.text}")
        except Exception as e:
            print(f"❌ Error during upload: {e}")
    else:
        print(f"❌ Test image not found: {test_image_path}")

if __name__ == "__main__":
    test_gallery_complete() 