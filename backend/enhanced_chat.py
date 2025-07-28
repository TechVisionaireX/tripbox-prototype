from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db, EnhancedChatMessage, Group, GroupMember, User, Recommendation, Notification
import json
from datetime import datetime

enhanced_chat_bp = Blueprint('enhanced_chat_bp', __name__)

@enhanced_chat_bp.route('/api/groups/<int:group_id>/enhanced-chat', methods=['GET'])
@jwt_required()
def get_enhanced_messages(group_id):
    """Get enhanced chat messages for a group"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        messages = EnhancedChatMessage.query.filter_by(group_id=group_id).order_by(EnhancedChatMessage.timestamp).all()
        
        enhanced_messages = []
        for message in messages:
            user = User.query.get(message.user_id)
            
            # Parse read_by JSON
            read_by = json.loads(message.read_by) if message.read_by else []
            
            # Parse metadata
            metadata = json.loads(message.message_metadata) if message.message_metadata else {}
            
            enhanced_messages.append({
                'id': message.id,
                'user_id': message.user_id,
                'user_name': user.name if user else 'Unknown',
                'message': message.message,
                'message_type': message.message_type,
                'reply_to_message_id': message.reply_to_message_id,
                'is_edited': message.is_edited,
                'edited_at': message.edited_at.isoformat() if message.edited_at else None,
                'read_by': read_by,
                'is_read': current_user_id in read_by,
                'timestamp': message.timestamp.isoformat() if message.timestamp else None,
                'metadata': metadata
            })
        
        return jsonify({'messages': enhanced_messages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_chat_bp.route('/api/groups/<int:group_id>/enhanced-chat', methods=['POST'])
@jwt_required()
def send_enhanced_message(group_id):
    """Send enhanced chat message"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Create message
        message = EnhancedChatMessage(
            group_id=group_id,
            user_id=current_user_id,
            message=data.get('message'),
            message_type=data.get('message_type', 'text'),
            reply_to_message_id=data.get('reply_to_message_id'),
            read_by=json.dumps([current_user_id]),  # Sender has read it
            message_metadata=json.dumps(data.get('metadata', {}))
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Create notifications for other group members
        members = GroupMember.query.filter_by(group_id=group_id).all()
        group = Group.query.get(group_id)
        
        for member in members:
            if member.user_id != current_user_id:
                notification = Notification(
                    user_id=member.user_id,
                    group_id=group_id,
                    type='message',
                    title=f'New message in {group.name}',
                    message=data.get('message')[:100] + '...' if len(data.get('message', '')) > 100 else data.get('message'),
                    action_url=f'/groups/{group_id}/chat'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_chat_bp.route('/api/enhanced-chat/<int:message_id>/edit', methods=['PUT'])
@jwt_required()
def edit_message(message_id):
    """Edit a message"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        message = EnhancedChatMessage.query.get_or_404(message_id)
        
        # Check if user owns the message
        if message.user_id != current_user_id:
            return jsonify({'error': 'Can only edit your own messages'}), 403
        
        # Update message
        message.message = data.get('message')
        message.is_edited = True
        message.edited_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Message edited successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_chat_bp.route('/api/enhanced-chat/<int:message_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_message_read(message_id):
    """Mark message as read"""
    try:
        current_user_id = get_jwt_identity()
        
        message = EnhancedChatMessage.query.get_or_404(message_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=message.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update read_by
        read_by = json.loads(message.read_by) if message.read_by else []
        if current_user_id not in read_by:
            read_by.append(current_user_id)
            message.read_by = json.dumps(read_by)
            db.session.commit()
        
        return jsonify({'message': 'Message marked as read'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_chat_bp.route('/api/recommendations/<int:recommendation_id>/comments', methods=['GET'])
@jwt_required()
def get_recommendation_comments(recommendation_id):
    """Get comments on a recommendation"""
    try:
        current_user_id = get_jwt_identity()
        
        recommendation = Recommendation.query.get_or_404(recommendation_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=recommendation.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get messages that are comments on this recommendation
        comments = EnhancedChatMessage.query.filter_by(
            group_id=recommendation.group_id,
            message_type='recommendation_comment'
                    ).filter(
            EnhancedChatMessage.message_metadata.contains(f'"recommendation_id": {recommendation_id}')
        ).order_by(EnhancedChatMessage.timestamp).all()
        
        comment_list = []
        for comment in comments:
            user = User.query.get(comment.user_id)
            metadata = json.loads(comment.message_metadata) if comment.message_metadata else {}
            
            if metadata.get('recommendation_id') == recommendation_id:
                comment_list.append({
                    'id': comment.id,
                    'user_id': comment.user_id,
                    'user_name': user.name if user else 'Unknown',
                    'message': comment.message,
                    'timestamp': comment.timestamp.isoformat() if comment.timestamp else None
                })
        
        return jsonify({'comments': comment_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_chat_bp.route('/api/recommendations/<int:recommendation_id>/comments', methods=['POST'])
@jwt_required()
def add_recommendation_comment(recommendation_id):
    """Add comment to a recommendation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        recommendation = Recommendation.query.get_or_404(recommendation_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=recommendation.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Create comment message
        comment = EnhancedChatMessage(
            group_id=recommendation.group_id,
            user_id=current_user_id,
            message=data.get('message'),
            message_type='recommendation_comment',
            read_by=json.dumps([current_user_id]),
            message_metadata=json.dumps({
                'recommendation_id': recommendation_id,
                'recommendation_title': recommendation.title
            })
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Create notifications for other group members
        members = GroupMember.query.filter_by(group_id=recommendation.group_id).all()
        group = Group.query.get(recommendation.group_id)
        
        for member in members:
            if member.user_id != current_user_id:
                notification = Notification(
                    user_id=member.user_id,
                    group_id=recommendation.group_id,
                    type='recommendation_comment',
                    title=f'New comment on recommendation: {recommendation.title}',
                    message=data.get('message')[:100] + '...' if len(data.get('message', '')) > 100 else data.get('message'),
                    action_url=f'/groups/{recommendation.group_id}/recommendations/{recommendation_id}'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment_id': comment.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_chat_bp.route('/api/groups/<int:group_id>/typing', methods=['POST'])
@jwt_required()
def update_typing_status(group_id):
    """Update typing status for real-time indicators"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # In a real implementation, you'd use WebSockets or Server-Sent Events
        # For now, we'll just return success
        return jsonify({
            'message': 'Typing status updated',
            'is_typing': data.get('is_typing', False)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_chat_bp.route('/api/groups/<int:group_id>/search-messages', methods=['GET'])
@jwt_required()
def search_messages(group_id):
    """Search messages in a group"""
    try:
        current_user_id = get_jwt_identity()
        query = request.args.get('q', '')
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Search messages
        messages = EnhancedChatMessage.query.filter_by(group_id=group_id).filter(
            EnhancedChatMessage.message.contains(query)
        ).order_by(EnhancedChatMessage.timestamp.desc()).limit(50).all()
        
        search_results = []
        for message in messages:
            user = User.query.get(message.user_id)
            search_results.append({
                'id': message.id,
                'user_name': user.name if user else 'Unknown',
                'message': message.message,
                'message_type': message.message_type,
                'timestamp': message.timestamp.isoformat() if message.timestamp else None
            })
        
        return jsonify({
            'results': search_results,
            'query': query,
            'total': len(search_results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 