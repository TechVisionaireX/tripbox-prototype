from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp, bcrypt
import os
import socket

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

# Register auth blueprint only
app.register_blueprint(auth_bp)

# Create tables if not present
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Test database connection
        from models import User
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

def find_free_port():
    """Find a free port to use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

if __name__ == '__main__':
    # Try different ports if one is busy
    ports_to_try = [5000, 3000, 8080, 8000, 4000]
    
    for port in ports_to_try:
        try:
            print(f"Attempting to start server on port {port}...")
            app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
            break
        except OSError as e:
            print(f"Port {port} is busy, trying next port...")
            continue
    else:
        # If all ports are busy, find a free one
        free_port = find_free_port()
        print(f"Using free port: {free_port}")
        app.run(host='127.0.0.1', port=free_port, debug=False, use_reloader=False) 