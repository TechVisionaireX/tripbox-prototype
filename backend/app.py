from flask import Flask, jsonify, request
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

# Configure CORS for production
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:5000", 
    "https://tripbox-intelliorganizer.onrender.com",
    "https://tripbox-prototype.onrender.com"
], supports_credentials=True)

# Configurations
database_url = os.environ.get('DATABASE_URL', 'sqlite:///tripbox.db')
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

# Register core blueprints only
try:
    app.register_blueprint(auth_bp)
    print("✅ Auth blueprint registered successfully")
except Exception as e:
    print(f"❌ Failed to register auth blueprint: {e}")

# Import and register other blueprints with error handling
blueprints_to_try = [
    ('trips', 'trips_bp'),
    ('chat', 'chat_bp'),
    ('recommend', 'recommend_bp'),
    ('expense', 'expense_bp'),
    ('gallery', 'gallery_bp'),
    ('checklist', 'checklist_bp'),
    ('budget', 'budget_bp'),
    ('finalize', 'finalize_bp'),
    ('location', 'location_bp'),
    ('itinerary', 'itinerary_bp'),
    ('polls', 'polls_bp'),
    ('trip_finalization', 'trip_finalization_bp'),
    ('enhanced_chat', 'enhanced_chat_bp')
]

for module_name, blueprint_name in blueprints_to_try:
    try:
        module = __import__(module_name)
        blueprint = getattr(module, blueprint_name)
        app.register_blueprint(blueprint)
        print(f"✅ {blueprint_name} registered successfully")
    except Exception as e:
        print(f"⚠️ Failed to register {blueprint_name}: {e}")

# Create tables if not present
with app.app_context():
    try:
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
        print(f"⚠️ Warning: Database setup error: {e}")
        print("🔄 Continuing without database initialization...")

# Root and test route
@app.route('/')
def home():
    return jsonify(message="TripBox-IntelliOrganizer backend is running!")

@app.route('/api/hello')
def hello():
    return jsonify(message="TripBox-IntelliOrganizer backend is running!")

@app.route('/api/create-test-user', methods=['POST'])
def create_test_user():
    try:
        # Check if test user already exists
        test_user = User.query.filter_by(email='test@test.com').first()
        if test_user:
            return jsonify({'message': 'Test user already exists', 'email': 'test@test.com', 'password': 'test123'})
        
        # Create test user
        hashed_password = bcrypt.generate_password_hash('test123').decode('utf-8')
        test_user = User(email='test@test.com', password=hashed_password, name='Test User')
        db.session.add(test_user)
        db.session.commit()
        
        return jsonify({'message': 'Test user created successfully', 'email': 'test@test.com', 'password': 'test123'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint for deployment
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'TripBox backend is running',
        'database': 'connected' if db.engine else 'disconnected'
    })

# Run server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 TripBox-IntelliOrganizer Backend Starting...")
    print(f"📍 Running on: http://localhost:{port}")
    print(f"🔗 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("📧 Test Login: test@test.com / test123")
    app.run(host="0.0.0.0", port=port, debug=False)
