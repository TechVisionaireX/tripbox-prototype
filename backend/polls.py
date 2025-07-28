from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db, Poll, Group, GroupMember, RecommendationVote, Recommendation
import json
from datetime import datetime, timedelta

polls_bp = Blueprint('polls_bp', __name__)

@polls_bp.route('/api/groups/<int:group_id>/polls', methods=['GET'])
@jwt_required()
def get_polls(group_id):
    """Get all polls for a group"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        polls = Poll.query.filter_by(group_id=group_id).order_by(Poll.timestamp.desc()).all()
        
        return jsonify({
            'polls': [{
                'id': poll.id,
                'question': poll.question,
                'options': json.loads(poll.options) if poll.options else [],
                'votes': json.loads(poll.votes) if poll.votes else {},
                'is_active': poll.is_active,
                'multiple_choice': poll.multiple_choice,
                'timestamp': poll.timestamp.isoformat() if poll.timestamp else None,
                'expires_at': poll.expires_at.isoformat() if poll.expires_at else None
            } for poll in polls]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/api/groups/<int:group_id>/polls', methods=['POST'])
@jwt_required()
def create_poll(group_id):
    """Create new poll"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Set expiry date if provided
        expires_at = None
        if data.get('expires_in_hours'):
            expires_at = datetime.utcnow() + timedelta(hours=int(data['expires_in_hours']))
        
        poll = Poll(
            group_id=group_id,
            user_id=current_user_id,
            question=data.get('question'),
            options=json.dumps(data.get('options', [])),
            votes=json.dumps({}),
            multiple_choice=data.get('multiple_choice', False),
            expires_at=expires_at
        )
        
        db.session.add(poll)
        db.session.commit()
        
        return jsonify({
            'message': 'Poll created successfully',
            'poll': {
                'id': poll.id,
                'question': poll.question,
                'options': json.loads(poll.options),
                'votes': {},
                'is_active': poll.is_active,
                'multiple_choice': poll.multiple_choice
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/api/polls/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_in_poll(poll_id):
    """Vote in a poll"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        poll = Poll.query.get_or_404(poll_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=poll.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if poll is active and not expired
        if not poll.is_active:
            return jsonify({'error': 'Poll is not active'}), 400
        
        if poll.expires_at and datetime.utcnow() > poll.expires_at:
            return jsonify({'error': 'Poll has expired'}), 400
        
        # Get current votes
        votes = json.loads(poll.votes) if poll.votes else {}
        
        # Update user's vote
        user_vote = data.get('option_index')
        if poll.multiple_choice and isinstance(user_vote, list):
            votes[str(current_user_id)] = user_vote
        else:
            votes[str(current_user_id)] = user_vote
        
        poll.votes = json.dumps(votes)
        db.session.commit()
        
        return jsonify({
            'message': 'Vote recorded successfully',
            'votes': votes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/api/polls/<int:poll_id>/close', methods=['POST'])
@jwt_required()
def close_poll(poll_id):
    """Close a poll"""
    try:
        current_user_id = get_jwt_identity()
        
        poll = Poll.query.get_or_404(poll_id)
        
        # Check if user is the creator or group admin
        if poll.user_id != current_user_id:
            return jsonify({'error': 'Only poll creator can close poll'}), 403
        
        poll.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Poll closed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/api/recommendations/<int:recommendation_id>/vote', methods=['POST'])
@jwt_required()
def vote_on_recommendation(recommendation_id):
    """Vote on a recommendation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        recommendation = Recommendation.query.get_or_404(recommendation_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=recommendation.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if user already voted
        existing_vote = RecommendationVote.query.filter_by(
            recommendation_id=recommendation_id,
            user_id=current_user_id
        ).first()
        
        if existing_vote:
            # Update existing vote
            existing_vote.vote = data.get('vote')
            existing_vote.comment = data.get('comment')
        else:
            # Create new vote
            vote = RecommendationVote(
                recommendation_id=recommendation_id,
                user_id=current_user_id,
                vote=data.get('vote'),
                comment=data.get('comment')
            )
            db.session.add(vote)
        
        db.session.commit()
        
        return jsonify({'message': 'Vote recorded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@polls_bp.route('/api/recommendations/<int:recommendation_id>/votes', methods=['GET'])
@jwt_required()
def get_recommendation_votes(recommendation_id):
    """Get votes for a recommendation"""
    try:
        current_user_id = get_jwt_identity()
        
        recommendation = Recommendation.query.get_or_404(recommendation_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=recommendation.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        votes = RecommendationVote.query.filter_by(recommendation_id=recommendation_id).all()
        
        return jsonify({
            'votes': [{
                'user_id': vote.user_id,
                'vote': vote.vote,
                'comment': vote.comment,
                'timestamp': vote.timestamp.isoformat() if vote.timestamp else None
            } for vote in votes]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 