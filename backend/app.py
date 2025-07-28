from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp, bcrypt
import os

# Import your feature blueprints
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

# ✅ NEW: Location Check-in Blueprint
try:
    from location import location_bp
    print("Imported location_bp successfully!")
except Exception as e:
    print("FAILED to import location_bp:", e)

# ✅ NEW: AI Recommendations Blueprint
try:
    from ai_recommendations import ai_recommendations_bp
    print("Imported ai_recommendations_bp successfully!")
except Exception as e:
    print("FAILED to import ai_recommendations_bp:", e)

# ✅ NEW: Live Location Blueprint
try:
    from live_location import live_location_bp
    print("Imported live_location_bp successfully!")
except Exception as e:
    print("FAILED to import live_location_bp:", e)

# ✅ NEW: PDF Generator Blueprint
try:
    from pdf_generator import pdf_generator_bp
    print("Imported pdf_generator_bp successfully!")
except Exception as e:
    print("FAILED to import pdf_generator_bp:", e)

# ✅ NEW: Real-time Chat Blueprint
try:
    from real_time_chat import real_time_chat_bp
    print("Imported real_time_chat_bp successfully!")
except Exception as e:
    print("FAILED to import real_time_chat_bp:", e)

# Initialize app
app = Flask(__name__)

# Update CORS configuration for production
CORS(app, origins=[
    "http://localhost:3000",
    "https://resilient-marshmallow-13df59.netlify.app",
    "https://*.netlify.app"  # Allow any Netlify subdomain
])

# Configurations
# Use environment variable for database URL in production, fallback to SQLite for development
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tripbox.db')
# Fix for Render's postgres:// URL (needs to be postgresql://)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

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
app.register_blueprint(recommend_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(gallery_bp)
app.register_blueprint(checklist_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(finalize_bp)
app.register_blueprint(location_bp)  #  NEW
app.register_blueprint(ai_recommendations_bp)  # AI Recommendations
app.register_blueprint(live_location_bp)  # Live Location Tracking
app.register_blueprint(pdf_generator_bp)  # PDF Generation
app.register_blueprint(real_time_chat_bp)  # Enhanced Chat

# Create tables if not present
with app.app_context():
    db.create_all()

# Root and test route
@app.route('/')
def home():
    return jsonify(message="TripBox-IntelliOrganizer backend is running!")

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from backend!")

# Run server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
