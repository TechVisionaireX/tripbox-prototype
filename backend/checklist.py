print("CHECKLIST BLUEPRINT LOADED")
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Group, GroupMember, ChecklistItem
from datetime import datetime

checklist_bp = Blueprint('checklist_bp', __name__)

@checklist_bp.route('/api/groups/<int:group_id>/checklist-items', methods=['POST'])
@jwt_required()
def add_checklist_item(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    data = request.get_json()
    item_type = data.get('type')
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'Item text cannot be empty'}), 400
    
    if item_type not in ['packing', 'todo', 'reminder']:
        return jsonify({'error': 'Invalid item type'}), 400
    
    try:
        # Create checklist item
        item = ChecklistItem(
            group_id=group_id,
            user_id=user_id,
            item_type=item_type,
            text=text,
            is_completed=False
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Get user info for response
        user = User.query.get(user_id)
        
        return jsonify({
            'message': 'Item added successfully',
            'item': {
                'id': item.id,
                'text': item.text,
                'type': item.item_type,
                'is_completed': item.is_completed,
                'user_id': item.user_id,
                'user_name': user.name
            }
        }), 201
        
    except Exception as e:
        print(f"Error adding checklist item: {e}")
        return jsonify({'error': 'Failed to add item'}), 500

@checklist_bp.route('/api/groups/<int:group_id>/packing-items', methods=['GET'])
@jwt_required()
def get_packing_items(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    try:
        # Get packing items with user information
        items = db.session.query(ChecklistItem, User).join(User).filter(
            ChecklistItem.group_id == group_id,
            ChecklistItem.item_type == 'packing'
        ).order_by(ChecklistItem.created_date.desc()).all()
        
        result = []
        for item, user in items:
            result.append({
                'id': item.id,
                'text': item.text,
                'is_completed': item.is_completed,
                'user_id': item.user_id,
                'user_name': user.name
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting packing items: {e}")
        return jsonify({'error': 'Failed to get packing items'}), 500

@checklist_bp.route('/api/groups/<int:group_id>/todo-items', methods=['GET'])
@jwt_required()
def get_todo_items(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    try:
        # Get todo items with user information
        items = db.session.query(ChecklistItem, User).join(User).filter(
            ChecklistItem.group_id == group_id,
            ChecklistItem.item_type == 'todo'
        ).order_by(ChecklistItem.created_date.desc()).all()
        
        result = []
        for item, user in items:
            result.append({
                'id': item.id,
                'text': item.text,
                'is_completed': item.is_completed,
                'created_date': item.created_date.isoformat(),
                'user_id': item.user_id,
                'user_name': user.name
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting todo items: {e}")
        return jsonify({'error': 'Failed to get todo items'}), 500

@checklist_bp.route('/api/groups/<int:group_id>/reminder-items', methods=['GET'])
@jwt_required()
def get_reminder_items(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    try:
        # Get reminder items with user information
        items = db.session.query(ChecklistItem, User).join(User).filter(
            ChecklistItem.group_id == group_id,
            ChecklistItem.item_type == 'reminder'
        ).order_by(ChecklistItem.created_date.desc()).all()
        
        result = []
        for item, user in items:
            result.append({
                'id': item.id,
                'text': item.text,
                'is_completed': item.is_completed,
                'created_date': item.created_date.isoformat(),
                'user_id': item.user_id,
                'user_name': user.name
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting reminder items: {e}")
        return jsonify({'error': 'Failed to get reminder items'}), 500

@checklist_bp.route('/api/packing-items/<int:item_id>/toggle-complete', methods=['POST'])
@jwt_required()
def toggle_packing_item(item_id):
    user_id = int(get_jwt_identity())
    
    # Get the item
    item = ChecklistItem.query.get(item_id)
    if not item or item.item_type != 'packing':
        return jsonify({'error': 'Packing item not found'}), 404
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=item.group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    try:
        # Toggle completion status
        item.is_completed = not item.is_completed
        db.session.commit()
        
        # Get updated list
        items = db.session.query(ChecklistItem, User).join(User).filter(
            ChecklistItem.group_id == item.group_id,
            ChecklistItem.item_type == 'packing'
        ).order_by(ChecklistItem.created_date.desc()).all()
        
        result = []
        for updated_item, user in items:
            result.append({
                'id': updated_item.id,
                'text': updated_item.text,
                'is_completed': updated_item.is_completed,
                'created_date': updated_item.created_date.isoformat(),
                'user_id': updated_item.user_id,
                'user_name': user.name
            })
        
        return jsonify({'items': result})
        
    except Exception as e:
        print(f"Error toggling packing item: {e}")
        return jsonify({'error': 'Failed to update item'}), 500

@checklist_bp.route('/api/todo-items/<int:item_id>/toggle-complete', methods=['POST'])
@jwt_required()
def toggle_todo_item(item_id):
    user_id = int(get_jwt_identity())
    
    # Get the item
    item = ChecklistItem.query.get(item_id)
    if not item or item.item_type != 'todo':
        return jsonify({'error': 'Todo item not found'}), 404
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=item.group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    try:
        # Toggle completion status
        item.is_completed = not item.is_completed
        db.session.commit()
        
        # Get updated list
        items = db.session.query(ChecklistItem, User).join(User).filter(
            ChecklistItem.group_id == item.group_id,
            ChecklistItem.item_type == 'todo'
        ).order_by(ChecklistItem.created_date.desc()).all()
        
        result = []
        for updated_item, user in items:
            result.append({
                'id': updated_item.id,
                'text': updated_item.text,
                'is_completed': updated_item.is_completed,
                'created_date': updated_item.created_date.isoformat(),
                'user_id': updated_item.user_id,
                'user_name': user.name
            })
        
        return jsonify({'items': result})
        
    except Exception as e:
        print(f"Error toggling todo item: {e}")
        return jsonify({'error': 'Failed to update item'}), 500

@checklist_bp.route('/api/reminder-items/<int:item_id>/toggle-complete', methods=['POST'])
@jwt_required()
def toggle_reminder_item(item_id):
    user_id = int(get_jwt_identity())
    
    # Get the item
    item = ChecklistItem.query.get(item_id)
    if not item or item.item_type != 'reminder':
        return jsonify({'error': 'Reminder item not found'}), 404
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=item.group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    try:
        # Toggle completion status
        item.is_completed = not item.is_completed
        db.session.commit()
        
        # Get updated list
        items = db.session.query(ChecklistItem, User).join(User).filter(
            ChecklistItem.group_id == item.group_id,
            ChecklistItem.item_type == 'reminder'
        ).order_by(ChecklistItem.created_date.desc()).all()
        
        result = []
        for updated_item, user in items:
            result.append({
                'id': updated_item.id,
                'text': updated_item.text,
                'is_completed': updated_item.is_completed,
                'created_date': updated_item.created_date.isoformat(),
                'user_id': updated_item.user_id,
                'user_name': user.name
            })
        
        return jsonify({'items': result})
        
    except Exception as e:
        print(f"Error toggling reminder item: {e}")
        return jsonify({'error': 'Failed to update item'}), 500

@checklist_bp.route('/api/checklist-items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_checklist_item(item_id):
    user_id = int(get_jwt_identity())
    
    # Get the item
    item = ChecklistItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # Check if user is the owner of the item
    if item.user_id != user_id:
        return jsonify({'error': 'You can only delete your own items'}), 403
    
    try:
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Item deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting checklist item: {e}")
        return jsonify({'error': 'Failed to delete item'}), 500
