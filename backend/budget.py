from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, BudgetItem  # ✅ Import BudgetItem instead of redefining it
from datetime import datetime

budget_bp = Blueprint('budget_bp', __name__)

# ✅ Add budget item
@budget_bp.route('/api/groups/<int:group_id>/budget', methods=['POST'])
@jwt_required()
def add_budget(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        return jsonify({'error': 'Unauthorized'}), 403

    item = BudgetItem(
        group_id=group_id,
        user_id=user_id,
        category=data['category'],
        amount=data['amount']
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Budget item added', 'id': item.id}), 201

# ✅ View all budget items
@budget_bp.route('/api/groups/<int:group_id>/budget', methods=['GET'])
@jwt_required()
def get_budget(group_id):
    user_id = int(get_jwt_identity())
    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        return jsonify({'error': 'Unauthorized'}), 403

    items = BudgetItem.query.filter_by(group_id=group_id).order_by(BudgetItem.timestamp.desc()).all()
    total = sum(item.amount for item in items)

    return jsonify({
        'total': total,
        'items': [{
            'id': item.id,
            'category': item.category,
            'amount': item.amount,
            'timestamp': item.timestamp.isoformat(),
            'user_id': item.user_id
        } for item in items]
    })
