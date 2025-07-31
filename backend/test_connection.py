import requests
import time
import sys

def test_server(port):
    """Test if server is running on given port"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/api/hello", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is running on port {port}")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server on port {port}")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def test_all_ports():
    """Test common ports"""
    ports = [5000, 3000, 8080, 8000, 4000]
    
    for port in ports:
        print(f"Testing port {port}...")
        if test_server(port):
            return port
        time.sleep(1)
    
    return None

if __name__ == "__main__":
    print("🔍 Testing server connections...")
    
    working_port = test_all_ports()
    
    if working_port:
        print(f"✅ Server found on port {working_port}")
        print(f"🌐 You can access it at: http://127.0.0.1:{working_port}")
    else:
        print("❌ No server found on any tested port")
        print("💡 Make sure the server is running first") 