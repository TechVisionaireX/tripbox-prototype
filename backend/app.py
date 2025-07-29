from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
from auth import auth_bp, bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure CORS for all origins in development
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:5000", 
    "http://localhost:5000",
    "https://tripbox-intelliorganizer.onrender.com",
    "https://tripbox-prototype.onrender.com",
    "file://"  # Allow file:// protocol for local HTML files
], supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Configurations
database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/tripbox.db')
# Fix for Render's postgres:// URL (needs to be postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_secret_key_here')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Register only the auth blueprint (core functionality)
try:
    app.register_blueprint(auth_bp)
    print("✅ Auth blueprint registered successfully")
except Exception as e:
    print(f"❌ Failed to register auth blueprint: {e}")

# Basic routes
@app.route('/')
def home():
    return jsonify({
        "message": "TripBox API is running!",
        "version": "1.0",
        "status": "healthy"
    })

@app.route('/health')
def health_check():
    try:
        # Test database connection
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from TripBox API!"})

# Create tables and test user when app starts
with app.app_context():
    try:
        # Ensure instance directory exists
        os.makedirs('instance', exist_ok=True)
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create test user if it doesn't exist
        test_user = User.query.filter_by(email='test@test.com').first()
        if not test_user:
            hashed_password = bcrypt.generate_password_hash('test123').decode('utf-8')
            test_user = User(email='test@test.com', password=hashed_password, name='Test User')
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully")
        else:
            print("✅ Test user already exists")
            
    except Exception as e:
        print(f"⚠️ Warning during database setup: {e}")

# For Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
