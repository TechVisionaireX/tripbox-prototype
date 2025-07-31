from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, User
from auth import auth_bp, bcrypt
import os
import threading
import time
import socket

# Import all your feature blueprints
try:
    from trips import trips_bp
    print("Imported trips_bp successfully!")
except Exception as e:
    print("FAILED to import trips_bp:", e)

try:
    from groups import groups_bp
    print("Imported groups_bp successfully!")
except Exception as e:
    print("FAILED to import groups_bp:", e)

try:
    from chat import chat_bp
    print("Imported chat_bp successfully!")
except Exception as e:
    print("FAILED to import chat_bp:", e)

try:
    from polls import polls_bp
    print("Imported polls_bp successfully!")
except Exception as e:
    print("FAILED to import polls_bp:", e)

try:
    from pdf_generator import pdf_bp
    print("Imported pdf_bp successfully!")
except Exception as e:
    print("FAILED to import pdf_bp:", e)

try:
    from notifications import notifications_bp
    print("Imported notifications_bp successfully!")
except Exception as e:
    print("FAILED to import notifications_bp:", e)

try:
    from recommend import recommend_bp
    print("Imported recommend_bp successfully!")
except Exception as e:
    print("FAILED to import recommend_bp:", e)

try:
    from expense import expense_bp
    print("Imported expense_bp successfully!")
except Exception as e:
    print("FAILED to import expense_bp:", e)

try:
    from gallery import gallery_bp
    print("Imported gallery_bp successfully!")
except Exception as e:
    print("FAILED to import gallery_bp:", e)

try:
    from checklist import checklist_bp
    print("Imported checklist_bp successfully!")
except Exception as e:
    print("FAILED to import checklist_bp:", e)

try:
    from budget import budget_bp
    print("Imported budget_bp successfully!")
except Exception as e:
    print("FAILED to import budget_bp:", e)

try:
    from finalize import finalize_bp
    print("Imported finalize_bp successfully!")
except Exception as e:
    print("FAILED to import finalize_bp:", e)

try:
    from location import location_bp
    print("Imported location_bp successfully!")
except Exception as e:
    print("FAILED to import location_bp:", e)

# Initialize app
app = Flask(__name__)

# CORS configuration - allow all origins for testing
CORS(app, origins="*")

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tripbox.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_secret_key_here')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(polls_bp)

# Conditionally register PDF blueprint if available
try:
    if 'pdf_bp' in globals():
        app.register_blueprint(pdf_bp)
        print("✅ PDF blueprint registered successfully")
    else:
        print("⚠️ PDF blueprint not available - skipping registration")
except Exception as e:
    print(f"⚠️ Error registering PDF blueprint: {e}")

app.register_blueprint(notifications_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(gallery_bp)
app.register_blueprint(checklist_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(finalize_bp)
app.register_blueprint(location_bp)

# Create tables if not present
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Test database connection
        user_count = User.query.count()
        print(f"✅ Database connected - {user_count} users found")
        
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")
        raise e

# Test routes
@app.route('/')
def home():
    return jsonify(message="TripBox-IntelliOrganizer backend is running!")

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from backend!")

@app.route('/api/test')
def test():
    return jsonify(message="Test endpoint working!")

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
            print(f"📝 Update frontend/index.html to use: const API_BASE = 'http://127.0.0.1:{port}';")
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