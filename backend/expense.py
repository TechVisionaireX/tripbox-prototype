from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, Expense

expense_bp = Blueprint('expense_bp', __name__)

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
