from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, ChatMessage, User
from datetime import datetime
import json

real_time_chat_bp = Blueprint('real_time_chat_bp', __name__)

# Enhanced chat message model (extending the existing one)
class EnhancedChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), default='text')  # text, image, location, file
    reply_to_message_id = db.Column(db.Integer, db.ForeignKey('enhanced_chat_message.id'))
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    read_by = db.Column(db.Text)  # JSON array of user IDs who read the message
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    metadata = db.Column(db.Text)  # JSON for additional data (location coords, file info, etc.)

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/enhanced', methods=['POST'])
@jwt_required()
def send_enhanced_message(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Check if user is a member of the group
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get user info for the response
    user = User.query.get(user_id)
    
    message_type = data.get('type', 'text')
    metadata = data.get('metadata', {})
    
    # Handle different message types
    if message_type == 'location':
        if not metadata.get('latitude') or not metadata.get('longitude'):
            return jsonify({'error': 'Location coordinates required'}), 400
        message_text = f"📍 Shared location: {metadata.get('location_name', 'Unknown location')}"
    elif message_type == 'image':
        if not metadata.get('image_url'):
            return jsonify({'error': 'Image URL required'}), 400
        message_text = f"📷 Shared an image: {metadata.get('caption', '')}"
    elif message_type == 'file':
        if not metadata.get('file_name'):
            return jsonify({'error': 'File name required'}), 400
        message_text = f"📎 Shared file: {metadata.get('file_name')}"
    else:
        message_text = data.get('message', '')
    
    # Create enhanced message
    message = EnhancedChatMessage(
        group_id=group_id,
        user_id=user_id,
        message=message_text,
        message_type=message_type,
        reply_to_message_id=data.get('reply_to'),
        metadata=json.dumps(metadata) if metadata else None
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Prepare response with user info
    response_data = {
        'message_id': message.id,
        'group_id': group_id,
        'user_id': user_id,
        'user_name': user.name if user else f'User {user_id}',
        'message': message_text,
        'type': message_type,
        'metadata': metadata,
        'reply_to': data.get('reply_to'),
        'timestamp': message.timestamp.isoformat(),
        'read_count': 0
    }
    
    # In a real implementation, you would broadcast this via WebSocket
    # broadcast_to_group(group_id, 'new_message', response_data)
    
    return jsonify({
        'message': 'Message sent successfully',
        'data': response_data
    }), 201

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/enhanced', methods=['GET'])
@jwt_required()
def get_enhanced_messages(group_id):
    user_id = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    before_message_id = request.args.get('before', type=int)
    
    # Build query
    query = EnhancedChatMessage.query.filter_by(group_id=group_id)
    
    if before_message_id:
        query = query.filter(EnhancedChatMessage.id < before_message_id)
    
    messages = query.order_by(EnhancedChatMessage.timestamp.desc()).limit(per_page).all()
    
    # Get user info for all message senders
    user_ids = list(set(msg.user_id for msg in messages))
    users = {user.id: user for user in User.query.filter(User.id.in_(user_ids)).all()}
    
    result = []
    for message in reversed(messages):  # Show oldest first
        user = users.get(message.user_id)
        metadata = json.loads(message.metadata) if message.metadata else {}
        
        read_by_list = json.loads(message.read_by) if message.read_by else []
        
        result.append({
            'id': message.id,
            'user_id': message.user_id,
            'user_name': user.name if user else f'User {message.user_id}',
            'message': message.message,
            'type': message.message_type,
            'metadata': metadata,
            'reply_to': message.reply_to_message_id,
            'is_edited': message.is_edited,
            'edited_at': message.edited_at.isoformat() if message.edited_at else None,
            'timestamp': message.timestamp.isoformat(),
            'read_by': read_by_list,
            'read_count': len(read_by_list)
        })
    
    return jsonify({
        'messages': result,
        'page': page,
        'per_page': per_page,
        'total': len(result),
        'has_more': len(result) == per_page
    })

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/messages/<int:message_id>/read', methods=['POST'])
@jwt_required()
def mark_message_read(group_id, message_id):
    user_id = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get message
    message = EnhancedChatMessage.query.filter_by(id=message_id, group_id=group_id).first()
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    # Update read status
    read_by_list = json.loads(message.read_by) if message.read_by else []
    
    if user_id not in read_by_list:
        read_by_list.append(user_id)
        message.read_by = json.dumps(read_by_list)
        db.session.commit()
    
    return jsonify({
        'message': 'Message marked as read',
        'read_count': len(read_by_list)
    })

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/messages/<int:message_id>/edit', methods=['PUT'])
@jwt_required()
def edit_message(group_id, message_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Get message
    message = EnhancedChatMessage.query.filter_by(
        id=message_id, 
        group_id=group_id, 
        user_id=user_id
    ).first()
    
    if not message:
        return jsonify({'error': 'Message not found or unauthorized'}), 404
    
    # Update message
    message.message = data.get('message', message.message)
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    
    if data.get('metadata'):
        message.metadata = json.dumps(data['metadata'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Message updated successfully',
        'edited_at': message.edited_at.isoformat()
    })

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/messages/<int:message_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_message(group_id, message_id):
    user_id = int(get_jwt_identity())
    
    # Get message
    message = EnhancedChatMessage.query.filter_by(
        id=message_id, 
        group_id=group_id, 
        user_id=user_id
    ).first()
    
    if not message:
        return jsonify({'error': 'Message not found or unauthorized'}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'message': 'Message deleted successfully'})

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/typing', methods=['POST'])
@jwt_required()
def update_typing_status(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    is_typing = data.get('is_typing', False)
    
    # In a real implementation, you would broadcast this via WebSocket
    typing_data = {
        'user_id': user_id,
        'group_id': group_id,
        'is_typing': is_typing,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # broadcast_to_group(group_id, 'typing_status', typing_data)
    
    return jsonify({
        'message': 'Typing status updated',
        'data': typing_data
    })

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/online-members', methods=['GET'])
@jwt_required()
def get_online_members(group_id):
    user_id = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # In a real implementation, you would track online status
    # For now, return all group members as potentially online
    members = GroupMember.query.filter_by(group_id=group_id).all()
    users = User.query.filter(User.id.in_([m.user_id for m in members])).all()
    
    online_members = []
    for user in users:
        online_members.append({
            'user_id': user.id,
            'name': user.name,
            'last_seen': datetime.utcnow().isoformat(),  # Mock data
            'is_online': True  # Mock data
        })
    
    return jsonify({
        'online_members': online_members,
        'total_online': len(online_members)
    })

@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/search', methods=['GET'])
@jwt_required()
def search_messages(group_id):
    user_id = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    query = request.args.get('q', '')
    message_type = request.args.get('type', 'all')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    # Build search query
    search_query = EnhancedChatMessage.query.filter_by(group_id=group_id)
    search_query = search_query.filter(EnhancedChatMessage.message.contains(query))
    
    if message_type != 'all':
        search_query = search_query.filter_by(message_type=message_type)
    
    messages = search_query.order_by(EnhancedChatMessage.timestamp.desc()).limit(limit).all()
    
    # Get user info
    user_ids = list(set(msg.user_id for msg in messages))
    users = {user.id: user for user in User.query.filter(User.id.in_(user_ids)).all()}
    
    result = []
    for message in messages:
        user = users.get(message.user_id)
        metadata = json.loads(message.metadata) if message.metadata else {}
        
        result.append({
            'id': message.id,
            'user_id': message.user_id,
            'user_name': user.name if user else f'User {message.user_id}',
            'message': message.message,
            'type': message.message_type,
            'metadata': metadata,
            'timestamp': message.timestamp.isoformat()
        })
    
    return jsonify({
        'results': result,
        'query': query,
        'total_found': len(result)
    })

# WebSocket simulation endpoints (in a real app, use Socket.IO or similar)
@real_time_chat_bp.route('/api/groups/<int:group_id>/chat/events', methods=['GET'])
@jwt_required()
def get_chat_events(group_id):
    """Simulate WebSocket events polling"""
    user_id = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get last event timestamp from query params
    since = request.args.get('since')
    if since:
        try:
            since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
        except:
            since_datetime = datetime.utcnow()
    else:
        since_datetime = datetime.utcnow()
    
    # Get new messages since timestamp
    new_messages = EnhancedChatMessage.query.filter(
        EnhancedChatMessage.group_id == group_id,
        EnhancedChatMessage.timestamp > since_datetime
    ).order_by(EnhancedChatMessage.timestamp.asc()).all()
    
    events = []
    for message in new_messages:
        user = User.query.get(message.user_id)
        metadata = json.loads(message.metadata) if message.metadata else {}
        
        events.append({
            'type': 'new_message',
            'data': {
                'id': message.id,
                'user_id': message.user_id,
                'user_name': user.name if user else f'User {message.user_id}',
                'message': message.message,
                'message_type': message.message_type,
                'metadata': metadata,
                'timestamp': message.timestamp.isoformat()
            }
        })
    
    return jsonify({
        'events': events,
        'timestamp': datetime.utcnow().isoformat(),
        'has_new_events': len(events) > 0
    }) 