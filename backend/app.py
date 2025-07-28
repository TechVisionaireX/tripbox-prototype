from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp, bcrypt

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

# 🔁 NEW: Import gallery_bp
try:
    from gallery import gallery_bp
    print("Imported gallery_bp successfully!")
except Exception as e:
    print("FAILED to import gallery_bp:", e)

# Initialize app
app = Flask(__name__)
CORS(app)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tripbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'

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
app.register_blueprint(gallery_bp)  # 🔁 NEW

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
    app.run(host="0.0.0.0", port=5000)
