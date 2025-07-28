from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Recommendation, GroupMember

recommend_bp = Blueprint('recommend_bp', __name__)

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
