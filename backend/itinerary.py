from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db, ItineraryItem, Group, GroupMember
import json

itinerary_bp = Blueprint('itinerary_bp', __name__)

@itinerary_bp.route('/api/groups/<int:group_id>/itinerary', methods=['GET'])
@jwt_required()
def get_itinerary(group_id):
    """Get all itinerary items for a group"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        items = ItineraryItem.query.filter_by(group_id=group_id).order_by(ItineraryItem.date, ItineraryItem.time).all()
        
        return jsonify({
            'itinerary': [{
                'id': item.id,
                'type': item.type,
                'title': item.title,
                'description': item.description,
                'location': item.location,
                'date': item.date,
                'time': item.time,
                'cost': item.cost,
                'booking_reference': item.booking_reference,
                'confirmed': item.confirmed,
                'timestamp': item.timestamp.isoformat() if item.timestamp else None
            } for item in items]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@itinerary_bp.route('/api/groups/<int:group_id>/itinerary', methods=['POST'])
@jwt_required()
def add_itinerary_item(group_id):
    """Add new itinerary item"""
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
        
        item = ItineraryItem(
            group_id=group_id,
            user_id=current_user_id,
            type=data.get('type'),
            title=data.get('title'),
            description=data.get('description'),
            location=data.get('location'),
            date=data.get('date'),
            time=data.get('time'),
            cost=data.get('cost'),
            booking_reference=data.get('booking_reference'),
            confirmed=data.get('confirmed', False)
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'message': 'Itinerary item added successfully',
            'item': {
                'id': item.id,
                'type': item.type,
                'title': item.title,
                'description': item.description,
                'location': item.location,
                'date': item.date,
                'time': item.time,
                'cost': item.cost,
                'booking_reference': item.booking_reference,
                'confirmed': item.confirmed
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@itinerary_bp.route('/api/itinerary/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_itinerary_item(item_id):
    """Update itinerary item"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        item = ItineraryItem.query.get_or_404(item_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=item.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update fields
        if 'title' in data:
            item.title = data['title']
        if 'description' in data:
            item.description = data['description']
        if 'location' in data:
            item.location = data['location']
        if 'date' in data:
            item.date = data['date']
        if 'time' in data:
            item.time = data['time']
        if 'cost' in data:
            item.cost = data['cost']
        if 'booking_reference' in data:
            item.booking_reference = data['booking_reference']
        if 'confirmed' in data:
            item.confirmed = data['confirmed']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Itinerary item updated successfully',
            'item': {
                'id': item.id,
                'type': item.type,
                'title': item.title,
                'description': item.description,
                'location': item.location,
                'date': item.date,
                'time': item.time,
                'cost': item.cost,
                'booking_reference': item.booking_reference,
                'confirmed': item.confirmed
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@itinerary_bp.route('/api/itinerary/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_itinerary_item(item_id):
    """Delete itinerary item"""
    try:
        current_user_id = get_jwt_identity()
        
        item = ItineraryItem.query.get_or_404(item_id)
        
        # Check if user is member of group
        membership = GroupMember.query.filter_by(
            group_id=item.group_id, 
            user_id=current_user_id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Itinerary item deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 