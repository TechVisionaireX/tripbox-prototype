from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from models import db, User
import datetime

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password=hashed, name=name)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registration successful'})

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(days=1))
        return jsonify({'token': access_token, 'user': {'email': user.email, 'name': user.name}})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
