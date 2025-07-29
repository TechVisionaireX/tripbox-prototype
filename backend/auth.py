from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, User
import datetime

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # Validate input
        if not email or not password or not name:
            return jsonify({'error': 'All fields (name, email, password) are required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists with this email'}), 400
        
        # Create new user
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, password=hashed, name=name)
        
        # Save to database with error handling
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ User registered successfully: {email}")
        
        return jsonify({
            'message': 'Registration successful', 
            'user': {'email': user.email, 'name': user.name}
        })
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        print(f"🔍 Login attempt for: {email}")
        
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({'error': 'No account found with this email. Please register first.'}), 401
        
        # Check password
        if bcrypt.check_password_hash(user.password, password):
            print(f"✅ Login successful: {email}")
            
            # Create both access and refresh tokens
            access_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(hours=24))
            refresh_token = create_refresh_token(identity=str(user.id), expires_delta=datetime.timedelta(days=30))
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {'email': user.email, 'name': user.name},
                'message': 'Login successful'
            })
        else:
            print(f"❌ Invalid password for: {email}")
            return jsonify({'error': 'Invalid password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Create new access token
        new_access_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(hours=24))
        
        return jsonify({
            'access_token': new_access_token,
            'user': {'email': user.email, 'name': user.name}
        })
        
    except Exception as e:
        print(f"❌ Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500

@auth_bp.route('/api/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'valid': False, 'error': 'User not found'}), 401
        
        return jsonify({
            'valid': True, 
            'user': {'email': user.email, 'name': user.name}
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 401

@auth_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a more advanced implementation, you might want to blacklist the token
    # For now, we'll just return a success response
    return jsonify({'message': 'Logged out successfully'})

# Debug endpoint to check database status
@auth_bp.route('/api/debug/users', methods=['GET'])
def debug_users():
    try:
        users = User.query.all()
        user_count = len(users)
        user_list = [{'id': u.id, 'email': u.email, 'name': u.name} for u in users]
        
        return jsonify({
            'database_connected': True,
            'total_users': user_count,
            'users': user_list[:5]  # Show first 5 users only
        })
    except Exception as e:
        return jsonify({
            'database_connected': False,
            'error': str(e)
        }), 500
