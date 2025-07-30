print("GROUPS BLUEPRINT LOADED")
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Trip, Group, GroupMember
from datetime import datetime

groups_bp = Blueprint('groups_bp', __name__)

@groups_bp.route('/api/groups', methods=['GET'])
@jwt_required()
def get_user_groups():
    user_id = int(get_jwt_identity())
    
    try:
        # Get groups where user is a member or owner
        groups = db.session.query(Group, Trip, User).join(Trip).join(User, Group.creator_id == User.id).filter(
            Group.id.in_(
                db.session.query(GroupMember.group_id).filter(GroupMember.user_id == user_id)
            )
        ).all()
        
        result = []
        for group, trip, creator in groups:
            # Get member count
            member_count = GroupMember.query.filter_by(group_id=group.id).count()
            
            result.append({
                'id': group.id,
                'name': group.name,
                'trip_id': group.trip_id,
                'trip_name': trip.name,
                'creator_id': group.creator_id,
                'creator_name': creator.name,
                'member_count': member_count,
                'is_owner': group.creator_id == user_id,
                'created_date': group.created_date.isoformat() if group.created_date else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting user groups: {e}")
        return jsonify({'error': 'Failed to get groups'}), 500

@groups_bp.route('/api/groups', methods=['POST'])
@jwt_required()
def create_group():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    name = data.get('name', '').strip()
    trip_id = data.get('trip_id')
    
    if not name:
        return jsonify({'error': 'Group name is required'}), 400
    
    if not trip_id:
        return jsonify({'error': 'Trip ID is required'}), 400
    
    try:
        # Check if trip exists and user has access
        trip = Trip.query.get(trip_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        # Check if user owns the trip or is a member
        if trip.user_id != user_id:
            # Check if user is a member through existing groups
            member_groups = db.session.query(GroupMember).join(Group).filter(
                Group.trip_id == trip_id,
                GroupMember.user_id == user_id
            ).first()
            if not member_groups:
                return jsonify({'error': 'You do not have access to this trip'}), 403
        
        # Check if group name already exists for this trip
        existing_group = Group.query.filter_by(trip_id=trip_id, name=name).first()
        if existing_group:
            return jsonify({'error': 'A group with this name already exists for this trip'}), 409
        
        # Create the group
        group = Group(
            name=name,
            trip_id=trip_id,
            creator_id=user_id,
            created_date=datetime.now()
        )
        
        db.session.add(group)
        db.session.commit()
        
        # Add creator as first member
        creator_member = GroupMember(
            group_id=group.id,
            user_id=user_id
        )
        
        db.session.add(creator_member)
        db.session.commit()
        
        # Get creator info for response
        creator = User.query.get(user_id)
        
        return jsonify({
            'message': 'Group created successfully',
            'group': {
                'id': group.id,
                'name': group.name,
                'trip_id': group.trip_id,
                'creator_id': group.creator_id,
                'creator_name': creator.name,
                'member_count': 1,
                'is_owner': True,
                'created_date': group.created_date.isoformat()
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating group: {e}")
        return jsonify({'error': 'Failed to create group'}), 500

@groups_bp.route('/api/groups/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group_details(group_id):
    user_id = int(get_jwt_identity())
    
    try:
        # Get group with trip and creator info
        group = db.session.query(Group, Trip, User).join(Trip).join(User, Group.creator_id == User.id).filter(
            Group.id == group_id
        ).first()
        
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        group_obj, trip, creator = group
        
        # Check if user is a member
        member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not member:
            return jsonify({'error': 'You are not a member of this group'}), 403
        
        return jsonify({
            'id': group_obj.id,
            'name': group_obj.name,
            'trip_id': group_obj.trip_id,
            'trip_name': trip.name,
            'creator_id': group_obj.creator_id,
            'creator_name': creator.name,
            'is_owner': group_obj.creator_id == user_id,
            'created_date': group_obj.created_date.isoformat() if group_obj.created_date else None
        })
        
    except Exception as e:
        print(f"Error getting group details: {e}")
        return jsonify({'error': 'Failed to get group details'}), 500

@groups_bp.route('/api/groups/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_group_members(group_id):
    user_id = int(get_jwt_identity())
    
    try:
        # Check if user is a member of the group
        member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not member:
            return jsonify({'error': 'You are not a member of this group'}), 403
        
        # Get group info
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        # Get all members with user info
        members = db.session.query(GroupMember, User).join(User).filter(
            GroupMember.group_id == group_id
        ).all()
        
        result = []
        for member_obj, user in members:
            result.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_owner': member_obj.user_id == group.creator_id,
                'joined_date': member_obj.joined_date.isoformat() if member_obj.joined_date else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting group members: {e}")
        return jsonify({'error': 'Failed to get group members'}), 500

@groups_bp.route('/api/groups/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_group_member(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Check if user is a member of the group
        member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not member:
            return jsonify({'error': 'You are not a member of this group'}), 403
        
        # Find user by email
        user_to_add = User.query.filter_by(email=email).first()
        if not user_to_add:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is already a member
        existing_member = GroupMember.query.filter_by(group_id=group_id, user_id=user_to_add.id).first()
        if existing_member:
            return jsonify({'error': 'User is already a member of this group'}), 409
        
        # Add user to group
        new_member = GroupMember(
            group_id=group_id,
            user_id=user_to_add.id,
            joined_date=datetime.now()
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Member added successfully',
            'member': {
                'id': user_to_add.id,
                'name': user_to_add.name,
                'email': user_to_add.email
            }
        }), 201
        
    except Exception as e:
        print(f"Error adding group member: {e}")
        return jsonify({'error': 'Failed to add member'}), 500

@groups_bp.route('/api/groups/<int:group_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_group_member(group_id, member_id):
    user_id = int(get_jwt_identity())
    
    try:
        # Check if user is the group owner
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if group.creator_id != user_id:
            return jsonify({'error': 'Only group owners can remove members'}), 403
        
        # Check if member exists
        member = GroupMember.query.filter_by(group_id=group_id, user_id=member_id).first()
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Prevent removing the owner
        if member_id == group.creator_id:
            return jsonify({'error': 'Cannot remove the group owner'}), 400
        
        # Remove member
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({'message': 'Member removed successfully'})
        
    except Exception as e:
        print(f"Error removing group member: {e}")
        return jsonify({'error': 'Failed to remove member'}), 500

@groups_bp.route('/api/groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    user_id = int(get_jwt_identity())
    
    try:
        # Get group
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        # Check if user is the group owner
        if group.creator_id != user_id:
            return jsonify({'error': 'Only group owners can delete groups'}), 403
        
        # Delete all group members
        GroupMember.query.filter_by(group_id=group_id).delete()
        
        # Delete the group
        db.session.delete(group)
        db.session.commit()
        
        return jsonify({'message': 'Group deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting group: {e}")
        return jsonify({'error': 'Failed to delete group'}), 500
