# ============================================================
# User Security Blueprint - Password and Account Security
# Handles password changes, 2FA, and security settings
# ============================================================

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils import check_password, hash_password, validate_password_strength
from models import db
from datetime import datetime

# Create blueprint for security with URL prefix
security_bp = Blueprint('security', __name__, url_prefix='/profile/security')


# ============================================================
# Password Update Route
# ============================================================

@security_bp.route('/password', methods=['POST'])
@login_required
def update_password():
    """
    Update user's password
    URL: /profile/security/password
    Requires: current_password, new_password
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate input fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Check if all fields are provided
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400

        # Verify current password
        if not check_password(current_user.password, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Check if new password is same as old password
        if current_password == new_password:
            return jsonify({'error': 'New password must be different from current password'}), 400

        # Validate new password strength
        is_valid, strength_message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'error': strength_message}), 400

        # Update password
        current_user.password = hash_password(new_password)
        current_user.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': 'Password updated successfully'
        })

    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        print(f"Password update error: {e}")
        return jsonify({'error': 'Failed to update password'}), 500


# ============================================================
# Get Security Settings
# ============================================================

@security_bp.route('/settings', methods=['GET'])
@login_required
def get_security_settings():
    """
    Get current user's security settings
    URL: /profile/security/settings
    """
    try:
        # Return security settings
        return jsonify({
            'success': True,
            'settings': {
                'two_factor_enabled': getattr(current_user, 'two_factor_enabled', False),
                'email_verified': getattr(current_user, 'email_verified', False),
                'last_password_change': getattr(current_user, 'updated_at', None),
                'account_created': current_user.created_at
            }
        })
    except Exception as e:
        print(f"Get security settings error: {e}")
        return jsonify({'error': 'Failed to get security settings'}), 500


# ============================================================
# Check Password Strength API
# ============================================================

@security_bp.route('/check-password-strength', methods=['POST'])
@login_required
def check_password_strength_api():
    """
    Check password strength without updating
    URL: /profile/security/check-password-strength
    """
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({'error': 'Password required'}), 400
            
        password = data.get('password')
        
        # Validate password strength
        is_valid, message = validate_password_strength(password)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'message': message
        })
        
    except Exception as e:
        print(f"Password strength check error: {e}")
        return jsonify({'error': 'Failed to check password strength'}), 500


# ============================================================
# Enable/Disable Two-Factor Authentication
# ============================================================

@security_bp.route('/two-factor', methods=['POST'])
@login_required
def toggle_two_factor():
    """
    Enable or disable two-factor authentication
    URL: /profile/security/two-factor
    """
    try:
        data = request.get_json()
        
        if not data or 'enabled' not in data:
            return jsonify({'error': 'Enabled flag required'}), 400
            
        enabled = data.get('enabled')
        
        # Check if user model has two_factor_enabled field
        if hasattr(current_user, 'two_factor_enabled'):
            current_user.two_factor_enabled = enabled
            current_user.updated_at = datetime.utcnow()
            db.session.commit()
            
            status = 'enabled' if enabled else 'disabled'
            return jsonify({
                'success': True,
                'message': f'Two-factor authentication {status} successfully'
            })
        else:
            return jsonify({'error': 'Two-factor authentication not supported'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"Two-factor toggle error: {e}")
        return jsonify({'error': 'Failed to update two-factor settings'}), 500


# ============================================================
# Get Login History
# ============================================================

@security_bp.route('/login-history', methods=['GET'])
@login_required
def get_login_history():
    """
    Get user's login history
    URL: /profile/security/login-history
    """
    try:
        # This would typically query a LoginHistory table
        # For now, return placeholder data
        return jsonify({
            'success': True,
            'login_history': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'ip_address': '192.168.1.1',
                    'device': 'Chrome on Windows',
                    'location': 'Unknown'
                }
            ]
        })
    except Exception as e:
        print(f"Login history error: {e}")
        return jsonify({'error': 'Failed to get login history'}), 500


# ============================================================
# Request Email Verification
# ============================================================

@security_bp.route('/verify-email', methods=['POST'])
@login_required
def request_email_verification():
    """
    Send email verification link
    URL: /profile/security/verify-email
    """
    try:
        # Check if email is already verified
        if getattr(current_user, 'email_verified', False):
            return jsonify({'error': 'Email already verified'}), 400
            
        # TODO: Generate and send verification email
        # This would use email_service to send verification link
        
        return jsonify({
            'success': True,
            'message': 'Verification email sent'
        })
        
    except Exception as e:
        print(f"Email verification error: {e}")
        return jsonify({'error': 'Failed to send verification email'}), 500


# ============================================================
# Deactivate Account
# ============================================================

@security_bp.route('/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    """
    Deactivate user account (soft delete)
    URL: /profile/security/deactivate
    """
    try:
        data = request.get_json()
        
        # Require password confirmation for security
        if not data or 'password' not in data:
            return jsonify({'error': 'Password confirmation required'}), 400
            
        password = data.get('password')
        
        # Verify password
        if not check_password(current_user.password, password):
            return jsonify({'error': 'Invalid password'}), 400
            
        # Soft delete - mark as inactive instead of deleting
        if hasattr(current_user, 'is_active'):
            current_user.is_active = False
            current_user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Account deactivated successfully'
            })
        else:
            return jsonify({'error': 'Account deactivation not supported'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"Account deactivation error: {e}")
        return jsonify({'error': 'Failed to deactivate account'}), 500