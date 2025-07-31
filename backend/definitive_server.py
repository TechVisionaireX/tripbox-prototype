from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
import socket

# Create Flask app
app = Flask(__name__)
CORS(app, origins="*")

@app.route('/')
def home():
    return jsonify({"message": "Server is running!", "status": "success"})

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from backend!", "status": "success"})

@app.route('/api/test')
def test():
    return jsonify({"message": "Test endpoint working!", "status": "success"})

def check_port(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            s.close()
            return True
    except OSError:
        return False

def find_free_port():
    """Find a free port"""
    for port in [5000, 3000, 8080, 8000, 4000, 5001, 3001, 8081]:
        if check_port(port):
            return port
    return None

def start_server(port):
    """Start the server in a separate thread"""
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("🔍 Finding available port...")
    
    port = find_free_port()
    if not port:
        print("❌ No available ports found!")
        exit(1)
    
    print(f"✅ Using port {port}")
    print(f"🌐 Server will be available at: http://127.0.0.1:{port}")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Test the server
    try:
        import requests
        response = requests.get(f"http://127.0.0.1:{port}/api/hello", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is working! Response: {response.json()}")
            print(f"🎉 You can now access the frontend at: frontend/index.html")
            print(f"🔗 Backend URL: http://127.0.0.1:{port}")
        else:
            print(f"❌ Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing server: {e}")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n�� Server stopped") 