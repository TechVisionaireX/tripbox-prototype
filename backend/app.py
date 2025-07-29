from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
from auth import auth_bp, bcrypt
import os

# Import your feature blueprints
try:
    from trips import trips_bp
    print("✅ Imported trips_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import trips_bp: {e}")
    trips_bp = None

# try:
#     from groups import groups_bp
#     print("Imported groups_bp successfully!")
# except Exception as e:
#     print("FAILED to import groups_bp:", e)

try:
    from chat import chat_bp
    print("✅ Imported chat_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import chat_bp: {e}")
    chat_bp = None

try:
    from recommend import recommend_bp
    print("✅ Imported recommend_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import recommend_bp: {e}")
    recommend_bp = None

try:
    from expense import expense_bp
    print("✅ Imported expense_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import expense_bp: {e}")
    expense_bp = None

try:
    from gallery import gallery_bp
    print("✅ Imported gallery_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import gallery_bp: {e}")
    gallery_bp = None

try:
    from checklist import checklist_bp
    print("✅ Imported checklist_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import checklist_bp: {e}")
    checklist_bp = None

try:
    from budget import budget_bp
    print("✅ Imported budget_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import budget_bp: {e}")
    budget_bp = None

try:
    from finalize import finalize_bp
    print("✅ Imported finalize_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import finalize_bp: {e}")
    finalize_bp = None

# ✅ NEW: Location Check-in Blueprint
try:
    from location import location_bp
    print("✅ Imported location_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import location_bp: {e}")
    location_bp = None

# ✅ NEW: Additional Feature Blueprints
try:
    from itinerary import itinerary_bp
    print("✅ Imported itinerary_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import itinerary_bp: {e}")
    itinerary_bp = None

try:
    from polls import polls_bp
    print("✅ Imported polls_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import polls_bp: {e}")
    polls_bp = None

try:
    from trip_finalization import trip_finalization_bp
    print("✅ Imported trip_finalization_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import trip_finalization_bp: {e}")
    trip_finalization_bp = None

try:
    from enhanced_chat import enhanced_chat_bp
    print("✅ Imported enhanced_chat_bp successfully!")
except Exception as e:
    print(f"❌ FAILED to import enhanced_chat_bp: {e}")
    enhanced_chat_bp = None

# Advanced features will be enabled after initial deployment
try:
    from ai_recommendations import ai_recommendations_bp
    from live_location import live_location_bp
    from pdf_generator import pdf_generator_bp
    from real_time_chat import real_time_chat_bp
    
    if ai_recommendations_bp:
        app.register_blueprint(ai_recommendations_bp)
    if live_location_bp:
        app.register_blueprint(live_location_bp)
    if pdf_generator_bp:
        app.register_blueprint(pdf_generator_bp)
    if real_time_chat_bp:
        app.register_blueprint(real_time_chat_bp)
    print("✅ Advanced features enabled successfully")
except Exception as e:
    print(f"⚠️ Warning: Advanced features could not be enabled: {e}")
    # Continue without advanced features

# Create Flask app
app = Flask(__name__)

# Configure CORS for production
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:5000", 
    "https://tripbox-intelliorganizer.onrender.com",
    "https://tripbox-prototype.onrender.com"
], supports_credentials=True)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configurations
# Use environment variable for database URL in production, fallback to SQLite for development
database_url = os.environ.get('DATABASE_URL', 'sqlite:///tripbox.db')
# Fix for Render's postgres:// URL (needs to be postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_secret_key_here')

# API Keys
app.config['GOOGLE_PLACES_API_KEY'] = os.environ.get('GOOGLE_PLACES_API_KEY')
app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY')
app.config['OPENWEATHER_API_KEY'] = os.environ.get('OPENWEATHER_API_KEY')
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Register all blueprints
try:
    app.register_blueprint(auth_bp)
    if trips_bp:
        app.register_blueprint(trips_bp)
    if chat_bp:
        app.register_blueprint(chat_bp)
    if recommend_bp:
        app.register_blueprint(recommend_bp)
    if expense_bp:
        app.register_blueprint(expense_bp)
    if gallery_bp:
        app.register_blueprint(gallery_bp)
    if checklist_bp:
        app.register_blueprint(checklist_bp)
    if budget_bp:
        app.register_blueprint(budget_bp)
    if finalize_bp:
        app.register_blueprint(finalize_bp)
    if location_bp:
        app.register_blueprint(location_bp)
    if itinerary_bp:
        app.register_blueprint(itinerary_bp)
    if polls_bp:
        app.register_blueprint(polls_bp)
    if trip_finalization_bp:
        app.register_blueprint(trip_finalization_bp)
    if enhanced_chat_bp:
        app.register_blueprint(enhanced_chat_bp)
    print("✅ Core blueprints registered successfully")
except Exception as e:
    print(f"⚠️ Warning: Core blueprint registration error: {e}")

# Advanced features will be enabled after initial deployment
try:
    app.register_blueprint(ai_recommendations_bp)
    app.register_blueprint(live_location_bp)
    app.register_blueprint(pdf_generator_bp)
    app.register_blueprint(real_time_chat_bp)
    print("✅ Advanced features enabled successfully")
except Exception as e:
    print(f"⚠️ Warning: Advanced features could not be enabled: {e}")
    # Continue without advanced features

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
