from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, ChatMessage

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

    message = ChatMessage(group_id=group_id, user_id=user_id, message=message_text)
    db.session.add(message)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully'}), 201

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
    result = [{
        'user_id': msg.user_id,
        'message': msg.message,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages]

    return jsonify(result)
