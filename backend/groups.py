from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, Trip

groups_bp = Blueprint('groups_bp', __name__)

# Create a new group
@groups_bp.route('/api/groups', methods=['POST'])
@jwt_required()
def create_group():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get('name')
    trip_id = data.get('trip_id')

    # Verify trip exists
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or unauthorized'}), 404

    group = Group(name=name, creator_id=user_id, trip_id=trip_id)
    db.session.add(group)
    db.session.commit()
    return jsonify({'message': 'Group created', 'group_id': group.id}), 201

# Get groups created by user
@groups_bp.route('/api/groups', methods=['GET'])
@jwt_required()
def get_groups():
    user_id = int(get_jwt_identity())
    groups = Group.query.filter_by(creator_id=user_id).all()
    result = [{
        'id': group.id,
        'name': group.name,
        'trip_id': group.trip_id
    } for group in groups]
    return jsonify(result)

# Add member to group
@groups_bp.route('/api/groups/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_group_member(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    friend_user_id = data.get('user_id')

    # Verify group exists and user is creator
    group = Group.query.filter_by(id=group_id, creator_id=user_id).first()
    if not group:
        return jsonify({'error': 'Group not found or unauthorized'}), 404

    member = GroupMember(group_id=group_id, user_id=friend_user_id)
    db.session.add(member)
    db.session.commit()
    return jsonify({'message': 'Member added to group'}), 201

# List members of group
@groups_bp.route('/api/groups/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_group_members(group_id):
    user_id = int(get_jwt_identity())

    # Verify group exists and user is creator
    group = Group.query.filter_by(id=group_id, creator_id=user_id).first()
    if not group:
        return jsonify({'error': 'Group not found or unauthorized'}), 404

    members = GroupMember.query.filter_by(group_id=group_id).all()
    result = [{'id': member.user_id} for member in members]

    return jsonify(result)
