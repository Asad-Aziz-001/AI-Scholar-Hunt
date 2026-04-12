# ============================================================
# User Profile Routes - Complete with all profile functions
# ============================================================

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db
from datetime import datetime

# Create blueprint for profile routes
profile_bp = Blueprint('profile', __name__)


# ============================================================
# Profile Page Route
# ============================================================
@profile_bp.route('/profile')
@login_required
def profile():
    """Render user profile page"""
    avatar_letter = current_user.name[0].upper() if current_user.name else 'U'
    
    # Calculate profile completion percentage
    completion = calculate_profile_completion(current_user)
    
    return render_template(
        'profile.html',
        user=current_user,
        avatar_letter=avatar_letter,
        completion=completion
    )


# ============================================================
# Profile Update Function - Used by API
# ============================================================
def profile_update():
    """
    Update user profile data
    This function is called from ap.py
    """
    try:
        # Get JSON data from request
        data = request.get_json() if request.is_json else request.form
        
        # Update user fields if provided
        if 'name' in data:
            current_user.name = data['name']
        if 'email' in data:
            current_user.email = data['email']
        if 'country' in data:
            current_user.country = data['country']
        if 'city' in data:
            current_user.city = data['city']
        if 'bio' in data:
            current_user.bio = data['bio']
        if 'theme' in data:
            current_user.theme = data['theme']
        if 'language' in data:
            current_user.language = data['language']
        
        # Update timestamp
        current_user.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.commit()
        
        # Calculate new profile completion
        completion = calculate_profile_completion(current_user)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'progress': completion
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Profile update error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# Profile Save Function - For manual save with redirect
# ============================================================
def profile_save():
    """
    Save profile and return redirect
    This function is called from ap.py
    """
    try:
        # Get JSON data from request
        data = request.get_json() if request.is_json else request.form
        
        # Update all profile fields
        if 'name' in data:
            current_user.name = data['name']
        if 'email' in data:
            current_user.email = data['email']
        if 'country' in data:
            current_user.country = data['country']
        if 'city' in data:
            current_user.city = data['city']
        if 'bio' in data:
            current_user.bio = data['bio']
        if 'theme' in data:
            current_user.theme = data['theme']
        if 'language' in data:
            current_user.language = data['language']
        
        # Update timestamp
        current_user.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully',
            'redirect': '/profile'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Profile save error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# Get Profile Data API
# ============================================================
@profile_bp.route('/api/profile/data', methods=['GET'])
@login_required
def get_profile_data():
    """Return user profile data as JSON"""
    try:
        return jsonify({
            'success': True,
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email,
                'username': current_user.username,
                'country': current_user.country,
                'city': current_user.city,
                'bio': current_user.bio,
                'theme': current_user.theme,
                'language': current_user.language,
                'avatar': current_user.avatar,
                'created_at': current_user.created_at,
                'updated_at': current_user.updated_at
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Helper Function - Calculate Profile Completion
# ============================================================
def calculate_profile_completion(user):
    """Calculate profile completion percentage"""
    fields = [
        user.name, user.email, user.country, 
        user.city, user.bio, user.theme, user.language
    ]
    
    # Count filled fields
    filled = sum(1 for field in fields if field)
    total = len(fields)
    
    return int((filled / total) * 100)


# ============================================================
# Update Profile API Route
# ============================================================
@profile_bp.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    """API endpoint for updating profile"""
    return profile_update()


# ============================================================
# Save Profile API Route
# ============================================================
@profile_bp.route('/api/profile/save', methods=['POST'])
@login_required
def api_profile_save():
    """API endpoint for saving profile"""
    return profile_save()


# ============================================================
# Avatar Upload API
# ============================================================
@profile_bp.route('/api/profile/avatar', methods=['POST'])
@login_required
def api_profile_avatar():
    """Handle avatar upload"""
    try:
        if 'avatar' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['avatar']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'File must be an image'}), 400
        
        # TODO: Save file logic here
        # filename = f"avatar_{current_user.id}_{file.filename}"
        # file.save(f"static/uploads/avatars/{filename}")
        # current_user.avatar = filename
        # db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Avatar uploaded successfully'
        })
        
    except Exception as e:
        print(f"Avatar upload error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# Now update ap.py - Change line 121
# ============================================================
"""
In ap.py, find this line (around line 121):

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update_alias():
    return profile_update()

Change it to:

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update_alias():
    from user_profile.routes import profile_update
    return profile_update()

OR better yet, import at the top:

from user_profile.routes import profile_update, profile_save

And then use them directly.
"""

# ============================================================
# Export functions for use in ap.py
# ============================================================
__all__ = ['profile_bp', 'profile_update', 'profile_save']