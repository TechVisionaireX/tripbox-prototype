from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp, bcrypt
try:
    from trips import trips_bp
    print("Imported trips_bp successfully!")
except Exception as e:
    print("FAILED to import trips_bp:", e)



app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tripbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify(message="TripBox-IntelliOrganizer backend is running!")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
