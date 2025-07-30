print("TRIPS BLUEPRINT LOADED")
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trip, Group, GroupMember

trips_bp = Blueprint('trips_bp', __name__)

@trips_bp.route('/api/trips', methods=['POST'])
@jwt_required()
def create_trip():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Create the trip
    trip = Trip(
        user_id=user_id,
        name=data.get('name'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        description=data.get('description')
    )
    db.session.add(trip)
    db.session.commit()
    
    # Automatically create a default group for the trip
    default_group = Group(
        name=f"{trip.name} - Main Group",
        creator_id=user_id,
        trip_id=trip.id
    )
    db.session.add(default_group)
    db.session.commit()
    
    # Add the trip creator as the first group member
    creator_member = GroupMember(
        group_id=default_group.id,
        user_id=user_id
    )
    db.session.add(creator_member)
    db.session.commit()
    
    return jsonify({
        'message': 'Trip created with default group!', 
        'trip': {
            'id': trip.id,
            'name': trip.name,
            'start_date': trip.start_date,
            'end_date': trip.end_date,
            'description': trip.description
        },
        'group': {
            'id': default_group.id,
            'name': default_group.name
        }
    })

@trips_bp.route('/api/trips', methods=['GET'])
@jwt_required()
def get_trips():
    user_id = int(get_jwt_identity())
    
    # Get trips owned by the user
    owned_trips = Trip.query.filter_by(user_id=user_id).all()
    
    # Get trips where user is a member (through groups)
    member_trips = db.session.query(Trip).join(Group).join(GroupMember).filter(
        GroupMember.user_id == user_id,
        Trip.user_id != user_id  # Exclude trips they already own
    ).all()
    
    # Combine owned and member trips
    all_trips = owned_trips + member_trips
    
    # Remove duplicates and format response
    unique_trips = []
    seen_trip_ids = set()
    
    for trip in all_trips:
        if trip.id not in seen_trip_ids:
            seen_trip_ids.add(trip.id)
            unique_trips.append({
                'id': trip.id,
                'name': trip.name,
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'description': trip.description,
                'is_owner': trip.user_id == user_id,
                'role': 'Owner' if trip.user_id == user_id else 'Member'
            })
    
    return jsonify(unique_trips)

@trips_bp.route('/api/trips/<int:trip_id>/groups', methods=['GET'])
@jwt_required()
def get_trip_groups(trip_id):
    user_id = int(get_jwt_identity())
    
    # Verify user has access to this trip
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    
    # Check if user is owner or member
    is_owner = trip.user_id == user_id
    is_member = db.session.query(GroupMember).join(Group).filter(
        Group.trip_id == trip_id,
        GroupMember.user_id == user_id
    ).first()
    
    if not is_owner and not is_member:
        return jsonify({'error': 'You do not have access to this trip'}), 403
    
    # Get all groups for this trip
    groups = Group.query.filter_by(trip_id=trip_id).all()
    
    result = []
    for group in groups:
        # Get member count for each group
        member_count = GroupMember.query.filter_by(group_id=group.id).count()
        
        result.append({
            'id': group.id,
            'name': group.name,
            'creator_id': group.creator_id,
            'member_count': member_count,
            'is_owner': group.creator_id == user_id
        })
    
    return jsonify(result)

@trips_bp.route('/api/trips/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    user_id = int(get_jwt_identity())
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    data = request.get_json()
    trip.name = data.get('name', trip.name)
    trip.start_date = data.get('start_date', trip.start_date)
    trip.end_date = data.get('end_date', trip.end_date)
    trip.description = data.get('description', trip.description)
    db.session.commit()
    return jsonify({'message': 'Trip updated!'})

@trips_bp.route('/api/trips/<int:trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    user_id = int(get_jwt_identity())
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': 'Trip deleted!'})

# NEW: Add member directly to trip (adds to default group)
@trips_bp.route('/api/trips/<int:trip_id>/members', methods=['POST'])
@jwt_required()
def add_trip_member(trip_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify trip exists and user is the owner
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or unauthorized'}), 404
    
    # Get the default group for this trip
    default_group = Group.query.filter_by(trip_id=trip_id).first()
    if not default_group:
        return jsonify({'error': 'Default group not found for trip'}), 404
    
    # Get member email or user_id from request
    member_email = data.get('email')
    member_user_id = data.get('user_id')
    
    if member_email:
        # Find user by email
        from models import User
        member_user = User.query.filter_by(email=member_email).first()
        if not member_user:
            return jsonify({'error': 'User with this email not found'}), 404
        member_user_id = member_user.id
    elif not member_user_id:
        return jsonify({'error': 'Either email or user_id is required'}), 400
    
    # Check if already a member
    existing_member = GroupMember.query.filter_by(
        group_id=default_group.id, 
        user_id=member_user_id
    ).first()
    if existing_member:
        return jsonify({'error': 'User is already a member of this trip'}), 400
    
    # Add member to the default group
    new_member = GroupMember(
        group_id=default_group.id,
        user_id=member_user_id
    )
    db.session.add(new_member)
    db.session.commit()
    
    return jsonify({
        'message': 'Member added to trip successfully',
        'group_id': default_group.id
    })

# NEW: Get all members of a trip (from default group)
@trips_bp.route('/api/trips/<int:trip_id>/members', methods=['GET'])
@jwt_required()
def get_trip_members(trip_id):
    user_id = int(get_jwt_identity())
    
    # Verify trip exists and user has access (either owner or member)
    trip = Trip.query.get_or_404(trip_id)
    
    # Get the default group for this trip
    default_group = Group.query.filter_by(trip_id=trip_id).first()
    if not default_group:
        return jsonify({'error': 'Default group not found for trip'}), 404
    
    # Check if user is either trip owner or group member
    is_owner = trip.user_id == user_id
    is_member = GroupMember.query.filter_by(
        group_id=default_group.id, 
        user_id=user_id
    ).first() is not None
    
    if not (is_owner or is_member):
        return jsonify({'error': 'You must be a member or owner of this trip to view members'}), 403
    
    # Get all members with user details
    from models import User
    members = db.session.query(GroupMember, User).join(
        User, GroupMember.user_id == User.id
    ).filter(GroupMember.group_id == default_group.id).all()
    
    member_list = [{
        'user_id': member.user_id,
        'name': user.name,
        'email': user.email,
        'is_owner': member.user_id == trip.user_id
    } for member, user in members]
    
    return jsonify({
        'trip_id': trip_id,
        'trip_name': trip.name,
        'members': member_list,
        'total_members': len(member_list)
    })

print("TRIPS BLUEPRINT LOADED")
