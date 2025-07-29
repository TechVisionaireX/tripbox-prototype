from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tripbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('TripMember', backref='user', lazy=True)
    messages = db.relationship('Message', backref='user', lazy=True)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    votes = db.relationship('PollVote', backref='user', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    destination = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invite_code = db.Column(db.String(10), unique=True, nullable=False)
    
    # Relationships
    members = db.relationship('TripMember', backref='trip', lazy=True)
    messages = db.relationship('Message', backref='trip', lazy=True)
    expenses = db.relationship('Expense', backref='trip', lazy=True)
    checklist_items = db.relationship('ChecklistItem', backref='trip', lazy=True)
    polls = db.relationship('Poll', backref='trip', lazy=True)

class TripMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # admin, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_location = db.Column(db.String(200))  # JSON string with lat, lng

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.String(20), default='text')  # text, location, expense

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    splits = db.relationship('ExpenseSplit', backref='expense', lazy=True)

class ExpenseSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON string
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ends_at = db.Column(db.DateTime)
    
    # Relationships
    votes = db.relationship('PollVote', backref='poll', lazy=True)

class PollVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    option_index = db.Column(db.Integer, nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions
def generate_invite_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

# Trip Management Routes
@app.route('/api/trips', methods=['GET'])
@jwt_required()
def get_trips():
    user_id = get_jwt_identity()
    trip_members = TripMember.query.filter_by(user_id=user_id).all()
    
    trips = []
    for member in trip_members:
        trip = member.trip
        trips.append({
            'id': trip.id,
            'name': trip.name,
            'description': trip.description,
            'destination': trip.destination,
            'start_date': trip.start_date.isoformat() if trip.start_date else None,
            'end_date': trip.end_date.isoformat() if trip.end_date else None,
            'invite_code': trip.invite_code,
            'role': member.role,
            'member_count': len(trip.members)
        })
    
    return jsonify(trips)

@app.route('/api/trips', methods=['POST'])
@jwt_required()
def create_trip():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    trip = Trip(
        name=data['name'],
        description=data.get('description', ''),
        destination=data.get('destination', ''),
        start_date=datetime.fromisoformat(data['start_date']).date() if data.get('start_date') else None,
        end_date=datetime.fromisoformat(data['end_date']).date() if data.get('end_date') else None,
        created_by=user_id,
        invite_code=generate_invite_code()
    )
    
    db.session.add(trip)
    db.session.flush()
    
    # Add creator as admin
    member = TripMember(user_id=user_id, trip_id=trip.id, role='admin')
    db.session.add(member)
    db.session.commit()
    
    return jsonify({
        'id': trip.id,
        'name': trip.name,
        'invite_code': trip.invite_code
    })

@app.route('/api/trips/join', methods=['POST'])
@jwt_required()
def join_trip():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    trip = Trip.query.filter_by(invite_code=data['invite_code']).first()
    if not trip:
        return jsonify({'message': 'Invalid invite code'}), 404
    
    # Check if already a member
    existing_member = TripMember.query.filter_by(user_id=user_id, trip_id=trip.id).first()
    if existing_member:
        return jsonify({'message': 'Already a member of this trip'}), 400
    
    member = TripMember(user_id=user_id, trip_id=trip.id)
    db.session.add(member)
    db.session.commit()
    
    return jsonify({'message': 'Successfully joined trip', 'trip_name': trip.name})

# Chat Routes
@app.route('/api/trips/<int:trip_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    messages = Message.query.filter_by(trip_id=trip_id).order_by(Message.timestamp).all()
    
    result = []
    for msg in messages:
        result.append({
            'id': msg.id,
            'content': msg.content,
            'username': msg.user.username,
            'timestamp': msg.timestamp.isoformat(),
            'message_type': msg.message_type
        })
    
    return jsonify(result)

@app.route('/api/trips/<int:trip_id>/messages', methods=['POST'])
@jwt_required()
def send_message(trip_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    message = Message(
        content=data['content'],
        user_id=user_id,
        trip_id=trip_id,
        message_type=data.get('message_type', 'text')
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Emit to all users in trip room
    user = User.query.get(user_id)
    socketio.emit('new_message', {
        'id': message.id,
        'content': message.content,
        'username': user.username,
        'timestamp': message.timestamp.isoformat(),
        'message_type': message.message_type
    }, room=f'trip_{trip_id}')
    
    return jsonify({'message': 'Message sent'})

# Expense Routes
@app.route('/api/trips/<int:trip_id>/expenses', methods=['GET'])
@jwt_required()
def get_expenses(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    expenses = Expense.query.filter_by(trip_id=trip_id).order_by(Expense.created_at.desc()).all()
    
    result = []
    for expense in expenses:
        splits = []
        for split in expense.splits:
            splits.append({
                'user_id': split.user_id,
                'username': split.user.username,
                'amount': split.amount,
                'paid': split.paid
            })
        
        result.append({
            'id': expense.id,
            'description': expense.description,
            'amount': expense.amount,
            'paid_by': expense.user.username,
            'created_at': expense.created_at.isoformat(),
            'splits': splits
        })
    
    return jsonify(result)

@app.route('/api/trips/<int:trip_id>/expenses', methods=['POST'])
@jwt_required()
def add_expense(trip_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    expense = Expense(
        description=data['description'],
        amount=data['amount'],
        paid_by=user_id,
        trip_id=trip_id
    )
    
    db.session.add(expense)
    db.session.flush()
    
    # Handle custom splits if provided, otherwise equal split
    if 'custom_splits' in data and data['custom_splits']:
        # Custom splits provided
        for split_data in data['custom_splits']:
            split = ExpenseSplit(
                expense_id=expense.id,
                user_id=split_data['user_id'],
                amount=split_data['amount'],
                paid=(split_data['user_id'] == user_id)
            )
            db.session.add(split)
    else:
        # Equal split among all members (default behavior)
        trip_members = TripMember.query.filter_by(trip_id=trip_id).all()
        split_amount = data['amount'] / len(trip_members)
        
        for trip_member in trip_members:
            split = ExpenseSplit(
                expense_id=expense.id,
                user_id=trip_member.user_id,
                amount=split_amount,
                paid=(trip_member.user_id == user_id)
            )
            db.session.add(split)
    
    db.session.commit()
    
    return jsonify({'message': 'Expense added successfully'})

# Get trip members for expense splitting
@app.route('/api/trips/<int:trip_id>/members', methods=['GET'])
@jwt_required()
def get_trip_members(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    members = TripMember.query.filter_by(trip_id=trip_id).all()
    
    result = []
    for member in members:
        result.append({
            'id': member.user_id,
            'username': member.user.username,
            'role': member.role,
            'joined_at': member.joined_at.isoformat()
        })
    
    return jsonify(result)

# Checklist Routes
@app.route('/api/trips/<int:trip_id>/checklist', methods=['GET'])
@jwt_required()
def get_checklist(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    items = ChecklistItem.query.filter_by(trip_id=trip_id).order_by(ChecklistItem.created_at).all()
    
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'text': item.text,
            'completed': item.completed,
            'created_by': item.user.username,
            'created_at': item.created_at.isoformat()
        })
    
    return jsonify(result)

@app.route('/api/trips/<int:trip_id>/checklist', methods=['POST'])
@jwt_required()
def add_checklist_item(trip_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    item = ChecklistItem(
        text=data['text'],
        trip_id=trip_id,
        created_by=user_id
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify({'message': 'Item added successfully'})

@app.route('/api/checklist/<int:item_id>/toggle', methods=['PUT'])
@jwt_required()
def toggle_checklist_item(item_id):
    user_id = get_jwt_identity()
    
    item = ChecklistItem.query.get_or_404(item_id)
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=item.trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    item.completed = not item.completed
    db.session.commit()
    
    return jsonify({'completed': item.completed})

# Location Routes
@app.route('/api/trips/<int:trip_id>/location', methods=['PUT'])
@jwt_required()
def update_location(trip_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    member.current_location = json.dumps({
        'lat': data['lat'],
        'lng': data['lng'],
        'timestamp': datetime.utcnow().isoformat()
    })
    
    db.session.commit()
    
    return jsonify({'message': 'Location updated'})

@app.route('/api/trips/<int:trip_id>/locations', methods=['GET'])
@jwt_required()
def get_locations(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    members = TripMember.query.filter_by(trip_id=trip_id).all()
    
    result = []
    for member in members:
        if member.current_location:
            location_data = json.loads(member.current_location)
            result.append({
                'username': member.user.username,
                'lat': location_data['lat'],
                'lng': location_data['lng'],
                'timestamp': location_data['timestamp']
            })
    
    return jsonify(result)

# Recommendations Route
@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    destination = request.args.get('destination')
    rec_type = request.args.get('type', 'hotels')  # hotels, flights, activities
    
    # Mock recommendations (in production, integrate with real APIs)
    recommendations = {
        'hotels': [
            {'name': 'Grand Hotel', 'rating': 4.5, 'price': '$150/night', 'image': 'hotel1.jpg'},
            {'name': 'City Inn', 'rating': 4.2, 'price': '$80/night', 'image': 'hotel2.jpg'},
            {'name': 'Luxury Resort', 'rating': 4.8, 'price': '$300/night', 'image': 'hotel3.jpg'}
        ],
        'flights': [
            {'airline': 'Air Travel', 'price': '$250', 'duration': '3h 45m', 'departure': '10:30 AM'},
            {'airline': 'Sky Wings', 'price': '$280', 'duration': '4h 15m', 'departure': '2:15 PM'},
            {'airline': 'Cloud Air', 'price': '$220', 'duration': '3h 55m', 'departure': '6:45 PM'}
        ],
        'activities': [
            {'name': 'City Tour', 'rating': 4.6, 'price': '$35', 'duration': '3 hours'},
            {'name': 'Museum Visit', 'rating': 4.3, 'price': '$20', 'duration': '2 hours'},
            {'name': 'Adventure Park', 'rating': 4.7, 'price': '$45', 'duration': '4 hours'}
        ]
    }
    
    return jsonify(recommendations.get(rec_type, []))

# Poll Routes
@app.route('/api/trips/<int:trip_id>/polls', methods=['GET'])
@jwt_required()
def get_polls(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    polls = Poll.query.filter_by(trip_id=trip_id).order_by(Poll.created_at.desc()).all()
    
    result = []
    for poll in polls:
        options = json.loads(poll.options)
        votes = {}
        total_votes = 0
        
        for vote in poll.votes:
            option_text = options[vote.option_index]
            votes[option_text] = votes.get(option_text, 0) + 1
            total_votes += 1
        
        user_vote = None
        user_vote_obj = PollVote.query.filter_by(poll_id=poll.id, user_id=user_id).first()
        if user_vote_obj:
            user_vote = options[user_vote_obj.option_index]
        
        result.append({
            'id': poll.id,
            'question': poll.question,
            'options': options,
            'votes': votes,
            'total_votes': total_votes,
            'created_by': poll.user.username,
            'created_at': poll.created_at.isoformat(),
            'ends_at': poll.ends_at.isoformat() if poll.ends_at else None,
            'user_vote': user_vote,
            'is_active': poll.ends_at is None or poll.ends_at > datetime.utcnow()
        })
    
    return jsonify(result)

@app.route('/api/trips/<int:trip_id>/polls', methods=['POST'])
@jwt_required()
def create_poll(trip_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    poll = Poll(
        question=data['question'],
        options=json.dumps(data['options']),
        trip_id=trip_id,
        created_by=user_id,
        ends_at=datetime.fromisoformat(data['ends_at']) if data.get('ends_at') else None
    )
    
    db.session.add(poll)
    db.session.commit()
    
    return jsonify({'message': 'Poll created successfully', 'poll_id': poll.id})

@app.route('/api/polls/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_poll(poll_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    poll = Poll.query.get_or_404(poll_id)
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=poll.trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    # Check if poll is still active
    if poll.ends_at and poll.ends_at < datetime.utcnow():
        return jsonify({'message': 'Poll has ended'}), 400
    
    # Remove existing vote if any
    existing_vote = PollVote.query.filter_by(poll_id=poll_id, user_id=user_id).first()
    if existing_vote:
        db.session.delete(existing_vote)
    
    # Add new vote
    vote = PollVote(
        poll_id=poll_id,
        user_id=user_id,
        option_index=data['option_index']
    )
    
    db.session.add(vote)
    db.session.commit()
    
    return jsonify({'message': 'Vote recorded successfully'})

# Enhanced Food Recommendations Route
@app.route('/api/recommendations/food', methods=['GET'])
@jwt_required()
def get_food_recommendations():
    destination = request.args.get('destination', 'general')
    category = request.args.get('category', 'all')  # breakfast, lunch, dinner, cafe, all
    
    # Mock food recommendations (in production, integrate with Yelp, Google Places, etc.)
    food_recommendations = {
        'restaurants': [
            {
                'name': 'The Local Bistro',
                'cuisine': 'International',
                'rating': 4.5,
                'price_range': '$$',
                'category': 'dinner',
                'address': '123 Main St',
                'description': 'Farm-to-table dining with local ingredients',
                'image': 'bistro.jpg',
                'distance': '0.3 miles'
            },
            {
                'name': 'Morning Glory Cafe',
                'cuisine': 'American',
                'rating': 4.3,
                'price_range': '$',
                'category': 'breakfast',
                'address': '456 Coffee Ave',
                'description': 'Best breakfast in town with fresh pastries',
                'image': 'cafe.jpg',
                'distance': '0.1 miles'
            },
            {
                'name': 'Pasta Paradise',
                'cuisine': 'Italian',
                'rating': 4.7,
                'price_range': '$$$',
                'category': 'dinner',
                'address': '789 Italian Way',
                'description': 'Authentic Italian cuisine with handmade pasta',
                'image': 'italian.jpg',
                'distance': '0.5 miles'
            },
            {
                'name': 'Taco Fiesta',
                'cuisine': 'Mexican',
                'rating': 4.4,
                'price_range': '$',
                'category': 'lunch',
                'address': '321 Spice Street',
                'description': 'Fresh tacos and authentic Mexican flavors',
                'image': 'mexican.jpg',
                'distance': '0.2 miles'
            },
            {
                'name': 'Sushi Zen',
                'cuisine': 'Japanese',
                'rating': 4.8,
                'price_range': '$$$$',
                'category': 'dinner',
                'address': '567 Zen Plaza',
                'description': 'Premium sushi with the freshest fish',
                'image': 'sushi.jpg',
                'distance': '0.4 miles'
            }
        ]
    }
    
    restaurants = food_recommendations['restaurants']
    if category != 'all':
        restaurants = [r for r in restaurants if r['category'] == category]
    
    return jsonify(restaurants)

# Itinerary and Summary Routes
@app.route('/api/trips/<int:trip_id>/itinerary', methods=['GET'])
@jwt_required()
def get_itinerary(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    trip = Trip.query.get_or_404(trip_id)
    
    # Get trip summary data
    expenses = Expense.query.filter_by(trip_id=trip_id).all()
    checklist_items = ChecklistItem.query.filter_by(trip_id=trip_id).all()
    polls = Poll.query.filter_by(trip_id=trip_id).all()
    messages = Message.query.filter_by(trip_id=trip_id).count()
    
    # Calculate expense summary
    total_expenses = sum(exp.amount for exp in expenses)
    completed_items = sum(1 for item in checklist_items if item.completed)
    
    # Generate day-by-day itinerary
    itinerary_days = []
    if trip.start_date and trip.end_date:
        current_date = trip.start_date
        day_count = (trip.end_date - trip.start_date).days + 1
        
        for i in range(day_count):
            day_date = current_date + timedelta(days=i)
            day_expenses = [exp for exp in expenses if exp.created_at.date() == day_date]
            day_total = sum(exp.amount for exp in day_expenses)
            
            itinerary_days.append({
                'date': day_date.isoformat(),
                'day_number': i + 1,
                'expenses': [{
                    'description': exp.description,
                    'amount': exp.amount,
                    'paid_by': exp.user.username
                } for exp in day_expenses],
                'total_spent': day_total,
                'activities': []  # This could be enhanced with actual activity tracking
            })
    
    return jsonify({
        'trip_info': {
            'name': trip.name,
            'destination': trip.destination,
            'start_date': trip.start_date.isoformat() if trip.start_date else None,
            'end_date': trip.end_date.isoformat() if trip.end_date else None,
            'duration_days': (trip.end_date - trip.start_date).days + 1 if trip.start_date and trip.end_date else 0,
            'member_count': len(trip.members)
        },
        'summary': {
            'total_expenses': total_expenses,
            'total_messages': messages,
            'checklist_progress': {
                'completed': completed_items,
                'total': len(checklist_items),
                'percentage': round((completed_items / len(checklist_items) * 100) if checklist_items else 0, 1)
            },
            'active_polls': len([p for p in polls if not p.ends_at or p.ends_at > datetime.utcnow()])
        },
        'daily_itinerary': itinerary_days,
        'recommendations': {
            'budget_tips': [
                'Consider sharing meals to save money',
                'Look for local markets for snacks',
                'Use public transportation when possible'
            ],
            'activities': [
                'Visit local landmarks',
                'Try regional cuisine',
                'Explore nearby parks or beaches'
            ]
        }
    })

@app.route('/api/trips/<int:trip_id>/summary/export', methods=['GET'])
@jwt_required()
def export_trip_summary(trip_id):
    user_id = get_jwt_identity()
    
    # Verify user is member of trip
    member = TripMember.query.filter_by(user_id=user_id, trip_id=trip_id).first()
    if not member:
        return jsonify({'message': 'Not authorized'}), 403
    
    # This would generate a downloadable PDF or detailed summary
    # For now, return a structured summary
    trip = Trip.query.get_or_404(trip_id)
    expenses = Expense.query.filter_by(trip_id=trip_id).all()
    members = TripMember.query.filter_by(trip_id=trip_id).all()
    
    # Calculate individual balances
    member_balances = {}
    for member in members:
        paid_total = sum(exp.amount for exp in expenses if exp.paid_by == member.user_id)
        owed_total = sum(
            split.amount for exp in expenses for split in exp.splits 
            if split.user_id == member.user_id
        )
        member_balances[member.user.username] = {
            'paid': paid_total,
            'owes': owed_total,
            'balance': paid_total - owed_total
        }
    
    return jsonify({
        'trip_name': trip.name,
        'destination': trip.destination,
        'dates': f"{trip.start_date} to {trip.end_date}" if trip.start_date and trip.end_date else "Dates not set",
        'members': [member.user.username for member in members],
        'expense_summary': {
            'total_spent': sum(exp.amount for exp in expenses),
            'number_of_expenses': len(expenses),
            'average_per_person': sum(exp.amount for exp in expenses) / len(members) if members else 0
        },
        'member_balances': member_balances,
        'detailed_expenses': [{
            'description': exp.description,
            'amount': exp.amount,
            'paid_by': exp.user.username,
            'date': exp.created_at.isoformat(),
            'splits': [{
                'user': split.user.username,
                'amount': split.amount,
                'paid': split.paid
            } for split in exp.splits]
        } for exp in expenses]
    })

# WebSocket Events
@socketio.on('join_trip')
def on_join_trip(data):
    trip_id = data['trip_id']
    join_room(f'trip_{trip_id}')
    emit('status', {'msg': f'Joined trip {trip_id}'})

@socketio.on('leave_trip')
def on_leave_trip(data):
    trip_id = data['trip_id']
    leave_room(f'trip_{trip_id}')
    emit('status', {'msg': f'Left trip {trip_id}'})

# Basic Routes
@app.route('/')
def home():
    return jsonify(message="TripBox-IntelliOrganizer backend is running!")

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from TripBox backend!")

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
