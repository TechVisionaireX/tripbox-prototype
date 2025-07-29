from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, LocationCheckin
from datetime import datetime

location_bp = Blueprint('location_bp', __name__)

# ✅ POST /api/groups/<group_id>/location
@location_bp.route('/api/groups/<int:group_id>/location', methods=['POST'])
@jwt_required()
def checkin(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        return jsonify({"error": "Unauthorized"}), 403

    checkin = LocationCheckin(
        group_id=group_id,
        user_id=user_id,
        message=data.get('message', 'I’m here!')
    )
    db.session.add(checkin)
    db.session.commit()
    return jsonify({"message": "Location check-in recorded"}), 201

# ✅ GET /api/groups/<group_id>/location
@location_bp.route('/api/groups/<int:group_id>/location', methods=['GET'])
@jwt_required()
def view_checkins(group_id):
    user_id = int(get_jwt_identity())

    if not GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first():
        return jsonify({"error": "Unauthorized"}), 403

    checkins = LocationCheckin.query.filter_by(group_id=group_id).order_by(LocationCheckin.timestamp.desc()).all()
    return jsonify([{
        "user_id": c.user_id,
        "message": c.message,
        "timestamp": c.timestamp.isoformat()
    } for c in checkins])
