import requests
import json

def test_login():
    # Test login with the test user
    login_data = {
        'email': 'test@gmail.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post('http://localhost:5000/api/login', 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Login test response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   Access token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   Refresh token: {data.get('refresh_token', 'N/A')[:20]}...")
            print(f"   User: {data.get('user', {})}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")

if __name__ == '__main__':
    test_login() 