from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Recommendation, GroupMember, Trip, Group

recommend_bp = Blueprint('recommend_bp', __name__)

# Trip-based recommendation endpoints
@recommend_bp.route('/api/trips/<int:trip_id>/recommendations', methods=['GET'])
@jwt_required()
def get_trip_recommendations(trip_id):
    """Get all recommendations for a trip"""
    user_id = int(get_jwt_identity())

    # Check if user owns the trip
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or access denied'}), 403

    # Get or create a group for this trip
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        return jsonify({'recommendations': []})  # No recommendations yet

    recs = Recommendation.query.filter_by(group_id=group.id).order_by(Recommendation.timestamp.desc()).all()
    result = [{
        'id': r.id,
        'title': r.title,
        'type': r.type,
        'comment': r.comment,
        'user_id': r.user_id,
        'timestamp': r.timestamp.isoformat()
    } for r in recs]

    return jsonify({'recommendations': result})

@recommend_bp.route('/api/trips/<int:trip_id>/recommendations', methods=['POST'])
@jwt_required()
def add_trip_recommendation(trip_id):
    """Add recommendation to a trip"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Check if user owns the trip
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or access denied'}), 403

    # Get or create a group for this trip
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        # Create default group for trip
        group = Group(
            name=f"{trip.name} Group",
            creator_id=user_id,
            trip_id=trip_id
        )
        db.session.add(group)
        db.session.flush()  # Get the ID
        
        # Add user as member
        member = GroupMember(group_id=group.id, user_id=user_id)
        db.session.add(member)

    rec = Recommendation(
        group_id=group.id,
        user_id=user_id,
        title=data.get('title'),
        type=data.get('type'),
        comment=data.get('comment')
    )
    db.session.add(rec)
    db.session.commit()

    return jsonify({
        'message': 'Recommendation added successfully',
        'recommendation': {
            'id': rec.id,
            'title': rec.title,
            'type': rec.type,
            'comment': rec.comment,
            'timestamp': rec.timestamp.isoformat()
        }
    }), 201

# Original group-based endpoints
# ✅ POST: Add recommendation to group
@recommend_bp.route('/api/groups/<int:group_id>/recommendations', methods=['POST'])
@jwt_required()
def add_recommendation(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Check if user is a group member
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403

    rec = Recommendation(
        group_id=group_id,
        user_id=user_id,
        title=data.get('title'),
        type=data.get('type'),
        comment=data.get('comment')
    )
    db.session.add(rec)
    db.session.commit()

    return jsonify({'message': 'Recommendation added'}), 201

# ✅ GET: View all group recommendations
@recommend_bp.route('/api/groups/<int:group_id>/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations(group_id):
    user_id = int(get_jwt_identity())

    # Check if user is a group member
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403

    recs = Recommendation.query.filter_by(group_id=group_id).order_by(Recommendation.timestamp.desc()).all()
    result = [{
        'title': r.title,
        'type': r.type,
        'comment': r.comment,
        'user_id': r.user_id,
        'timestamp': r.timestamp.isoformat()
    } for r in recs]

    return jsonify(result)
