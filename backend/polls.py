from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, Poll, PollVote, User
from notifications import create_group_notification
import json
from datetime import datetime, timedelta

polls_bp = Blueprint('polls_bp', __name__)

# POST: Create a new poll
@polls_bp.route('/api/groups/<int:group_id>/polls', methods=['POST'])
@jwt_required()
def create_poll(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    print(f"Creating poll for group {group_id} by user {user_id}")
    print(f"Request data: {data}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Check if user is a member of the group
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        print(f"User {user_id} is not a member of group {group_id}")
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    question = data.get('question')
    options = data.get('options', [])
    expires_in_hours = data.get('expires_in_hours', 24)  # Default 24 hours
    
    print(f"Question: {question}")
    print(f"Options: {options}")
    print(f"Expires in hours: {expires_in_hours}")
    
    if not question or not options or len(options) < 2:
        print(f"Validation failed: question={question}, options={options}")
        return jsonify({'error': 'Question and at least 2 options are required'}), 400
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    try:
        print(f"Creating Poll object with: group_id={group_id}, creator_id={user_id}, question={question}")
        print(f"Options JSON: {json.dumps(options)}")
        print(f"Expires at: {expires_at}")
        
        poll = Poll(
            group_id=group_id,
            creator_id=user_id,
            question=question,
            options=json.dumps(options),
            expires_at=expires_at,
            is_active=True,
            is_finalized=False
        )
        
        print(f"Poll object created: {poll}")
        db.session.add(poll)
        print("Poll added to session")
        db.session.commit()
        print(f"Poll committed successfully with ID {poll.id}")
        
        # Create notifications for all group members
        try:
            create_group_notification(
                group_id=group_id,
                notification_type='poll_created',
                title='New Poll Created',
                message=f'A new poll "{question}" has been created in your group.',
                exclude_user_id=user_id
            )
            print("Notification created successfully")
        except Exception as notif_error:
            print(f"Error creating notification: {notif_error}")
        
        return jsonify({
            'message': 'Poll created successfully',
            'poll_id': poll.id,
            'question': poll.question,
            'options': options,
            'expires_at': poll.expires_at.isoformat()
        }), 201
        
    except Exception as e:
        print(f"Error creating poll: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Error traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Failed to create poll: {str(e)}'}), 500

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
    
    # Create notification for poll creator
    poll = Poll.query.get(poll_id)
    if poll and poll.creator_id != user_id:
        from notifications import create_notification
        create_notification(
            user_id=poll.creator_id,
            group_id=poll.group_id,
            notification_type='poll_voted',
            title='New Vote Cast',
            message=f'Someone voted on your poll "{poll.question}".'
        )
    
    return jsonify({'message': 'Vote recorded successfully'}), 200

# GET: Get all active polls for user's trips (dashboard)
@polls_bp.route('/api/polls/active', methods=['GET'])
@jwt_required()
def get_active_polls():
    user_id = int(get_jwt_identity())
    
    print(f"Getting active polls for user {user_id}")
    
    # Get all groups the user is a member of
    user_groups = GroupMember.query.filter_by(user_id=user_id).all()
    group_ids = [member.group_id for member in user_groups]
    
    print(f"User is member of groups: {group_ids}")
    
    if not group_ids:
        print("No groups found for user")
        return jsonify([])
    
    # Get active polls from user's groups (include polls that are not finalized)
    active_polls = Poll.query.filter(
        Poll.group_id.in_(group_ids),
        Poll.is_finalized == False
    ).order_by(Poll.created_at.desc()).all()
    
    print(f"Found {len(active_polls)} active polls")
    
    result = []
    for poll in active_polls:
        print(f"Processing poll {poll.id}: {poll.question}")
        print(f"Poll is_active: {poll.is_active}, is_finalized: {poll.is_finalized}")
        
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
    
    print(f"Returning {len(result)} polls")
    return jsonify(result)

# Debug endpoint to check poll status
@polls_bp.route('/api/polls/debug', methods=['GET'])
@jwt_required()
def debug_polls():
    user_id = int(get_jwt_identity())
    
    print(f"Debug: Getting poll info for user {user_id}")
    
    # Get all groups the user is a member of
    user_groups = GroupMember.query.filter_by(user_id=user_id).all()
    group_ids = [member.group_id for member in user_groups]
    
    print(f"Debug: User groups: {group_ids}")
    
    # Get all polls in user's groups
    all_polls = Poll.query.filter(Poll.group_id.in_(group_ids)).all()
    
    debug_info = {
        'user_id': user_id,
        'user_groups': group_ids,
        'total_polls': len(all_polls),
        'polls': []
    }
    
    for poll in all_polls:
        poll_info = {
            'id': poll.id,
            'question': poll.question,
            'group_id': poll.group_id,
            'is_active': poll.is_active,
            'is_finalized': poll.is_finalized,
            'created_at': poll.created_at.isoformat(),
            'creator_id': poll.creator_id
        }
        debug_info['polls'].append(poll_info)
        print(f"Debug: Poll {poll.id} - active: {poll.is_active}, finalized: {poll.is_finalized}")
    
    return jsonify(debug_info)

# Utility endpoint to fix poll status (for debugging)
@polls_bp.route('/api/polls/fix-status', methods=['POST'])
@jwt_required()
def fix_poll_status():
    user_id = int(get_jwt_identity())
    
    # Only allow admin or creator to fix poll status
    user = User.query.get(user_id)
    if not user or user.email != 'tt@gmail.com':  # Only allow specific user for now
        return jsonify({'error': 'Not authorized'}), 403
    
    # Get all polls and fix their status
    all_polls = Poll.query.all()
    fixed_count = 0
    
    for poll in all_polls:
        if poll.is_finalized and poll.is_active:
            # If finalized, should not be active
            poll.is_active = False
            fixed_count += 1
        elif not poll.is_finalized and not poll.is_active:
            # If not finalized, should be active
            poll.is_active = True
            fixed_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Fixed {fixed_count} polls',
        'total_polls': len(all_polls),
        'fixed_count': fixed_count
    })

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
    
    # Create notifications for all group members
    create_group_notification(
        group_id=poll.group_id,
        notification_type='poll_finalized',
        title='Poll Finalized',
        message=f'The poll "{poll.question}" has been finalized. Winner: {winning_option}',
        exclude_user_id=user_id
    )
    
    return jsonify({
        'message': 'Poll finalized successfully',
        'winning_option': winning_option,
        'total_votes': sum(PollVote.query.filter_by(poll_id=poll_id).count() for _ in range(1))
    }), 200 