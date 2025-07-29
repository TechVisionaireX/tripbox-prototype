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

# Create tables if not present
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
            
            # Create test user if it doesn't exist
            test_user = User.query.filter_by(email='test@test.com').first()
            if not test_user:
                hashed_password = bcrypt.generate_password_hash('test123').decode('utf-8')
                test_user = User(email='test@test.com', password=hashed_password, name='Test User')
                db.session.add(test_user)
                db.session.commit()
                print("Test user created successfully")
                
        except Exception as e:
            print(f"Warning: Database setup error: {e}")

# API test route
@app.route('/api/hello')
def hello():
    return jsonify(message="TripBox-IntelliOrganizer backend is running!")

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
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_frontend_files(filename):
    """Serve frontend static files"""
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

# Run server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("TripBox-IntelliOrganizer Backend Starting...")
    print(f"Running on: http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

# For Gunicorn deployment
app = app
