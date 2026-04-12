from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    flash, jsonify
)
import os
import time
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------------------------------------------
# App Setup
# -------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 🔒 Change in production

# Upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads/avatars'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------------------------------------------------------
# Mock Database (Replace with real DB later)
# -------------------------------------------------------------------
users = {
    'student@example.com': {
        'id': 1,
        'name': 'John Doe',
        'email': 'student@example.com',
        'username': 'student@example.com',
        'country': 'US',
        'city': '',  # Added city field
        'bio': '',   # Added bio field
        'avatar': None,
        'theme': 'light',
        'language': 'en',
        'email_verified': False,
        'password_hash': generate_password_hash('password123')
    }
}

countries = [
    {'code': 'US', 'name': 'United States'},
    {'code': 'PK', 'name': 'Pakistan'},
    {'code': 'IN', 'name': 'India'},
    {'code': 'GB', 'name': 'United Kingdom'},
    {'code': 'CA', 'name': 'Canada'},
    {'code': 'AU', 'name': 'Australia'},
    {'code': 'DE', 'name': 'Germany'},
    {'code': 'FR', 'name': 'France'},
    {'code': 'JP', 'name': 'Japan'},
    {'code': 'CN', 'name': 'China'},
    {'code': 'BR', 'name': 'Brazil'},
    {'code': 'ZA', 'name': 'South Africa'},
]

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def get_current_user():
    email = session.get('user_id')
    return users.get(email)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def email_exists(email, current_email=None):
    return email in users and email != current_email

# -------------------------------------------------------------------
# Auth Routes
# -------------------------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users.get(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = email
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'success')
    return redirect(url_for('login'))

# -------------------------------------------------------------------
# Pages
# -------------------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=get_current_user())


@app.route('/profile')
@login_required
def profile():
    """User profile view page"""
    user = get_current_user()
    avatar_letter = user['name'][0].upper() if user['name'] else 'U'
    return render_template('profile.html', user=user, avatar_letter=avatar_letter)


@app.route('/edit_profile')
@login_required
def edit_profile():
    """Edit profile page"""
    user = get_current_user()
    return render_template(
        'edit_profile.html',
        user=user,
        countries=countries
    )

# -------------------------------------------------------------------
# Profile APIs
# -------------------------------------------------------------------
@app.route('/api/profile/save', methods=['POST'])
@login_required
def save_profile():
    user = get_current_user()

    name = request.form.get('name')
    email = request.form.get('email')
    country = request.form.get('country')
    city = request.form.get('city')  # Added city field
    bio = request.form.get('bio')    # Added bio field
    theme = request.form.get('theme')
    language = request.form.get('language')

    # Email change validation
    if email and email != user['email']:
        if email_exists(email, user['email']):
            return jsonify(success=False, message='Email already in use'), 400

        users[email] = user
        users.pop(user['email'])
        user['email'] = email
        user['username'] = email
        session['user_id'] = email

    # Update all user fields including city and bio
    if name:
        user['name'] = name
    if country:
        user['country'] = country
    if city is not None:  # Allow empty city
        user['city'] = city
    if bio is not None:   # Allow empty bio
        user['bio'] = bio
    if theme:
        user['theme'] = theme
    if language:
        user['language'] = language

    return jsonify(success=True, message='Profile saved successfully')


@app.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    user = get_current_user()
    file = request.files.get('avatar')

    if not file or file.filename == '':
        return jsonify(success=False, message='No file selected'), 400

    if not allowed_file(file.filename):
        return jsonify(success=False, message='Invalid file type'), 400

    filename = f"avatar_{user['id']}_{int(time.time())}.{file.filename.rsplit('.', 1)[1]}"
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    user['avatar'] = f"static/uploads/avatars/{filename}"

    return jsonify(
        success=True,
        message='Avatar updated',
        avatar_url=user['avatar']
    )

# -------------------------------------------------------------------
# Password Update
# -------------------------------------------------------------------
@app.route('/api/profile/password', methods=['POST'])
@login_required
def update_password():
    user = get_current_user()

    current = request.form.get('current_password')
    new = request.form.get('new_password')
    confirm = request.form.get('confirm_password')

    if not all([current, new, confirm]):
        return jsonify(success=False, message='All fields required'), 400

    if new != confirm:
        return jsonify(success=False, message='Passwords do not match'), 400

    if not check_password_hash(user['password_hash'], current):
        return jsonify(success=False, message='Current password incorrect'), 400

    user['password_hash'] = generate_password_hash(new)
    return jsonify(success=True, message='Password updated successfully')

# -------------------------------------------------------------------
# Errors
# -------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# -------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)