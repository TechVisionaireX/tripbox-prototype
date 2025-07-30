print("GALLERY BLUEPRINT LOADED")
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Group, GroupMember, Photo
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import send_from_directory

gallery_bp = Blueprint('gallery_bp', __name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'uploads/photos'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@gallery_bp.route('/api/groups/<int:group_id>/photos', methods=['POST'])
@jwt_required()
def upload_photo(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Check if photo file is present
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo file provided'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400
    
    try:
        # Ensure upload folder exists
        ensure_upload_folder()
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{user_id}_{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Get caption from form data
        caption = request.form.get('caption', '').strip()
        
        # Create photo record
        photo = Photo(
            group_id=group_id,
            user_id=user_id,
            filename=unique_filename,
            caption=caption,
            upload_date=datetime.now()
        )
        
        db.session.add(photo)
        db.session.commit()
        
        # Get user info for response
        user = User.query.get(user_id)
        
        return jsonify({
            'message': 'Photo uploaded successfully',
            'photo': {
                'id': photo.id,
                'filename': photo.filename,
                'caption': photo.caption,
                'upload_date': photo.upload_date.isoformat(),
                'user_id': photo.user_id,
                'user_name': user.name,
                'url': f'/uploads/photos/{unique_filename}'
            }
        }), 201
        
    except Exception as e:
        print(f"Error uploading photo: {e}")
        return jsonify({'error': 'Failed to upload photo'}), 500

@gallery_bp.route('/api/groups/<int:group_id>/photos', methods=['GET'])
@jwt_required()
def get_group_photos(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is a member of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    try:
        # Get photos with user information
        photos = db.session.query(Photo, User).join(User).filter(
            Photo.group_id == group_id
        ).order_by(Photo.upload_date.desc()).all()
        
        result = []
        for photo, user in photos:
            result.append({
                'id': photo.id,
                'filename': photo.filename,
                'caption': photo.caption,
                'upload_date': photo.upload_date.isoformat(),
                'user_id': photo.user_id,
                'user_name': user.name,
                'user_email': user.email,
                'url': f'/uploads/photos/{photo.filename}'
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting photos: {e}")
        return jsonify({'error': 'Failed to get photos'}), 500

@gallery_bp.route('/api/photos/<int:photo_id>', methods=['DELETE'])
@jwt_required()
def delete_photo(photo_id):
    user_id = int(get_jwt_identity())
    
    # Get photo
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    
    # Check if user is the owner of the photo
    if photo.user_id != user_id:
        return jsonify({'error': 'You can only delete your own photos'}), 403
    
    try:
        # Delete file from filesystem
        filepath = os.path.join(UPLOAD_FOLDER, photo.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete from database
        db.session.delete(photo)
        db.session.commit()
        
        return jsonify({'message': 'Photo deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting photo: {e}")
        return jsonify({'error': 'Failed to delete photo'}), 500

@gallery_bp.route('/uploads/photos/<filename>')
def serve_photo(filename):
    """Serve uploaded photos"""
    return send_from_directory(UPLOAD_FOLDER, filename)
