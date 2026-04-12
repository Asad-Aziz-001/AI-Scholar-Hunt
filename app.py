# ==================================================
#                  AI Scholar Hunt
#              Main Application File
# ==================================================

# ==================================================
#   Standard Library & Flask Imports
# ==================================================
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_mail import Mail
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer

# ==================================================
#   App Creation — MUST be first before blueprints
# ==================================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config.from_object('config.Config')               # Load SECRET_KEY, DB URI, etc.

# CORS — only once
CORS(app, supports_credentials=True, origins="*")

# ==================================================
#   Extensions Initialization
# ==================================================
from models import db, User
db.init_app(app)

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login_page'   # Redirect here if not logged in
login_manager.login_message = "Please login first"

# ==================================================
#   Services
# ==================================================
from email_service import EmailService
email_service = EmailService(app, mail)

# ==================================================
#   Chatbot — load once, store in variable
# ==================================================
from chatbot import get_response, search_scholarships, load_scholarships
scholarships = load_scholarships()   # ← Load scholarships data once at startup

# ==================================================
#   Blueprint Imports & Registration
# ==================================================
from auth.routes import auth_bp
from user_profile.preferences import preferences_bp
from user_profile.security import security_bp
from user_profile.routes import profile_bp, profile_update, profile_save
from blueprints.cv import cv_bp   # CV Builder blueprint

app.register_blueprint(auth_bp)
app.register_blueprint(preferences_bp)
app.register_blueprint(security_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(cv_bp, url_prefix='/cv-builder')


# ==================================================
#   User Loader (Flask-Login)
# ==================================================
@login_manager.user_loader
def load_user(user_id):
    """Load user from DB by ID for session management"""
    return db.session.get(User, int(user_id))

# ==================================================
#   Database Initialization Helper
# ==================================================
def init_database():
    """Create all DB tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")

# ==================================================
#   Helper Functions
# ==================================================
def calculate_profile_progress(user):
    """Calculate what % of profile is filled (out of 5 fields)"""
    fields = ['name', 'email', 'country', 'theme', 'language']
    filled = sum(1 for f in fields if getattr(user, f, None))
    return int((filled / len(fields)) * 100)

# ==================================================
#   Public Pages (No login required)
# ==================================================
@app.route('/')
def home():
    return render_template('index.html')

# ==================================================
#   Auth Pages
# ==================================================
@app.route('/login')
def login():
    """
    Login page.
    FIX: Agar user already logged in hai toh dashboard pe bhejo,
    warna login page dikhao. Yahi wajah thi ke /login 302 de raha tha.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))   # Already logged in → dashboard
    return render_template('login.html')        # Not logged in → show login form

@app.route('/signup')
def signup():
    """Signup page — redirect to dashboard if already logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    """Logout and go to home"""
    logout_user()
    return redirect(url_for('home'))

# ==================================================
#   Protected Dashboard & Profile Routes
# ==================================================
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard — requires login"""
    avatar_letter = current_user.name[0].upper() if current_user.name else 'U'
    return render_template('dashboard.html', user=current_user, avatar_letter=avatar_letter)

@app.route('/profile')
@login_required
def profile():
    """View profile page"""
    avatar_letter = current_user.name[0].upper() if current_user.name else 'U'
    return render_template('profile.html', user=current_user, avatar_letter=avatar_letter)

@app.route('/edit-profile')
@login_required
def edit_profile():
    """Edit profile page with country dropdown"""
    countries = [
        {'code': 'US', 'name': 'United States'},
        {'code': 'PK', 'name': 'Pakistan'},
        {'code': 'IN', 'name': 'India'},
        {'code': 'UK', 'name': 'United Kingdom'},
        {'code': 'CA', 'name': 'Canada'},
        {'code': 'AU', 'name': 'Australia'},
        {'code': 'DE', 'name': 'Germany'},
        {'code': 'FR', 'name': 'France'},
        {'code': 'JP', 'name': 'Japan'},
        {'code': 'CN', 'name': 'China'},
        {'code': 'BR', 'name': 'Brazil'},
        {'code': 'ZA', 'name': 'South Africa'},
    ]
    return render_template('edit_profile.html', user=current_user, countries=countries)

# ==================================================
#   Feature Pages (Protected)
# ==================================================
@app.route('/search')
@login_required
def search():
    return render_template('search.html')

@app.route('/ats')
@login_required
def ats():
    return render_template('ats.html')

@app.route('/essay')
@login_required
def essay():
    return render_template('essay.html')

@app.route('/scholarships')
@login_required
def scholarships_page():
    return render_template('scholarships.html')

# ==================================================
#   Profile API Endpoints
# ==================================================
@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    """Auto-save profile changes via AJAX"""
    try:
        data = request.get_json() if request.is_json else request.form
        fields = ['name', 'email', 'country', 'theme', 'language']
        for field in fields:
            if field in data:
                setattr(current_user, field, data[field])
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'progress': calculate_profile_progress(current_user)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/save', methods=['POST'])
@login_required
def api_profile_save():
    """Manual save profile"""
    try:
        data = request.get_json() if request.is_json else request.form
        fields = ['name', 'email', 'country', 'theme', 'language']
        for field in fields:
            if field in data:
                setattr(current_user, field, data[field])
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully',
            'redirect': url_for('profile')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/avatar', methods=['POST'])
@login_required
def api_profile_avatar():
    """Upload profile avatar"""
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        if not file.content_type.startswith('image/'):
            return jsonify({'success': False, 'error': 'File must be an image'}), 400
        # TODO: Save to static/uploads/avatars/
        return jsonify({'success': True, 'message': 'Avatar updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================================================
#   Resume Analyzer API
# ==================================================
@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_resume():
    """Handle resume analysis requests"""
    if request.method == 'OPTIONS':
        # CORS preflight response
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    try:
        data = request.get_json()
        # TODO: Replace with actual AI analysis
        result = {
            'success': True,
            'match_score': 78,
            'feedback': 'Your resume matches well with the requirements.',
            'suggestions': [
                'Add more relevant keywords',
                'Quantify your achievements',
                'Tailor your resume to the job description'
            ],
            'keywords_matched': ['Python', 'Communication', 'Leadership'],
            'keywords_missing': ['Project Management', 'Cloud Computing']
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================================================
#   Chatbot Routes
# ==================================================
@app.route('/chatbot')
@login_required
def chatbot_page():
    """Chatbot UI page"""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot messages"""
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"reply": "👋 Hello! Please ask me about any scholarship!"})
    matched = search_scholarships(user_message)
    reply = get_response(user_message, matched)
    return jsonify({"reply": reply})

@app.route('/list_all', methods=['GET'])
def list_all_scholarships():
    """List all loaded scholarships"""
    if not scholarships:
        return jsonify({"message": "No scholarships loaded", "count": 0, "scholarships": []})
    data = [
        {
            "name": s.get('scholarship_name', 'Unknown'),
            "country": s.get('study_in', 'Not specified'),
            "institution": s.get('institution', 'Not specified'),
            "level": s.get('level_of_study', [])
        }
        for s in scholarships
    ]
    return jsonify({"count": len(scholarships), "scholarships": data})

# ==================================================
#   Error Handlers
# ==================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ==================================================
#   Run Application
# ==================================================
if __name__ == '__main__':
    init_database()  # Create tables if not exist

    print("\n" + "=" * 60)
    print("  🎓 AI Scholar Hunt — Starting Server")
    print("  URL:  http://127.0.0.1:5000")
    print(f"  📚 Scholarships loaded: {len(scholarships) if isinstance(scholarships, list) else 0}")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)