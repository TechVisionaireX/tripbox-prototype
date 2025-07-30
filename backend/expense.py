from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, Expense, User, Trip, Group
from datetime import datetime

expense_bp = Blueprint('expense_bp', __name__)

# ✅ POST: Add a new expense with automatic splitting
@expense_bp.route('/api/groups/<int:group_id>/expenses', methods=['POST'])
@jwt_required()
def add_expense(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    # Validate required fields
    amount = data.get('amount')
    description = data.get('description', '')
    
    if not amount or amount <= 0:
        return jsonify({'error': 'Valid amount is required'}), 400

    # Create expense
    expense = Expense(
        group_id=group_id,
        user_id=user_id,
        amount=amount,
        category=data.get('category', 'General'),
        note=description
    )
    db.session.add(expense)
    db.session.commit()

    # Get all group members for splitting info
    all_members = GroupMember.query.filter_by(group_id=group_id).all()
    member_count = len(all_members)
    split_amount = round(amount / member_count, 2)

    print(f"🔍 Debug: Creating expense response")
    print(f"   Expense ID: {expense.id}")
    print(f"   Amount: {expense.amount}")
    print(f"   Category: {expense.category}")
    print(f"   Member count: {member_count}")
    print(f"   Split amount: {split_amount}")

    response_data = {
        'message': 'Expense added successfully',
        'expense': {
            'id': expense.id,
            'amount': expense.amount,
            'category': expense.category,
            'note': expense.note,
            'user_id': expense.user_id,
            'timestamp': expense.timestamp.isoformat(),
            'split_amount': split_amount,
            'member_count': member_count
        }
    }

    print(f"🔍 Debug: Response data: {response_data}")
    return jsonify(response_data), 201

# ✅ GET: List all expenses in group with user details
@expense_bp.route('/api/groups/<int:group_id>/expenses', methods=['GET'])
@jwt_required()
def get_expenses(group_id):
    user_id = int(get_jwt_identity())

    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    expenses = Expense.query.filter_by(group_id=group_id).order_by(Expense.timestamp.desc()).all()
    
    result = []
    for expense in expenses:
        # Get user details
        user = User.query.get(expense.user_id)
        result.append({
            'id': expense.id,
            'amount': expense.amount,
            'category': expense.category,
            'note': expense.note,
            'user_id': expense.user_id,
            'user_name': user.name if user else 'Unknown User',
            'user_email': user.email if user else '',
            'timestamp': expense.timestamp.isoformat()
        })

    return jsonify(result)

# ✅ GET: Calculate detailed split across group members
@expense_bp.route('/api/groups/<int:group_id>/expenses/split', methods=['GET'])
@jwt_required()
def split_expenses(group_id):
    user_id = int(get_jwt_identity())

    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    # Get all members with user details
    members = GroupMember.query.filter_by(group_id=group_id).all()
    expenses = Expense.query.filter_by(group_id=group_id).all()

    # Calculate totals
    total_expense = sum(e.amount for e in expenses)
    member_count = len(members)
    split_per_member = round(total_expense / member_count, 2) if member_count > 0 else 0

    # Get member details
    member_details = []
    for member in members:
        user = User.query.get(member.user_id)
        member_details.append({
            'user_id': member.user_id,
            'name': user.name if user else 'Unknown User',
            'email': user.email if user else '',
            'split_amount': split_per_member
        })

    return jsonify({
        'total_expense': round(total_expense, 2),
        'member_count': member_count,
        'split_per_member': split_per_member,
        'members': member_details,
        'expense_count': len(expenses)
    })

# ✅ GET: Get expense summary for a trip
@expense_bp.route('/api/trips/<int:trip_id>/expenses/summary', methods=['GET'])
@jwt_required()
def get_trip_expense_summary(trip_id):
    user_id = int(get_jwt_identity())

    # Get the main group for this trip
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        return jsonify({'error': 'Trip not found'}), 404

    # Verify user is part of the trip
    member = GroupMember.query.filter_by(group_id=group.id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this trip'}), 403

    # Get all expenses for this trip
    expenses = Expense.query.filter_by(group_id=group.id).all()
    members = GroupMember.query.filter_by(group_id=group.id).all()

    total_expense = sum(e.amount for e in expenses)
    member_count = len(members)
    split_per_member = round(total_expense / member_count, 2) if member_count > 0 else 0

    # Group expenses by category
    categories = {}
    for expense in expenses:
        category = expense.category or 'General'
        if category not in categories:
            categories[category] = 0
        categories[category] += expense.amount

    return jsonify({
        'trip_id': trip_id,
        'total_expense': round(total_expense, 2),
        'member_count': member_count,
        'split_per_member': split_per_member,
        'expense_count': len(expenses),
        'categories': categories
    })

# ✅ DELETE: Remove an expense (only by the person who added it)
@expense_bp.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = int(get_jwt_identity())

    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    # Check if user is the one who added the expense
    if expense.user_id != user_id:
        return jsonify({'error': 'You can only delete your own expenses'}), 403

    # Check if user is still a member of the group
    member = GroupMember.query.filter_by(group_id=expense.group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense deleted successfully'})
