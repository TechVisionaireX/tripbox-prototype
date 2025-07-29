from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
# NOTE: Remove local SQLAlchemy and Bcrypt instances – we will use the shared ones
# Standard libs
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the shared database and bcrypt instances defined in the dedicated modules
from models import db  # shared SQLAlchemy instance
from auth import auth_bp as _auth_bp_import_helper, bcrypt  # shared Bcrypt instance

# Create Flask app
app = Flask(__name__)

# Configure CORS for all origins in development
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:5000", 
    "http://localhost:5000",
    "https://tripbox-prototype.onrender.com",
    "file://"  # Allow file:// protocol for local HTML files
], supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Build absolute path to the instance directory (so gunicorn workers & Render see the same path)
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

# Configurations
if os.environ.get('FLASK_ENV') == 'production':
    env_db = os.environ.get('DATABASE_URL')
    if env_db:
        database_url = env_db
    else:
        database_url = f"sqlite:///{INSTANCE_DIR / 'tripbox.db'}"
else:
    database_url = f"sqlite:///{INSTANCE_DIR / 'tripbox.db'}"

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_secret_key_here')

# Initialize extensions with app (shared instances)
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Import User model AFTER db has been linked to the app
from models import User

# Import and register blueprints
blueprints = [
    ('auth', 'auth_bp'),
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

for module_name, blueprint_name in blueprints:
    try:
        module = __import__(module_name, fromlist=[blueprint_name])
        blueprint = getattr(module, blueprint_name)
        app.register_blueprint(blueprint)
        print(f"✅ {blueprint_name} registered successfully")
    except Exception as e:
        print(f"⚠️ Failed to register {blueprint_name}: {e}")

# Utility to create DB tables and a test user (called once at startup)
def init_db():
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

# Initialize database
init_db()

# API test route
@app.route('/api/hello')
def hello():
    # Standard hello endpoint used by tests and health checks
    return jsonify(message="Hello from backend!")

@app.route('/api/create-test-user', methods=['POST'])
def create_test_user():
    try:
        test_user = User.query.filter_by(email='test@test.com').first()
        if test_user:
            return jsonify({'message': 'Test user already exists', 'email': 'test@test.com', 'password': 'test123'})
        
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

# Frontend serving routes
@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_frontend_files(filename):
    """Serve frontend static files"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
    
    # Handle common frontend routes
    if filename in ['dashboard', 'features', 'advanced-features']:
        return send_from_directory(frontend_path, f'{filename}.html')
    
    # Try to serve the requested file
    try:
        return send_from_directory(frontend_path, filename)
    except:
        # If file not found, serve index.html for SPA behavior
        return send_from_directory(frontend_path, 'index.html')

# Run server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 TripBox-IntelliOrganizer Backend Starting...")
    print(f"📍 Running on: http://0.0.0.0:{port}")
    print(f"🔗 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("📧 Test Login: test@test.com / test123")
    print("🌐 Frontend served from backend at root URL")
    app.run(host="0.0.0.0", port=port, debug=False)

# For Gunicorn deployment
application = app
