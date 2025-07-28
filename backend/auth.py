from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
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
    
    print(f"Login attempt for email: {email}")
    
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(days=1))
        print(f"Login successful for user: {user.name}")
        return jsonify({'token': access_token, 'user': {'email': user.email, 'name': user.name}})
    else:
        print(f"Login failed for email: {email}")
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    user_id = get_jwt_identity()
    print(f"Token validation for user_id: {user_id}")
    
    user = User.query.get(user_id)
    if user:
        print(f"Token valid for user: {user.name}")
        return jsonify({'valid': True, 'user': {'email': user.email, 'name': user.name}})
    else:
        print(f"Token invalid - user not found for user_id: {user_id}")
        return jsonify({'valid': False, 'error': 'User not found'}), 401
