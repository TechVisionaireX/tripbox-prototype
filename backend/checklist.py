from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, ChecklistItem  # ✅ IMPORT model
from datetime import datetime

checklist_bp = Blueprint('checklist_bp', __name__)

# ✅ Add item to checklist or packing list
@checklist_bp.route('/api/groups/<int:group_id>/checklist', methods=['POST'])
@jwt_required()
def add_item(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        return jsonify({'error': 'Unauthorized'}), 403

    item = ChecklistItem(
        group_id=group_id,
        user_id=user_id,
        type=data.get('type', 'checklist'),  # checklist or packing
        text=data['text']
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Item added', 'id': item.id}), 201

# ✅ Get all items
@checklist_bp.route('/api/groups/<int:group_id>/checklist', methods=['GET'])
@jwt_required()
def get_items(group_id):
    user_id = int(get_jwt_identity())
    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        return jsonify({'error': 'Unauthorized'}), 403

    items = ChecklistItem.query.filter_by(group_id=group_id).all()
    return jsonify([{
        'id': item.id,
        'text': item.text,
        'type': item.type,
        'completed': item.completed,
        'timestamp': item.timestamp.isoformat(),
        'user_id': item.user_id
    } for item in items])

# ✅ Mark item complete/incomplete
@checklist_bp.route('/api/checklist/<int:item_id>', methods=['PATCH'])
@jwt_required()
def toggle_item(item_id):
    user_id = int(get_jwt_identity())
    item = ChecklistItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    item.completed = not item.completed
    db.session.commit()
    return jsonify({'message': 'Updated', 'completed': item.completed})

# ✅ Delete item
@checklist_bp.route('/api/checklist/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    item = ChecklistItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Deleted'})
