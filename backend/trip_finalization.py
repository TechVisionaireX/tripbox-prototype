from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db, TripFinalization, Trip, Group, GroupMember, ItineraryItem, Recommendation, RecommendationVote, Expense
import json

trip_finalization_bp = Blueprint('trip_finalization_bp', __name__)

@trip_finalization_bp.route('/api/trips/<int:trip_id>/finalize', methods=['POST'])
@jwt_required()
def finalize_trip(trip_id):
    """Finalize a trip - Lock all plans and create summary"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        trip = Trip.query.get_or_404(trip_id)
        
        # Get the group associated with this trip
        group = Group.query.filter_by(trip_id=trip_id).first()
        if not group:
            return jsonify({'error': 'No group found for this trip'}), 404
        
        # Check if user is group creator or member
        membership = GroupMember.query.filter_by(
            group_id=group.id, 
            user_id=current_user_id
        ).first()
        
        if not membership and group.creator_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if already finalized
        existing_finalization = TripFinalization.query.filter_by(trip_id=trip_id).first()
        if existing_finalization:
            return jsonify({'error': 'Trip already finalized'}), 400
        
        # Gather all final data
        # 1. Final Itinerary (only confirmed items)
        confirmed_itinerary = ItineraryItem.query.filter_by(
            group_id=group.id, 
            confirmed=True
        ).order_by(ItineraryItem.date, ItineraryItem.time).all()
        
        final_itinerary = [{
            'id': item.id,
            'type': item.type,
            'title': item.title,
            'description': item.description,
            'location': item.location,
            'date': item.date,
            'time': item.time,
            'cost': item.cost,
            'booking_reference': item.booking_reference
        } for item in confirmed_itinerary]
        
        # 2. Approved Recommendations
        approved_recommendations = []
        recommendations = Recommendation.query.filter_by(group_id=group.id).all()
        
        for rec in recommendations:
            votes = RecommendationVote.query.filter_by(recommendation_id=rec.id).all()
            approve_count = len([v for v in votes if v.vote == 'approve'])
            reject_count = len([v for v in votes if v.vote == 'reject'])
            
            if approve_count > reject_count:
                approved_recommendations.append({
                    'id': rec.id,
                    'title': rec.title,
                    'type': rec.type,
                    'comment': rec.comment,
                    'votes': {
                        'approve': approve_count,
                        'reject': reject_count
                    }
                })
        
        # 3. Final Budget
        expenses = Expense.query.filter_by(group_id=group.id).all()
        total_expenses = sum([exp.amount for exp in expenses])
        
        # 4. Create summary
        summary = f"""
        Trip: {trip.name}
        Duration: {trip.start_date} to {trip.end_date}
        
        Final Itinerary:
        - {len(final_itinerary)} confirmed activities/bookings
        - Total estimated cost: ${sum([item.get('cost', 0) for item in final_itinerary if item.get('cost')])}
        
        Approved Recommendations:
        - {len(approved_recommendations)} group-approved suggestions
        
        Total Expenses Tracked:
        - ${total_expenses}
        
        Group Members: {len(GroupMember.query.filter_by(group_id=group.id).all()) + 1}
        
        This trip has been finalized and locked. No further changes can be made to the core itinerary.
        """
        
        # Create finalization record
        finalization = TripFinalization(
            trip_id=trip_id,
            group_id=group.id,
            finalized_by=current_user_id,
            final_itinerary=json.dumps(final_itinerary),
            final_budget=total_expenses,
            final_recommendations=json.dumps(approved_recommendations),
            summary=summary.strip()
        )
        
        db.session.add(finalization)
        
        # Mark trip as finalized
        trip.finalized = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Trip finalized successfully - Welcome to Eternity!',
            'finalization': {
                'id': finalization.id,
                'summary': finalization.summary,
                'final_budget': finalization.final_budget,
                'final_itinerary': final_itinerary,
                'approved_recommendations': approved_recommendations,
                'timestamp': finalization.timestamp.isoformat()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trip_finalization_bp.route('/api/trips/<int:trip_id>/finalization', methods=['GET'])
@jwt_required()
def get_trip_finalization(trip_id):
    """Get finalization details for a trip"""
    try:
        current_user_id = get_jwt_identity()
        
        trip = Trip.query.get_or_404(trip_id)
        
        # Get the group associated with this trip
        group = Group.query.filter_by(trip_id=trip_id).first()
        if not group:
            return jsonify({'error': 'No group found for this trip'}), 404
        
        # Check if user is member
        membership = GroupMember.query.filter_by(
            group_id=group.id, 
            user_id=current_user_id
        ).first()
        
        if not membership and group.creator_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        finalization = TripFinalization.query.filter_by(trip_id=trip_id).first()
        
        if not finalization:
            return jsonify({'error': 'Trip not yet finalized'}), 404
        
        return jsonify({
            'finalization': {
                'id': finalization.id,
                'summary': finalization.summary,
                'final_budget': finalization.final_budget,
                'final_itinerary': json.loads(finalization.final_itinerary) if finalization.final_itinerary else [],
                'approved_recommendations': json.loads(finalization.final_recommendations) if finalization.final_recommendations else [],
                'timestamp': finalization.timestamp.isoformat(),
                'finalized_by': finalization.finalized_by
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trip_finalization_bp.route('/api/trips/<int:trip_id>/preview-finalization', methods=['GET'])
@jwt_required()
def preview_trip_finalization(trip_id):
    """Preview what will be included in trip finalization"""
    try:
        current_user_id = get_jwt_identity()
        
        trip = Trip.query.get_or_404(trip_id)
        
        # Get the group associated with this trip
        group = Group.query.filter_by(trip_id=trip_id).first()
        if not group:
            return jsonify({'error': 'No group found for this trip'}), 404
        
        # Check if user is member
        membership = GroupMember.query.filter_by(
            group_id=group.id, 
            user_id=current_user_id
        ).first()
        
        if not membership and group.creator_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get confirmed itinerary items
        confirmed_items = ItineraryItem.query.filter_by(
            group_id=group.id, 
            confirmed=True
        ).count()
        
        unconfirmed_items = ItineraryItem.query.filter_by(
            group_id=group.id, 
            confirmed=False
        ).count()
        
        # Get recommendation voting status
        recommendations = Recommendation.query.filter_by(group_id=group.id).all()
        approved_count = 0
        pending_count = 0
        
        for rec in recommendations:
            votes = RecommendationVote.query.filter_by(recommendation_id=rec.id).all()
            approve_count = len([v for v in votes if v.vote == 'approve'])
            reject_count = len([v for v in votes if v.vote == 'reject'])
            
            if approve_count > reject_count:
                approved_count += 1
            elif approve_count == reject_count or (approve_count == 0 and reject_count == 0):
                pending_count += 1
        
        # Get budget info
        expenses = Expense.query.filter_by(group_id=group.id).all()
        total_expenses = sum([exp.amount for exp in expenses])
        
        return jsonify({
            'preview': {
                'trip_name': trip.name,
                'duration': f"{trip.start_date} to {trip.end_date}",
                'confirmed_itinerary_items': confirmed_items,
                'unconfirmed_itinerary_items': unconfirmed_items,
                'approved_recommendations': approved_count,
                'pending_recommendations': pending_count,
                'total_expenses': total_expenses,
                'is_ready_to_finalize': confirmed_items > 0 or approved_count > 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 