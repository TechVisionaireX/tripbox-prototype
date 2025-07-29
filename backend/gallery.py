import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, GalleryImage, Trip, Group
from werkzeug.utils import secure_filename

gallery_bp = Blueprint('gallery_bp', __name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Trip-based gallery endpoints
@gallery_bp.route('/api/trips/<int:trip_id>/gallery', methods=['POST'])
@jwt_required()
def upload_trip_image(trip_id):
    """Upload image to a trip's gallery"""
    user_id = int(get_jwt_identity())
    
    # Check if user owns the trip
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or access denied'}), 403

    if 'image' not in request.files:
        return jsonify({'error': 'No image file part'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected image'}), 400

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

    filename = secure_filename(image.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    gallery = GalleryImage(group_id=group.id, user_id=user_id, filename=filename)
    db.session.add(gallery)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Image uploaded successfully',
        'filename': filename,
        'image': {
            'id': gallery.id,
            'filename': filename,
            'url': request.host_url + f'uploads/{filename}',
            'timestamp': gallery.timestamp.isoformat()
        }
    }), 201

@gallery_bp.route('/api/trips/<int:trip_id>/gallery', methods=['GET'])
@jwt_required()
def get_trip_images(trip_id):
    """Get all images for a trip"""
    user_id = int(get_jwt_identity())

    # Check if user owns the trip
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or access denied'}), 403

    # Get or create a group for this trip
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        return jsonify({'success': True, 'images': []})  # No images yet

    images = GalleryImage.query.filter_by(group_id=group.id).order_by(GalleryImage.timestamp.desc()).all()
    result = [{
        'id': img.id,
        'filename': img.filename,
        'url': request.host_url + f'uploads/{img.filename}',
        'timestamp': img.timestamp.isoformat()
    } for img in images]

    return jsonify({'success': True, 'images': result})

# Upload image
@gallery_bp.route('/api/groups/<int:group_id>/gallery', methods=['POST'])
@jwt_required()
def upload_image(group_id):
    user_id = int(get_jwt_identity())
    if 'image' not in request.files:
        return jsonify({'error': 'No image file part'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected image'}), 400

    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    filename = secure_filename(image.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    gallery = GalleryImage(group_id=group_id, user_id=user_id, filename=filename)
    db.session.add(gallery)
    db.session.commit()

    return jsonify({'message': 'Image uploaded', 'filename': filename}), 201

# List images
@gallery_bp.route('/api/groups/<int:group_id>/gallery', methods=['GET'])
@jwt_required()
def get_images(group_id):
    user_id = int(get_jwt_identity())
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403

    images = GalleryImage.query.filter_by(group_id=group_id).order_by(GalleryImage.timestamp.desc()).all()
    result = [{
        'filename': img.filename,
        'url': request.host_url + f'uploads/{img.filename}',
        'timestamp': img.timestamp.isoformat()
    } for img in images]

    return jsonify(result)

# Serve uploaded image file
@gallery_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
