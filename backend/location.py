from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, LocationCheckin, User

location_bp = Blueprint('location_bp', __name__)

# POST: Create a location check-in
@location_bp.route('/api/groups/<int:group_id>/checkin', methods=['POST'])
@jwt_required()
def create_checkin(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Check if user is a member of the group
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    location_name = data.get('location_name')
    address = data.get('address')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    message = data.get('message')
    
    if not location_name:
        return jsonify({'error': 'Location name is required'}), 400
    
    checkin = LocationCheckin(
        group_id=group_id,
        user_id=user_id,
        location_name=location_name,
        address=address,
        latitude=latitude,
        longitude=longitude,
        message=message
    )
    
    db.session.add(checkin)
    db.session.commit()
    
    # Get user name for response
    user = User.query.get(user_id)
    user_name = user.name if user else f'User {user_id}'
    
    return jsonify({
        'message': 'Check-in created successfully',
        'checkin_id': checkin.id,
        'user_name': user_name,
        'location_name': checkin.location_name,
        'checkin_time': checkin.checkin_time.isoformat()
    }), 201

# GET: Get all check-ins for a group
@location_bp.route('/api/groups/<int:group_id>/checkins', methods=['GET'])
@jwt_required()
def get_group_checkins(group_id):
    user_id = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    checkins = LocationCheckin.query.filter_by(group_id=group_id).order_by(LocationCheckin.checkin_time.desc()).all()
    result = []
    
    for checkin in checkins:
        user = User.query.get(checkin.user_id)
        result.append({
            'id': checkin.id,
            'user_name': user.name if user else f'User {checkin.user_id}',
            'location_name': checkin.location_name,
            'address': checkin.address,
            'latitude': checkin.latitude,
            'longitude': checkin.longitude,
            'message': checkin.message,
            'checkin_time': checkin.checkin_time.isoformat()
        })
    
    return jsonify(result)

# GET: Get all check-ins for user's trips (dashboard)
@location_bp.route('/api/checkins/recent', methods=['GET'])
@jwt_required()
def get_recent_checkins():
    user_id = int(get_jwt_identity())
    
    # Get all groups the user is a member of
    user_groups = GroupMember.query.filter_by(user_id=user_id).all()
    group_ids = [member.group_id for member in user_groups]
    
    if not group_ids:
        return jsonify([])
    
    # Get recent check-ins from user's groups
    recent_checkins = LocationCheckin.query.filter(
        LocationCheckin.group_id.in_(group_ids)
    ).order_by(LocationCheckin.checkin_time.desc()).limit(10).all()
    
    result = []
    for checkin in recent_checkins:
        user = User.query.get(checkin.user_id)
        group = Group.query.get(checkin.group_id)
        
        result.append({
            'id': checkin.id,
            'user_name': user.name if user else f'User {checkin.user_id}',
            'group_name': group.name if group else 'Unknown Group',
            'group_id': checkin.group_id,
            'location_name': checkin.location_name,
            'address': checkin.address,
            'latitude': checkin.latitude,
            'longitude': checkin.longitude,
            'message': checkin.message,
            'checkin_time': checkin.checkin_time.isoformat()
        })
    
    return jsonify(result)
