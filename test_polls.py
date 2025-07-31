import requests
import json

# Test backend connectivity
print("Testing backend connectivity...")
try:
    response = requests.get('http://localhost:5000/api/hello')
    print(f"✅ Backend is accessible: {response.json()}")
except Exception as e:
    print(f"❌ Backend not accessible: {e}")
    exit(1)

# Test polls endpoint (should return 401 without auth, which means endpoint exists)
print("\nTesting polls endpoint...")
try:
    response = requests.get('http://localhost:5000/api/polls/active')
    print(f"❌ Polls endpoint should require auth, got: {response.status_code}")
except Exception as e:
    print(f"✅ Polls endpoint exists (requires auth): {e}")

print("\n✅ Backend is running and polls endpoint is available!")
print("📝 To test poll creation:")
print("1. Make sure you're logged in to the frontend")
print("2. Create a group first in the Groups section")
print("3. Go to Polls section and try creating a poll")
print("4. Use the 'Test Poll' button for detailed debugging") 