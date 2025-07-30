from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, Poll, PollVote, User
import json
from datetime import datetime, timedelta

polls_bp = Blueprint('polls_bp', __name__)

# POST: Create a new poll
@polls_bp.route('/api/groups/<int:group_id>/polls', methods=['POST'])
@jwt_required()
def create_poll(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Check if user is a member of the group
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    question = data.get('question')
    options = data.get('options', [])
    expires_in_hours = data.get('expires_in_hours', 24)  # Default 24 hours
    
    if not question or not options or len(options) < 2:
        return jsonify({'error': 'Question and at least 2 options are required'}), 400
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    poll = Poll(
        group_id=group_id,
        creator_id=user_id,
        question=question,
        options=json.dumps(options),
        expires_at=expires_at
    )
    
    db.session.add(poll)
    db.session.commit()
    
    return jsonify({
        'message': 'Poll created successfully',
        'poll_id': poll.id,
        'question': poll.question,
        'options': options,
        'expires_at': poll.expires_at.isoformat()
    }), 201

# GET: Get all polls for a group
@polls_bp.route('/api/groups/<int:group_id>/polls', methods=['GET'])
@jwt_required()
def get_group_polls(group_id):
    user_id = int(get_jwt_identity())
    
    # Check membership
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    polls = Poll.query.filter_by(group_id=group_id).order_by(Poll.created_at.desc()).all()
    result = []
    
    for poll in polls:
        # Get vote counts for each option
        options = json.loads(poll.options)
        vote_counts = {}
        user_vote = None
        
        for option in options:
            vote_count = PollVote.query.filter_by(poll_id=poll.id, selected_option=option).count()
            vote_counts[option] = vote_count
            
            # Check if current user has voted for this option
            if PollVote.query.filter_by(poll_id=poll.id, user_id=user_id, selected_option=option).first():
                user_vote = option
        
        # Get all votes with voter names
        votes = PollVote.query.filter_by(poll_id=poll.id).all()
        vote_details = []
        for vote in votes:
            voter = User.query.get(vote.user_id)
            vote_details.append({
                'voter_name': voter.name if voter else f'User {vote.user_id}',
                'selected_option': vote.selected_option,
                'voted_at': vote.voted_at.isoformat()
            })
        
        result.append({
            'id': poll.id,
            'question': poll.question,
            'options': options,
            'vote_counts': vote_counts,
            'user_vote': user_vote,
            'vote_details': vote_details,
            'is_active': poll.is_active,
            'is_finalized': poll.is_finalized,
            'winning_option': poll.winning_option,
            'created_at': poll.created_at.isoformat(),
            'expires_at': poll.expires_at.isoformat() if poll.expires_at else None,
            'creator_name': User.query.get(poll.creator_id).name if User.query.get(poll.creator_id) else 'Unknown'
        })
    
    return jsonify(result)

# POST: Vote on a poll
@polls_bp.route('/api/polls/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_on_poll(poll_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    selected_option = data.get('selected_option')
    
    if not selected_option:
        return jsonify({'error': 'Selected option is required'}), 400
    
    # Get poll and check if user is a member of the group
    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({'error': 'Poll not found'}), 404
    
    membership = GroupMember.query.filter_by(group_id=poll.group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    if not poll.is_active:
        return jsonify({'error': 'This poll is no longer active'}), 400
    
    # Check if user has already voted
    existing_vote = PollVote.query.filter_by(poll_id=poll_id, user_id=user_id).first()
    if existing_vote:
        # Update existing vote
        existing_vote.selected_option = selected_option
        existing_vote.voted_at = datetime.utcnow()
    else:
        # Create new vote
        vote = PollVote(poll_id=poll_id, user_id=user_id, selected_option=selected_option)
        db.session.add(vote)
    
    db.session.commit()
    
    return jsonify({'message': 'Vote recorded successfully'}), 200

# GET: Get all active polls for user's trips (dashboard)
@polls_bp.route('/api/polls/active', methods=['GET'])
@jwt_required()
def get_active_polls():
    user_id = int(get_jwt_identity())
    
    # Get all groups the user is a member of
    user_groups = GroupMember.query.filter_by(user_id=user_id).all()
    group_ids = [member.group_id for member in user_groups]
    
    if not group_ids:
        return jsonify([])
    
    # Get active polls from user's groups
    active_polls = Poll.query.filter(
        Poll.group_id.in_(group_ids),
        Poll.is_active == True
    ).order_by(Poll.created_at.desc()).all()
    
    result = []
    for poll in active_polls:
        # Get vote counts and user's vote
        options = json.loads(poll.options)
        vote_counts = {}
        user_vote = None
        
        for option in options:
            vote_count = PollVote.query.filter_by(poll_id=poll.id, selected_option=option).count()
            vote_counts[option] = vote_count
            
            if PollVote.query.filter_by(poll_id=poll.id, user_id=user_id, selected_option=option).first():
                user_vote = option
        
        # Get group name
        group = Group.query.get(poll.group_id)
        group_name = group.name if group else 'Unknown Group'
        
        result.append({
            'id': poll.id,
            'question': poll.question,
            'options': options,
            'vote_counts': vote_counts,
            'user_vote': user_vote,
            'group_name': group_name,
            'group_id': poll.group_id,
            'created_at': poll.created_at.isoformat(),
            'expires_at': poll.expires_at.isoformat() if poll.expires_at else None,
            'creator_name': User.query.get(poll.creator_id).name if User.query.get(poll.creator_id) else 'Unknown'
        })
    
    return jsonify(result)

# POST: Finalize a poll (only creator can finalize)
@polls_bp.route('/api/polls/<int:poll_id>/finalize', methods=['POST'])
@jwt_required()
def finalize_poll(poll_id):
    user_id = int(get_jwt_identity())
    
    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({'error': 'Poll not found'}), 404
    
    if poll.creator_id != user_id:
        return jsonify({'error': 'Only the poll creator can finalize the poll'}), 403
    
    if poll.is_finalized:
        return jsonify({'error': 'Poll is already finalized'}), 400
    
    # Calculate winning option
    options = json.loads(poll.options)
    max_votes = 0
    winning_option = None
    
    for option in options:
        vote_count = PollVote.query.filter_by(poll_id=poll_id, selected_option=option).count()
        if vote_count > max_votes:
            max_votes = vote_count
            winning_option = option
    
    poll.is_finalized = True
    poll.is_active = False
    poll.winning_option = winning_option
    
    db.session.commit()
    
    return jsonify({
        'message': 'Poll finalized successfully',
        'winning_option': winning_option,
        'total_votes': sum(PollVote.query.filter_by(poll_id=poll_id).count() for _ in range(1))
    }), 200 