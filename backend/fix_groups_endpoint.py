from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trip, Group, GroupMember

fix_groups_bp = Blueprint('fix_groups_bp', __name__)

@fix_groups_bp.route('/api/fix-missing-groups', methods=['POST'])
@jwt_required()
def fix_missing_groups():
    """Fix missing default groups for trips"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get all trips
        trips = Trip.query.all()
        print(f"Found {len(trips)} trips")
        
        # Get all groups
        groups = Group.query.all()
        print(f"Found {len(groups)} groups")
        
        # Find trips without default groups
        trips_with_groups = set(g.trip_id for g in groups)
        trips_without_groups = [t for t in trips if t.id not in trips_with_groups]
        
        print(f"Trips without default groups: {len(trips_without_groups)}")
        
        fixed_trips = []
        for trip in trips_without_groups:
            print(f"Creating default group for Trip {trip.id}: {trip.name}")
            
            # Create default group
            default_group = Group(
                name=f"{trip.name} - Main Group",
                creator_id=trip.user_id,
                trip_id=trip.id
            )
            db.session.add(default_group)
            db.session.commit()
            
            # Add trip creator as first member
            creator_member = GroupMember(
                group_id=default_group.id,
                user_id=trip.user_id
            )
            db.session.add(creator_member)
            db.session.commit()
            
            fixed_trips.append({
                'trip_id': trip.id,
                'trip_name': trip.name,
                'group_id': default_group.id,
                'group_name': default_group.name
            })
            
            print(f"✅ Created group {default_group.id} for trip {trip.id}")
        
        return jsonify({
            'message': f'Fixed {len(fixed_trips)} trips',
            'fixed_trips': fixed_trips
        })
        
    except Exception as e:
        print(f"Error fixing groups: {str(e)}")
        return jsonify({'error': f'Failed to fix groups: {str(e)}'}), 500 