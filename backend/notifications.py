from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Notification, User, Group, GroupMember

notifications_bp = Blueprint('notifications_bp', __name__)

# GET: Get all notifications for current user
@notifications_bp.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    
    result = []
    for notification in notifications:
        result.append({
            'id': notification.id,
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'group_id': notification.group_id
        })
    
    return jsonify(result)

# POST: Mark notification as read
@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    user_id = int(get_jwt_identity())
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200

# POST: Mark all notifications as read
@notifications_bp.route('/api/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    user_id = int(get_jwt_identity())
    
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200

# Utility function to create notifications
def create_notification(user_id, group_id, notification_type, title, message):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user_id,
        group_id=group_id,
        type=notification_type,
        title=title,
        message=message
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def create_group_notification(group_id, notification_type, title, message, exclude_user_id=None):
    """Create notifications for all members of a group"""
    members = GroupMember.query.filter_by(group_id=group_id).all()
    
    for member in members:
        if exclude_user_id and member.user_id == exclude_user_id:
            continue
        
        create_notification(member.user_id, group_id, notification_type, title, message) 