from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, ChatMessage, User

chat_bp = Blueprint('chat_bp', __name__)

#  POST: Send message to a group
@chat_bp.route('/api/groups/<int:group_id>/chat', methods=['POST'])
@jwt_required()
def send_message(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    message_text = data.get('message')

    # Check if user is a member of the group
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403

    # Get user info for notification
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get group info
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    message = ChatMessage(group_id=group_id, user_id=user_id, message=message_text)
    db.session.add(message)
    db.session.commit()

    # Create notifications for other group members
    other_members = GroupMember.query.filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id != user_id
    ).all()
    
    # Store notifications in session or database (simplified version)
    # In a real app, you'd use a proper notification system
    for member in other_members:
        # You could store this in a notifications table
        # For now, we'll just return success
        pass

    return jsonify({
        'message': 'Message sent successfully',
        'message_id': message.id,
        'sender_name': user.name,
        'timestamp': message.timestamp.isoformat()
    }), 201

#  GET: Retrieve all messages in a group
@chat_bp.route('/api/groups/<int:group_id>/chat', methods=['GET'])
@jwt_required()
def get_messages(group_id):
    user_id = int(get_jwt_identity())

    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403

    messages = ChatMessage.query.filter_by(group_id=group_id).order_by(ChatMessage.timestamp.asc()).all()
    result = []
    
    for msg in messages:
        user = User.query.get(msg.user_id)
        result.append({
            'user_id': msg.user_id,
            'sender_name': user.name if user else f'User {msg.user_id}',
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat()
        })

    return jsonify(result)

# GET: Get chat notifications for current user
@chat_bp.route('/api/notifications/chat', methods=['GET'])
@jwt_required()
def get_chat_notifications():
    user_id = int(get_jwt_identity())
    
    # Get all groups the user is a member of
    user_groups = GroupMember.query.filter_by(user_id=user_id).all()
    group_ids = [member.group_id for member in user_groups]
    
    if not group_ids:
        return jsonify([])
    
    # Get recent messages from user's groups (excluding user's own messages)
    recent_messages = ChatMessage.query.filter(
        ChatMessage.group_id.in_(group_ids),
        ChatMessage.user_id != user_id
    ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    
    notifications = []
    for msg in recent_messages:
        sender = User.query.get(msg.user_id)
        group = Group.query.get(msg.group_id)
        
        if sender and group:
            notifications.append({
                'sender_name': sender.name,
                'message_preview': msg.message[:30] + '...' if len(msg.message) > 30 else msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'group_id': msg.group_id,
                'group_name': group.name,
                'message_id': msg.id
            })
    
    return jsonify(notifications)
