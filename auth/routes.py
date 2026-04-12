# ============================================================
# Authentication Routes
# Handles signup, login, forgot password, reset password, and logout
# ============================================================

from flask import Blueprint, render_template, request, jsonify, url_for, current_app
from flask import redirect, url_for, render_template, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, PasswordResetToken
from utils import hash_password, check_password, generate_reset_token
from datetime import datetime, timedelta
from email_service import EmailService

auth_bp = Blueprint('auth', __name__)


# ============================================================
# PAGE ROUTES - Render HTML templates
# ============================================================

@auth_bp.route('/signup')
def signup_page():
    """Render signup page - redirect to dashboard if already logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')


@auth_bp.route('/login')
def login_page():
    """Render login page - redirect to dashboard if already logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@auth_bp.route('/forgot-password')
def forgot_password_page():
    """Render forgot password page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('forgot-password.html')


@auth_bp.route('/reset-password/<token>')
def reset_password_page(token):
    """Render reset password page with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('reset-password.html', token=token)


# ============================================================
# SIGNUP API - Create new user account
# ============================================================

@auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    """Create new user account with complete profile fields"""
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get('username') or '').strip()
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        # -------- Validation --------
        if not username:
            return jsonify({"error": "Username is required"}), 400
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        if not name:
            return jsonify({"error": "Name is required"}), 400
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Valid email is required"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400

        # -------- Duplicate Check --------
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        # -------- Create User with complete fields --------
        new_user = User(
            username=username,
            name=name,
            email=email,
            password=hash_password(password),
            theme='light',  # Default theme
            language='en',  # Default language
            created_at=datetime.utcnow()
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "Account created successfully!",
            "redirect": url_for('auth.login_page')
        }), 201

    except Exception as e:
        db.session.rollback()
        print("Signup error:", e)
        return jsonify({"error": "Server error"}), 500


# ============================================================
# LOGIN API - Authenticate user
# ============================================================

@auth_bp.route('/auth/login', methods=['POST'])
def auth_login():
    """Login using username OR email"""
    try:
        data = request.get_json(silent=True) or {}
        login_input = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', True)

        if not login_input or not password:
            return jsonify({"error": "Username/email and password required"}), 400

        # Find user by username OR email (case insensitive)
        user = User.query.filter(
            (User.username == login_input) | 
            (db.func.lower(User.email) == login_input.lower())
        ).first()

        if not user or not check_password(user.password, password):
            return jsonify({"error": "Invalid username or password"}), 401

        # Update last active timestamp
        user.updated_at = datetime.utcnow()
        db.session.commit()

        # Log the user in
        login_user(user, remember=remember)

        return jsonify({
            "success": True,
            "message": f"Welcome back, {user.name}!",
            "redirect": url_for('dashboard')
        })

    except Exception as e:
        print("Login error:", e)
        return jsonify({"error": "Server error"}), 500


# ============================================================
# FORGOT PASSWORD - Send reset email
# ============================================================

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email to user"""
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()

        if not email:
            return jsonify({"error": "Email required"}), 400
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Valid email required"}), 400

        # Find user by email (case insensitive)
        user = User.query.filter(db.func.lower(User.email) == email).first()

        # Always return success message for security (don't reveal if email exists)
        if not user:
            return jsonify({
                "message": "If an account exists with that email, a reset link has been sent."
            })

        # -------- Check for existing valid token --------
        existing_token = PasswordResetToken.query.filter_by(
            user_id=user.id, 
            used=False
        ).filter(PasswordResetToken.expires_at > datetime.utcnow()).first()
        
        if existing_token:
            # Use existing token if still valid
            token = existing_token.token
        else:
            # Generate new token
            token = generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)

            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at,
                used=False
            )

            db.session.add(reset_token)
            db.session.commit()

        # -------- Generate Reset Link --------
        reset_link = url_for(
            'auth.reset_password_page',
            token=token,
            _external=True
        )

        # -------- Send Email Using EmailService --------
        email_service = EmailService(current_app, current_app.extensions['mail'])
        msg = email_service.create_password_reset_email(user, reset_link)
        email_service.send_email(msg)

        return jsonify({
            "message": "Password reset link sent to your email!"
        })

    except Exception as e:
        db.session.rollback()
        print("Forgot password error:", e)
        return jsonify({"error": "Server error"}), 500


# ============================================================
# RESET PASSWORD - Update password using token
# ============================================================

@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Update password using valid token"""
    try:
        data = request.get_json(silent=True) or {}
        token = data.get('token')
        password = data.get('password')

        if not token or not password:
            return jsonify({"error": "Token and password required"}), 400

        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400

        # Check password strength
        if not any(char.isdigit() for char in password):
            return jsonify({"error": "Password must contain at least one number"}), 400
        if not any(char.isupper() for char in password):
            return jsonify({"error": "Password must contain at least one uppercase letter"}), 400

        # Find valid token
        reset_token = PasswordResetToken.query.filter_by(
            token=token,
            used=False
        ).first()

        if not reset_token or reset_token.is_expired():
            return jsonify({"error": "Invalid or expired token"}), 400

        user = User.query.get(reset_token.user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update password
        user.password = hash_password(password)
        user.updated_at = datetime.utcnow()

        # Mark token as used
        reset_token.used = True

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Password updated successfully",
            "redirect": url_for('auth.login_page')
        })

    except Exception as e:
        db.session.rollback()
        print("Reset password error:", e)
        return jsonify({"error": "Server error"}), 500


# ============================================================
# CHECK AUTH STATUS - Verify if user is logged in
# ============================================================

@auth_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "name": current_user.name,
                "email": current_user.email
            }
        })
    return jsonify({"authenticated": False})


# ============================================================
# LOGOUT - End user session
# ============================================================

@auth_bp.route('/auth/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    return jsonify({
        "success": True,
        "message": "Logged out successfully",
        "redirect": url_for('home')
    })