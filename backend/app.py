from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db, User
from auth import auth_bp, bcrypt
import os

app = Flask(__name__)

# Configure CORS
CORS(app, supports_credentials=True)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tripbox.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_secret_key_here')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
