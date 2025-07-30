import requests
import os

def test_gallery_member_access():
    print("🔍 Testing Gallery Member Access")
    print("=" * 50)
    
    # Test 1: Login as owner
    try:
        login_data = {
            "email": "test@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8080/api/login", json=login_data)
        if response.status_code == 200:
            owner_token = response.json()["access_token"]
            print("✅ Owner login successful")
        else:
            print(f"❌ Owner login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Owner login error: {e}")
        return
    
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    
    # Test 2: Create a test member user
    try:
        member_data = {
            "name": "Test Member",
            "email": "member@gmail.com",
            "password": "member123"
        }
        response = requests.post("http://localhost:8080/api/register", json=member_data)
        if response.status_code == 200:
            print("✅ Member user created")
        else:
            print(f"⚠️ Member user creation: {response.status_code} (might already exist)")
    except Exception as e:
        print(f"❌ Member user creation error: {e}")
    
    # Test 3: Create a trip as owner
    try:
        trip_data = {
            "name": "Gallery Test Trip",
            "start_date": "2024-08-01",
            "end_date": "2024-08-07",
            "description": "Testing gallery member access"
        }
        response = requests.post("http://localhost:8080/api/trips", headers=owner_headers, json=trip_data)
        if response.status_code in [200, 201]:
            result = response.json()
            trip_id = result["trip"]["id"]
            group_id = result["group"]["id"]
            print(f"✅ Created trip: {trip_id}")
            print(f"✅ Created group: {group_id}")
        else:
            print(f"❌ Failed to create trip: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating trip: {e}")
        return
    
    # Test 4: Add member to the trip
    try:
        member_data = {
            "email": "member@gmail.com"
        }
        response = requests.post(f"http://localhost:8080/api/trips/{trip_id}/members", headers=owner_headers, json=member_data)
        print(f"📝 Member addition response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Member added to trip successfully")
        else:
            print(f"❌ Member addition failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding member: {e}")
    
    # Test 5: Owner uploads a photo
    try:
        # Create a test image file
        test_image_path = "uploads/test_owner_photo.png"
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        
        # Create a simple test image (1x1 pixel PNG)
        with open(test_image_path, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\x27\xe8\x04\x00\x00\x00\x00IEND\xaeB`\x82')
        
        print(f"📸 Created test image: {test_image_path}")
        
        # Upload photo as owner
        with open(test_image_path, "rb") as f:
            files = {"photo": ("test_owner_photo.png", f, "image/png")}
            data = {"caption": "Photo uploaded by owner"}
            response = requests.post(f"http://localhost:8080/api/groups/{group_id}/photos", 
                                  headers=owner_headers, files=files, data=data)
        
        print(f"📝 Owner photo upload response: {response.status_code}")
        if response.status_code == 201:
            owner_photo_result = response.json()
            print(f"✅ Owner uploaded photo: {owner_photo_result['photo']['filename']}")
        else:
            print(f"❌ Owner photo upload failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error uploading owner photo: {e}")
        return
    
    # Test 6: Login as member
    try:
        member_login_data = {
            "email": "member@gmail.com",
            "password": "member123"
        }
        response = requests.post("http://localhost:8080/api/login", json=member_login_data)
        if response.status_code == 200:
            member_token = response.json()["access_token"]
            print("✅ Member login successful")
        else:
            print(f"❌ Member login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Member login error: {e}")
        return
    
    member_headers = {"Authorization": f"Bearer {member_token}"}
    
    # Test 7: Member uploads a photo
    try:
        # Create another test image file
        test_image_path2 = "uploads/test_member_photo.png"
        
        # Create a simple test image (1x1 pixel PNG)
        with open(test_image_path2, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\x27\xe8\x04\x00\x00\x00\x00IEND\xaeB`\x82')
        
        print(f"📸 Created test image: {test_image_path2}")
        
        # Upload photo as member
        with open(test_image_path2, "rb") as f:
            files = {"photo": ("test_member_photo.png", f, "image/png")}
            data = {"caption": "Photo uploaded by member"}
            response = requests.post(f"http://localhost:8080/api/groups/{group_id}/photos", 
                                  headers=member_headers, files=files, data=data)
        
        print(f"📝 Member photo upload response: {response.status_code}")
        if response.status_code == 201:
            member_photo_result = response.json()
            print(f"✅ Member uploaded photo: {member_photo_result['photo']['filename']}")
        else:
            print(f"❌ Member photo upload failed: {response.text}")
    except Exception as e:
        print(f"❌ Error uploading member photo: {e}")
    
    # Test 8: Check if member can see all photos (including owner's photo)
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/photos", headers=member_headers)
        print(f"📝 Member get photos response: {response.status_code}")
        if response.status_code == 200:
            photos = response.json()
            print(f"✅ Member can see {len(photos)} photos")
            for photo in photos:
                print(f"   - {photo['filename']} by {photo['user_name']} (caption: {photo['caption']})")
        else:
            print(f"❌ Member cannot see photos: {response.text}")
    except Exception as e:
        print(f"❌ Error checking member photo access: {e}")
    
    # Test 9: Check if owner can see all photos (including member's photo)
    try:
        response = requests.get(f"http://localhost:8080/api/groups/{group_id}/photos", headers=owner_headers)
        print(f"📝 Owner get photos response: {response.status_code}")
        if response.status_code == 200:
            photos = response.json()
            print(f"✅ Owner can see {len(photos)} photos")
            for photo in photos:
                print(f"   - {photo['filename']} by {photo['user_name']} (caption: {photo['caption']})")
        else:
            print(f"❌ Owner cannot see photos: {response.text}")
    except Exception as e:
        print(f"❌ Error checking owner photo access: {e}")
    
    # Test 10: Test photo access from different user (non-member)
    try:
        # Create another test user
        non_member_data = {
            "name": "Non Member",
            "email": "nonmember@gmail.com",
            "password": "nonmember123"
        }
        response = requests.post("http://localhost:8080/api/register", json=non_member_data)
        if response.status_code == 200:
            print("✅ Non-member user created")
        else:
            print(f"⚠️ Non-member user creation: {response.status_code} (might already exist)")
        
        # Login as non-member
        non_member_login_data = {
            "email": "nonmember@gmail.com",
            "password": "nonmember123"
        }
        response = requests.post("http://localhost:8080/api/login", json=non_member_login_data)
        if response.status_code == 200:
            non_member_token = response.json()["access_token"]
            non_member_headers = {"Authorization": f"Bearer {non_member_token}"}
            
            # Try to access photos
            response = requests.get(f"http://localhost:8080/api/groups/{group_id}/photos", headers=non_member_headers)
            print(f"📝 Non-member get photos response: {response.status_code}")
            if response.status_code == 403:
                print("✅ Non-member correctly denied access to photos")
            else:
                print(f"❌ Non-member should be denied access but got: {response.status_code}")
        else:
            print(f"❌ Non-member login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing non-member access: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 GALLERY MEMBER ACCESS TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_gallery_member_access() 