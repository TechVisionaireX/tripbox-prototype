from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp, bcrypt
import os

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

if __name__ == '__main__':
    print("Starting server on port 5000...")
    print("Server will be available at: http://localhost:5000")
    app.run(host='localhost', port=5000, debug=True) 