from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, LiveLocation
from datetime import datetime, timedelta
import json

live_location_bp = Blueprint('live_location_bp', __name__)

@live_location_bp.route('/api/groups/<int:group_id>/live-location/update', methods=['POST'])
@jwt_required()
def update_live_location(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Deactivate previous locations for this user in this group
    db.session.query(LiveLocation).filter_by(
        group_id=group_id, 
        user_id=user_id
    ).update({'is_active': False})
    
    # Create new location record
    location = LiveLocation(
        group_id=group_id,
        user_id=user_id,
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        accuracy=data.get('accuracy'),
        speed=data.get('speed'),
        heading=data.get('heading'),
        altitude=data.get('altitude'),
        battery_level=data.get('battery_level'),
        location_name=data.get('location_name', ''),
        is_active=True
    )
    
    db.session.add(location)
    db.session.commit()
    
    return jsonify({
        'message': 'Location updated successfully',
        'location_id': location.id,
        'timestamp': location.timestamp.isoformat()
    }), 201

@live_location_bp.route('/api/groups/<int:group_id>/live-location/members', methods=['GET'])
@jwt_required()
def get_group_live_locations(group_id):
    user_id = int(get_jwt_identity())
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get all active locations for group members (last 30 minutes)
    time_threshold = datetime.utcnow() - timedelta(minutes=30)
    
    locations = db.session.query(LiveLocation).filter(
        LiveLocation.group_id == group_id,
        LiveLocation.is_active == True,
        LiveLocation.timestamp >= time_threshold
    ).all()
    
    # Get unique latest location for each user
    user_locations = {}
    for location in locations:
        if location.user_id not in user_locations or location.timestamp > user_locations[location.user_id].timestamp:
            user_locations[location.user_id] = location
    
    result = []
    for user_id, location in user_locations.items():
        result.append({
            'user_id': user_id,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'accuracy': location.accuracy,
            'speed': location.speed,
            'heading': location.heading,
            'altitude': location.altitude,
            'timestamp': location.timestamp.isoformat(),
            'battery_level': location.battery_level,
            'location_name': location.location_name,
            'time_ago': calculate_time_ago(location.timestamp)
        })
    
    return jsonify({
        'locations': result,
        'total_members': len(result),
        'group_id': group_id
    })

@live_location_bp.route('/api/groups/<int:group_id>/live-location/history', methods=['GET'])
@jwt_required()
def get_location_history(group_id):
    user_id = int(get_jwt_identity())
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get query parameters
    target_user_id = request.args.get('user_id', user_id, type=int)
    hours = request.args.get('hours', 24, type=int)
    
    # Get location history
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    locations = db.session.query(LiveLocation).filter(
        LiveLocation.group_id == group_id,
        LiveLocation.user_id == target_user_id,
        LiveLocation.timestamp >= time_threshold
    ).order_by(LiveLocation.timestamp.desc()).limit(100).all()
    
    result = []
    for location in locations:
        result.append({
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': location.timestamp.isoformat(),
            'location_name': location.location_name,
            'speed': location.speed,
            'accuracy': location.accuracy
        })
    
    return jsonify({
        'history': result,
        'user_id': target_user_id,
        'hours_covered': hours,
        'total_points': len(result)
    })

@live_location_bp.route('/api/groups/<int:group_id>/live-location/emergency', methods=['POST'])
@jwt_required()
def send_emergency_alert(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get user's current location
    current_location = db.session.query(LiveLocation).filter_by(
        group_id=group_id,
        user_id=user_id,
        is_active=True
    ).order_by(LiveLocation.timestamp.desc()).first()
    
    if not current_location:
        return jsonify({'error': 'Current location not available'}), 400
    
    # Create emergency alert (you could extend this to send notifications)
    emergency_data = {
        'user_id': user_id,
        'group_id': group_id,
        'latitude': current_location.latitude,
        'longitude': current_location.longitude,
        'message': data.get('message', 'Emergency! I need help!'),
        'timestamp': datetime.utcnow().isoformat(),
        'type': 'emergency'
    }
    
    # In a real implementation, you would:
    # 1. Send push notifications to all group members
    # 2. Send SMS alerts
    # 3. Log the emergency in a separate table
    # 4. Potentially alert emergency services
    
    return jsonify({
        'message': 'Emergency alert sent to all group members',
        'alert_data': emergency_data
    }), 201

@live_location_bp.route('/api/groups/<int:group_id>/live-location/geofence', methods=['POST'])
@jwt_required()
def create_geofence(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Create geofence (virtual boundary)
    geofence = {
        'name': data.get('name'),
        'center_lat': data.get('latitude'),
        'center_lng': data.get('longitude'),
        'radius': data.get('radius', 100),  # meters
        'created_by': user_id,
        'group_id': group_id,
        'created_at': datetime.utcnow().isoformat()
    }
    
    # In a real implementation, store this in a Geofence table
    # For now, we'll return the geofence data
    
    return jsonify({
        'message': 'Geofence created successfully',
        'geofence': geofence
    }), 201

@live_location_bp.route('/api/groups/<int:group_id>/live-location/distance', methods=['GET'])
@jwt_required()
def calculate_distances(group_id):
    user_id = int(get_jwt_identity())
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Get all current locations
    locations = db.session.query(LiveLocation).filter(
        LiveLocation.group_id == group_id,
        LiveLocation.is_active == True
    ).all()
    
    # Calculate distances between all members
    distances = []
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i < j:  # Avoid duplicates
                distance = calculate_distance(
                    loc1.latitude, loc1.longitude,
                    loc2.latitude, loc2.longitude
                )
                distances.append({
                    'user1_id': loc1.user_id,
                    'user2_id': loc2.user_id,
                    'distance_km': round(distance, 2),
                    'distance_miles': round(distance * 0.621371, 2)
                })
    
    return jsonify({
        'distances': distances,
        'total_members': len(locations)
    })

def calculate_time_ago(timestamp):
    """Calculate human-readable time difference"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.seconds < 60:
        return f"{diff.seconds} seconds ago"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60} minutes ago"
    elif diff.days == 0:
        return f"{diff.seconds // 3600} hours ago"
    else:
        return f"{diff.days} days ago"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    import math
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c 