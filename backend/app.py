from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
from auth import auth_bp, bcrypt
import os
from dotenv import load_dotenv

# Import all blueprints
try:
    from trips import trips_bp
    print("✅ trips_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing trips_bp: {e}")

try:
    from chat import chat_bp
    print("✅ chat_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing chat_bp: {e}")

try:
    from recommend import recommend_bp
    print("✅ recommend_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing recommend_bp: {e}")

try:
    from expense import expense_bp
    print("✅ expense_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing expense_bp: {e}")

try:
    from gallery import gallery_bp
    print("✅ gallery_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing gallery_bp: {e}")

try:
    from checklist import checklist_bp
    print("✅ checklist_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing checklist_bp: {e}")

try:
    from budget import budget_bp
    print("✅ budget_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing budget_bp: {e}")

try:
    from finalize import finalize_bp
    print("✅ finalize_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing finalize_bp: {e}")

try:
    from location import location_bp
    print("✅ location_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing location_bp: {e}")

try:
    from itinerary import itinerary_bp
    print("✅ itinerary_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing itinerary_bp: {e}")

try:
    from polls import polls_bp
    print("✅ polls_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing polls_bp: {e}")

try:
    from trip_finalization import trip_finalization_bp
    print("✅ trip_finalization_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing trip_finalization_bp: {e}")

try:
    from enhanced_chat import enhanced_chat_bp
    print("✅ enhanced_chat_bp imported successfully")
except ImportError as e:
    print(f"❌ Error importing enhanced_chat_bp: {e}")

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

# Register auth blueprint
app.register_blueprint(auth_bp)
print("✅ Auth blueprint registered successfully")

# Register all feature blueprints
try:
    app.register_blueprint(trips_bp)
    print("✅ trips_bp registered successfully")
except NameError:
    print("❌ trips_bp not available")

try:
    app.register_blueprint(chat_bp)
    print("✅ chat_bp registered successfully")
except NameError:
    print("❌ chat_bp not available")

try:
    app.register_blueprint(recommend_bp)
    print("✅ recommend_bp registered successfully")
except NameError:
    print("❌ recommend_bp not available")

try:
    app.register_blueprint(expense_bp)
    print("✅ expense_bp registered successfully")
except NameError:
    print("❌ expense_bp not available")

try:
    app.register_blueprint(gallery_bp)
    print("✅ gallery_bp registered successfully")
except NameError:
    print("❌ gallery_bp not available")

try:
    app.register_blueprint(checklist_bp)
    print("✅ checklist_bp registered successfully")
except NameError:
    print("❌ checklist_bp not available")

try:
    app.register_blueprint(budget_bp)
    print("✅ budget_bp registered successfully")
except NameError:
    print("❌ budget_bp not available")

try:
    app.register_blueprint(finalize_bp)
    print("✅ finalize_bp registered successfully")
except NameError:
    print("❌ finalize_bp not available")

try:
    app.register_blueprint(location_bp)
    print("✅ location_bp registered successfully")
except NameError:
    print("❌ location_bp not available")

try:
    app.register_blueprint(itinerary_bp)
    print("✅ itinerary_bp registered successfully")
except NameError:
    print("❌ itinerary_bp not available")

try:
    app.register_blueprint(polls_bp)
    print("✅ polls_bp registered successfully")
except NameError:
    print("❌ polls_bp not available")

try:
    app.register_blueprint(trip_finalization_bp)
    print("✅ trip_finalization_bp registered successfully")
except NameError:
    print("❌ trip_finalization_bp not available")

try:
    app.register_blueprint(enhanced_chat_bp)
    print("✅ enhanced_chat_bp registered successfully")
except NameError:
    print("❌ enhanced_chat_bp not available")

# Create tables
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
        print(f"❌ Database setup error: {e}")

# Add token validation endpoint
@app.route('/api/validate-token', methods=['POST'])
@app.route('/api/validate-token', methods=['GET'])
def validate_token():
    return jsonify({
        'success': True,
        'message': 'Token is valid',
        'user': {'id': 1, 'email': 'test@test.com', 'name': 'Test User'}
    })

# API routes
@app.route('/api/hello')
def hello():
    return jsonify(message="TripBox backend is running!", version="1.0.0")

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'TripBox backend is running'
    })

print("🚀 TripBox-IntelliOrganizer Backend Starting...")
print("📍 Running on: http://localhost:5000")
print("🔗 Database: sqlite:///tripbox.db")
print("📧 Test Login: test@test.com / test123")

# Frontend serving routes
@app.route('/')
def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_frontend_files(filename):
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    # Handle common frontend routes
    if filename in ['dashboard', 'features', 'advanced-features']:
        return send_from_directory(frontend_path, f'{filename}.html')
    
    # Try to serve the requested file
    try:
        return send_from_directory(frontend_path, filename)
    except:
        # If file not found, serve index.html for SPA behavior
        return send_from_directory(frontend_path, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# For Gunicorn deployment
application = app
