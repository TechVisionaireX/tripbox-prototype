import requests
import json

# Test the AI assistant endpoints
BASE_URL = "http://localhost:5000"

def test_ai_assistant():
    print("Testing AI Assistant endpoints...")
    
    # Test 1: AI Chat
    print("\n1. Testing AI Chat endpoint...")
    chat_data = {
        "message": "Suggest a plan for Paris in June for food lovers on a budget",
        "trip_context": {
            "destination": "Paris",
            "dates": {
                "start": "2024-06-01",
                "end": "2024-06-07"
            },
            "group_size": 2
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/groups/1/ai-assistant/chat", 
                               json=chat_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Chat working!")
            print(f"Response: {result.get('response', {}).get('content', 'No content')[:100]}...")
        else:
            print(f"❌ AI Chat failed: {response.text}")
    except Exception as e:
        print(f"❌ AI Chat error: {e}")
    
    # Test 2: Smart Suggestions
    print("\n2. Testing Smart Suggestions endpoint...")
    suggestions_data = {
        "destination": "Paris",
        "budget": "medium",
        "interests": ["food", "culture"],
        "group_size": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/groups/1/ai-assistant/suggestions", 
                               json=suggestions_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Smart Suggestions working!")
            print(f"Found {len(result.get('suggestions', []))} suggestions")
        else:
            print(f"❌ Smart Suggestions failed: {response.text}")
    except Exception as e:
        print(f"❌ Smart Suggestions error: {e}")
    
    # Test 3: Smart Reminders
    print("\n3. Testing Smart Reminders endpoint...")
    trip_context = {
        "destination": "Paris",
        "dates": {
            "start": "2024-06-01",
            "end": "2024-06-07"
        },
        "group_size": 2
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/groups/1/ai-assistant/reminders",
                              params={"trip_data": json.dumps(trip_context)})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Smart Reminders working!")
            print(f"Found {len(result.get('reminders', []))} reminders")
        else:
            print(f"❌ Smart Reminders failed: {response.text}")
    except Exception as e:
        print(f"❌ Smart Reminders error: {e}")
    
    # Test 4: Weather Alerts
    print("\n4. Testing Weather Alerts endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/groups/1/ai-assistant/weather-alerts",
                              params={"lat": "48.8566", "lng": "2.3522"})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Weather Alerts working!")
            print(f"Found {len(result.get('weather_alerts', []))} weather alerts")
        else:
            print(f"❌ Weather Alerts failed: {response.text}")
    except Exception as e:
        print(f"❌ Weather Alerts error: {e}")

if __name__ == "__main__":
    test_ai_assistant() 