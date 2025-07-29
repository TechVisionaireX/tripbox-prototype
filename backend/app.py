import os
import sys

# Add error handling for imports
try:
    from flask import Flask, jsonify, request, send_from_directory, send_file
    from flask_cors import CORS
    from flask_jwt_extended import JWTManager
    print("✅ Flask imports successful")
except ImportError as e:
    print(f"❌ Flask import error: {e}")
    sys.exit(1)

try:
    from models import db, User
    from auth import auth_bp, bcrypt
    print("✅ Local imports successful")
except ImportError as e:
    print(f"❌ Local import error: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not available, continuing without .env")

# Create Flask app
app = Flask(__name__)
print("✅ Flask app created")

# Configure CORS for all origins in development
CORS(app, origins="*", supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Configurations
database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/tripbox.db')
# Fix for Render's postgres:// URL (needs to be postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'fallback-secret-key-for-development')

print(f"✅ Database URL: {database_url}")

# Initialize extensions
try:
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    print("✅ Extensions initialized")
except Exception as e:
    print(f"❌ Extension initialization error: {e}")
    sys.exit(1)

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
            result = connection.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from TripBox API!"})

# Create tables and test user when app starts
try:
    with app.app_context():
        # Ensure instance directory exists
        os.makedirs('instance', exist_ok=True)
        print("✅ Instance directory created")
        
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
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
