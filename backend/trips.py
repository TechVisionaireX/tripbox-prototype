print("TRIPS BLUEPRINT LOADED")
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trip

trips_bp = Blueprint('trips_bp', __name__)

@trips_bp.route('/api/trips', methods=['POST'])
@jwt_required()
def create_trip():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    trip = Trip(
        user_id=user_id,
        name=data.get('name'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        description=data.get('description')
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify({'message': 'Trip created!', 'trip': {
        'id': trip.id,
        'name': trip.name,
        'start_date': trip.start_date,
        'end_date': trip.end_date,
        'description': trip.description
    }})

@trips_bp.route('/api/trips', methods=['GET'])
@jwt_required()
def get_trips():
    user_id = int(get_jwt_identity())
    trips = Trip.query.filter_by(user_id=user_id).all()
    trips_list = [{
        'id': t.id,
        'name': t.name,
        'start_date': t.start_date,
        'end_date': t.end_date,
        'description': t.description
    } for t in trips]
    return jsonify(trips_list)

@trips_bp.route('/api/trips/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    user_id = int(get_jwt_identity())
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    data = request.get_json()
    trip.name = data.get('name', trip.name)
    trip.start_date = data.get('start_date', trip.start_date)
    trip.end_date = data.get('end_date', trip.end_date)
    trip.description = data.get('description', trip.description)
    db.session.commit()
    return jsonify({'message': 'Trip updated!'})

@trips_bp.route('/api/trips/<int:trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    user_id = int(get_jwt_identity())
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': 'Trip deleted!'})

print("TRIPS BLUEPRINT LOADED")
