from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, Expense, Trip, Group

expense_bp = Blueprint('expense_bp', __name__)

# Trip-based expense endpoints
@expense_bp.route('/api/trips/<int:trip_id>/expenses', methods=['POST'])
@jwt_required()
def add_trip_expense(trip_id):
    """Add expense to a trip"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Check if user owns the trip
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or access denied'}), 403

    # Get or create a group for this trip
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        # Create default group for trip
        group = Group(
            name=f"{trip.name} Group",
            creator_id=user_id,
            trip_id=trip_id
        )
        db.session.add(group)
        db.session.flush()  # Get the ID
        
        # Add user as member
        member = GroupMember(group_id=group.id, user_id=user_id)
        db.session.add(member)

    expense = Expense(
        group_id=group.id,
        user_id=user_id,
        amount=float(data.get('amount', 0)),
        category=data.get('category'),
        note=data.get('description', data.get('note', ''))
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify({
        'message': 'Expense added successfully',
        'expense': {
            'id': expense.id,
            'amount': expense.amount,
            'category': expense.category,
            'note': expense.note,
            'timestamp': expense.timestamp.isoformat()
        }
    }), 201

@expense_bp.route('/api/trips/<int:trip_id>/expenses', methods=['GET'])
@jwt_required()
def get_trip_expenses(trip_id):
    """Get all expenses for a trip"""
    user_id = int(get_jwt_identity())

    # Check if user owns the trip
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or access denied'}), 403

    # Get or create a group for this trip
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        return jsonify([])  # No expenses yet

    expenses = Expense.query.filter_by(group_id=group.id).order_by(Expense.timestamp.desc()).all()
    result = [{
        'id': e.id,
        'amount': e.amount,
        'category': e.category,
        'note': e.note,
        'user_id': e.user_id,
        'timestamp': e.timestamp.isoformat()
    } for e in expenses]

    return jsonify(result)

# Original group-based endpoints
# ✅ POST: Add a new expense
@expense_bp.route('/api/groups/<int:group_id>/expenses', methods=['POST'])
@jwt_required()
def add_expense(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    expense = Expense(
        group_id=group_id,
        user_id=user_id,
        amount=data.get('amount'),
        category=data.get('category'),
        note=data.get('note')
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify({'message': 'Expense added'}), 201

# ✅ GET: List all expenses in group
@expense_bp.route('/api/groups/<int:group_id>/expenses', methods=['GET'])
@jwt_required()
def get_expenses(group_id):
    user_id = int(get_jwt_identity())

    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    expenses = Expense.query.filter_by(group_id=group_id).order_by(Expense.timestamp.desc()).all()
    result = [{
        'amount': e.amount,
        'category': e.category,
        'note': e.note,
        'user_id': e.user_id,
        'timestamp': e.timestamp.isoformat()
    } for e in expenses]

    return jsonify(result)

# ✅ GET: Calculate split across group members
@expense_bp.route('/api/groups/<int:group_id>/expenses/split', methods=['GET'])
@jwt_required()
def split_expenses(group_id):
    user_id = int(get_jwt_identity())

    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    members = GroupMember.query.filter_by(group_id=group_id).all()
    expenses = Expense.query.filter_by(group_id=group_id).all()

    total = sum(e.amount for e in expenses)
    per_member = round(total / len(members), 2) if members else 0

    return jsonify({
        'total_expense': round(total, 2),
        'members': len(members),
        'split_per_member': per_member
    })
