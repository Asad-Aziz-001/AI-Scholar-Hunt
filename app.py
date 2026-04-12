# ==============================================================
#                       AI Scholar Hunt
#                    Main Application File
#
#  This is the ONLY entry point for the Flask app.
#  Do NOT create Flask() in any other file (chatbot, ats, etc.)
# ==============================================================

from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_mail import Mail
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer

# ==============================================================
#   App Creation — Must happen FIRST before any blueprint import
# ==============================================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config.from_object('config.Config')               # Load settings from config.py

# Enable CORS for all routes (needed for API calls from frontend)
CORS(app, supports_credentials=True, origins="*")

# ==============================================================
#   Extensions Initialization
# ==============================================================
from models import db, User

db.init_app(app)          # SQLAlchemy database
mail = Mail(app)          # Flask-Mail for sending emails
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Login Manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login_page'   # Redirect here if not logged in
login_manager.login_message = "Please login to access this page."

# ==============================================================
#   Services
# ==============================================================
from email_service import EmailService
email_service = EmailService(app, mail)

# ==============================================================
#   Chatbot — Load scholarship data ONCE at startup
# ==============================================================
from chatbot import get_response, search_scholarships, load_scholarships
scholarships = load_scholarships()

# ==============================================================
#   Blueprint Registration
#   Each feature is separated into its own blueprint
# ==============================================================
from auth.routes import auth_bp                    # Login, signup, forgot/reset password
from user_profile.preferences import preferences_bp # Theme settings
from user_profile.security import security_bp       # Password change
from user_profile.routes import profile_bp          # Profile view & update
from blueprints.cv import cv_bp                    # CV Builder

app.register_blueprint(auth_bp)
app.register_blueprint(preferences_bp)
app.register_blueprint(security_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(cv_bp, url_prefix='/cv-builder')


# ==============================================================
#   Flask-Login: User Loader
# ==============================================================
@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID for session management."""
    return db.session.get(User, int(user_id))


# ==============================================================
#   Database Initialization
# ==============================================================
def init_database():
    """Create all DB tables if they don't already exist."""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")


# ==============================================================
#   Helper: Profile Progress Calculation
# ==============================================================
def calculate_profile_progress(user):
    """Return profile completion percentage (out of 5 key fields)."""
    fields = ['name', 'email', 'theme']
    filled = sum(1 for f in fields if getattr(user, f, None))
    return int((filled / len(fields)) * 100)


# ==============================================================
#   Public Routes (No login required)
# ==============================================================
@app.route('/')
def home():
    """Landing/home page."""
    return render_template('index.html')


# ==============================================================
#   Auth Page Routes
#   NOTE: API logic (POST) is handled in auth/routes.py blueprint
# ==============================================================
@app.route('/login')
def login():
    """Login page. Redirect to dashboard if already logged in."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/signup')
def signup():
    """Signup page. Redirect to dashboard if already logged in."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    """Logout current user and redirect to home."""
    logout_user()
    return redirect(url_for('home'))


# ==============================================================
#   Protected App Pages (Login required)
# ==============================================================
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page after login."""
    avatar_letter = current_user.name[0].upper() if current_user.name else 'U'
    return render_template('dashboard.html', user=current_user, avatar_letter=avatar_letter)


@app.route('/search')
@login_required
def search():
    """Scholarship search page."""
    return render_template('search.html')


@app.route('/ats')
@login_required
def ats():
    """ATS Resume Analyzer page."""
    return render_template('ats.html')


@app.route('/essay')
@login_required
def essay():
    """Essay/SOP Writer page."""
    return render_template('essay.html')


# ==============================================================
#   Profile Routes
#   NOTE: /profile view is handled by user_profile/routes.py
# ==============================================================
@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    """Auto-save profile changes via AJAX."""
    try:
        data = request.get_json() if request.is_json else request.form
        for field in ['name', 'email', 'theme']:
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
    """Manual save profile with redirect URL."""
    try:
        data = request.get_json() if request.is_json else request.form
        for field in ['name', 'email', 'theme']:
            if field in data:
                setattr(current_user, field, data[field])
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully',
            'redirect': url_for('profile_bp.profile')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==============================================================
#   ATS Resume Analyzer API
# ==============================================================
@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_resume():
    """Handle ATS resume analysis requests."""
    if request.method == 'OPTIONS':
        # CORS preflight response
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        resume_text = data.get('resume', '') if data else ''

        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400

        import re
        word_count = len(resume_text.split())

        # Basic keyword scoring
        score = 50
        if re.search(r'email|phone|linkedin', resume_text.lower()):  score += 10
        if re.search(r'education|degree|university', resume_text.lower()): score += 10
        if re.search(r'experience|work|position', resume_text.lower()):    score += 15
        if re.search(r'skills|technical|proficient', resume_text.lower()): score += 10
        if 300 <= word_count <= 800:                                        score += 5
        score = min(score, 100)

        # Extract basic keywords
        words = re.findall(r'\b[a-z]{4,}\b', resume_text.lower())
        stopwords = {'that', 'have', 'with', 'this', 'from', 'your', 'will', 'work', 'also'}
        keywords = list(dict.fromkeys(w for w in words if w not in stopwords))[:12]

        return jsonify({
            'success': True,
            'score': score,
            'match_score': score,
            'word_count': word_count,
            'keywords_found': keywords[:10],
            'suggestions': [
                'Add quantifiable achievements with numbers',
                'Include more industry-specific keywords',
                'Use action verbs (managed, developed, created)'
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==============================================================
#   Chatbot Routes
# ==============================================================
@app.route('/chatbot')
@login_required
def chatbot_page():
    """Chatbot UI page."""
    return render_template('chat.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot messages from frontend."""
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"reply": "👋 Hello! Please ask me about any scholarship!"})
    matched = search_scholarships(user_message)
    reply = get_response(user_message, matched)
    return jsonify({"reply": reply})


@app.route('/list_all', methods=['GET'])
def list_all_scholarships():
    """List all loaded scholarships (for testing/debug)."""
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


# ==============================================================
#   Error Handlers
# ==============================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# ==============================================================
#   Run Application
# ==============================================================
if __name__ == '__main__':
    init_database()

    print("\n" + "=" * 60)
    print("  🎓 AI Scholar Hunt — Starting Server")
    print("  URL:  http://127.0.0.1:5000")
    print(f"  📚 Scholarships loaded: {len(scholarships) if isinstance(scholarships, list) else 0}")
    print("=" * 60 + "\n")

    app.run(debug=False, host='0.0.0.0', port=7860)
