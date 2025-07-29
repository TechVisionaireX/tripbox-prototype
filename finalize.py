from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trip, Group, GroupMember, ChecklistItem, BudgetItem, Recommendation

finalize_bp = Blueprint('finalize_bp', __name__)

# ✅ Finalize a trip
@finalize_bp.route('/api/trips/<int:trip_id>/finalize', methods=['PATCH'])
@jwt_required()
def finalize_trip(trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    trip.finalized = True
    db.session.commit()
    return jsonify({"message": "Trip finalized successfully"}), 200

# ✅ Trip Summary Endpoint
@finalize_bp.route('/api/trips/<int:trip_id>/summary', methods=['GET'])
@jwt_required()
def trip_summary(trip_id):
    trip = Trip.query.get(trip_id)
    if not trip or not trip.finalized:
        return jsonify({"error": "Trip not finalized or not found"}), 400

    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        return jsonify({"error": "Group not found"}), 404

    members = [m.user_id for m in GroupMember.query.filter_by(group_id=group.id).all()]
    checklist = ChecklistItem.query.filter_by(group_id=group.id).all()
    expenses = BudgetItem.query.filter_by(group_id=group.id).all()
    recs = Recommendation.query.filter_by(group_id=group.id).all()

    return jsonify({
        "trip": {
            "id": trip.id,
            "name": trip.name,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "description": trip.description,
            "finalized": trip.finalized
        },
        "group": {
            "group_id": group.id,
            "members": members
        },
        "checklist": [
            {
                "id": i.id,
                "text": i.text,
                "completed": i.completed
            } for i in checklist
        ],
        "expenses": {
            "total": sum(e.amount for e in expenses),
            "items": [
                {
                    "id": e.id,
                    "amount": e.amount,
                    "category": e.category
                } for e in expenses
            ]
        },
        "recommendations": [
            {
                "id": r.id,
                "title": r.title,
                "type": r.type
            } for r in recs
        ]
    }), 200
