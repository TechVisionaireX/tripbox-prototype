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
    
    print(f"Sending message to group {group_id} from user {user_id}")
    print(f"Message text: {message_text}")

    # Check if user is a member of the group
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        print(f"User {user_id} is not a member of group {group_id}")
        return jsonify({'error': 'You are not a member of this group'}), 403

    # Get user info for notification
    user = User.query.get(user_id)
    if not user:
        print(f"User {user_id} not found")
        return jsonify({'error': 'User not found'}), 404

    # Get group info
    group = Group.query.get(group_id)
    if not group:
        print(f"Group {group_id} not found")
        return jsonify({'error': 'Group not found'}), 404

    print(f"Creating message from {user.name} in group {group.name}")

    message = ChatMessage(group_id=group_id, user_id=user_id, message=message_text)
    db.session.add(message)
    db.session.commit()

    print(f"Message created with ID {message.id}")

    # Create notifications for other group members
    other_members = GroupMember.query.filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id != user_id
    ).all()
    
    print(f"Other members to notify: {[m.user_id for m in other_members]}")
    
    # Create notifications for other group members
    from notifications import create_notification
    for member in other_members:
        create_notification(
            user_id=member.user_id,
            group_id=group_id,
            notification_type='chat_message',
            title=f'New message from {user.name}',
            message=f'{user.name}: {message_text[:50]}{"..." if len(message_text) > 50 else ""}'
        )

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
    print(f"Getting messages for group {group_id} by user {user_id}")

    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        print(f"User {user_id} is not a member of group {group_id}")
        return jsonify({'error': 'You are not a member of this group'}), 403

    messages = ChatMessage.query.filter_by(group_id=group_id).order_by(ChatMessage.timestamp.asc()).all()
    print(f"Found {len(messages)} messages for group {group_id}")
    
    result = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        sender_name = user.name if user else f'User {msg.user_id}'
        print(f"Message from user {msg.user_id} ({sender_name}): {msg.message[:50]}...")
        
        result.append({
            'user_id': msg.user_id,
            'sender_name': sender_name,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat()
        })

    print(f"Returning {len(result)} messages")
    return jsonify(result)

# GET: Get chat notifications for current user
@chat_bp.route('/api/notifications/chat', methods=['GET'])
@jwt_required()
def get_chat_notifications():
    user_id = int(get_jwt_identity())
    print(f"Getting chat notifications for user {user_id}")
    
    # Get all groups the user is a member of
    user_groups = GroupMember.query.filter_by(user_id=user_id).all()
    group_ids = [member.group_id for member in user_groups]
    print(f"User is member of groups: {group_ids}")
    
    if not group_ids:
        print("No groups found for user")
        return jsonify([])
    
    # Get recent messages from user's groups (excluding user's own messages)
    recent_messages = ChatMessage.query.filter(
        ChatMessage.group_id.in_(group_ids),
        ChatMessage.user_id != user_id
    ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    
    print(f"Found {len(recent_messages)} recent messages")
    
    notifications = []
    for msg in recent_messages:
        sender = User.query.get(msg.user_id)
        group = Group.query.get(msg.group_id)
        
        print(f"Message from user {msg.user_id} in group {msg.group_id}")
        print(f"Sender: {sender.name if sender else 'Unknown'}")
        print(f"Group: {group.name if group else 'Unknown'}")
        
        if sender and group:
            notifications.append({
                'sender_name': sender.name,
                'message_preview': msg.message[:30] + '...' if len(msg.message) > 30 else msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'group_id': msg.group_id,
                'group_name': group.name,
                'message_id': msg.id
            })
    
    print(f"Returning {len(notifications)} notifications")
    return jsonify(notifications)
