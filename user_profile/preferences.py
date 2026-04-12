# ============================================================
# User Preferences Blueprint - Theme and Language Settings
# Handles user theme preferences and other settings
# ============================================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from datetime import datetime

# Create blueprint for preferences with URL prefix
preferences_bp = Blueprint('preferences', __name__, url_prefix='/profile/preferences')


# ============================================================
# Theme Update Route
# ============================================================

@preferences_bp.route('/theme', methods=['POST'])
@login_required
def update_theme():
    """
    Update user's theme preference (light/dark mode)
    URL: /profile/preferences/theme
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate theme value
        if not data or 'theme' not in data:
            return jsonify({'error': 'Theme is required'}), 400
            
        theme = data.get('theme')

        # Check if theme is valid
        if theme not in ['light', 'dark']:
            return jsonify({'error': 'Invalid theme. Must be light or dark'}), 400

        # Update user's theme preference
        current_user.theme = theme
        current_user.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': f'Theme updated to {theme} mode'
        })

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"Theme update error: {e}")
        return jsonify({'error': 'Failed to update theme'}), 500


# ============================================================
# Get User Preferences
# ============================================================

@preferences_bp.route('/', methods=['GET'])
@login_required
def get_preferences():
    """
    Get current user's preferences
    URL: /profile/preferences/
    """
    try:
        # Return user preferences
        return jsonify({
            'success': True,
            'preferences': {
                'theme': getattr(current_user, 'theme', 'light'),
                'language': getattr(current_user, 'language', 'en'),
                'notifications': getattr(current_user, 'notifications', True)
            }
        })
    except Exception as e:
        print(f"Get preferences error: {e}")
        return jsonify({'error': 'Failed to get preferences'}), 500


# ============================================================
# Update Language Preference
# ============================================================

@preferences_bp.route('/language', methods=['POST'])
@login_required
def update_language():
    """
    Update user's language preference
    URL: /profile/preferences/language
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate language value
        if not data or 'language' not in data:
            return jsonify({'error': 'Language is required'}), 400
            
        language = data.get('language')

        # List of supported languages
        supported_languages = ['en', 'es', 'fr', 'de', 'zh', 'ar', 'ur', 'hi']
        
        # Check if language is supported
        if language not in supported_languages:
            return jsonify({'error': 'Unsupported language'}), 400

        # Update user's language preference
        current_user.language = language
        current_user.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': f'Language updated to {language}'
        })

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"Language update error: {e}")
        return jsonify({'error': 'Failed to update language'}), 500


# ============================================================
# Update Notification Preferences
# ============================================================

@preferences_bp.route('/notifications', methods=['POST'])
@login_required
def update_notifications():
    """
    Update user's notification preferences
    URL: /profile/preferences/notifications
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update notification settings if user model has these fields
        if hasattr(current_user, 'email_notifications'):
            current_user.email_notifications = data.get('email_notifications', True)
            
        if hasattr(current_user, 'push_notifications'):
            current_user.push_notifications = data.get('push_notifications', True)
            
        if hasattr(current_user, 'marketing_emails'):
            current_user.marketing_emails = data.get('marketing_emails', False)

        current_user.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': 'Notification preferences updated'
        })

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"Notification update error: {e}")
        return jsonify({'error': 'Failed to update notifications'}), 500


# ============================================================
# Update All Preferences at Once
# ============================================================

@preferences_bp.route('/update-all', methods=['POST'])
@login_required
def update_all_preferences():
    """
    Update multiple preferences at once
    URL: /profile/preferences/update-all
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update theme if provided
        if 'theme' in data:
            theme = data['theme']
            if theme in ['light', 'dark']:
                current_user.theme = theme
            else:
                return jsonify({'error': 'Invalid theme value'}), 400

        # Update language if provided
        if 'language' in data:
            language = data['language']
            supported_languages = ['en', 'es', 'fr', 'de', 'zh', 'ar', 'ur', 'hi']
            if language in supported_languages:
                current_user.language = language
            else:
                return jsonify({'error': 'Unsupported language'}), 400

        # Update timestamp
        current_user.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': 'All preferences updated successfully'
        })

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"Update all preferences error: {e}")
        return jsonify({'error': 'Failed to update preferences'}), 500