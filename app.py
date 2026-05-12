# ==============================================================
#                       AI Scholar Hunt
#                    Main Application File
# ==============================================================

import traceback
from flask import Flask, json, jsonify, render_template, request, redirect, url_for
from mats import calculate_ats
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_mail import Mail
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer

from comparison import get_all_scholarship_names, get_scholarship_details  # Import functions
from cost_estimator import load_all_scholarships_cost

from timeline_visualizer import load_all_scholarships_timeline

# Add these imports for the new features
from scholarship_tracker import load_all_scholarships_tracker
from deadline_calendar import load_all_scholarships_for_calendar
from checklist_generator import load_all_scholarships_for_checklist

# Eassy analysis and plagiarism detection imports
from flask import Flask, request, jsonify
from flask_cors import CORS

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
from comparison import get_all_scholarship_names, get_all_scholarship_names, get_scholarship_details
from comparison import get_scholarship_details
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
from essay import essay_bp

app.register_blueprint(auth_bp)
app.register_blueprint(preferences_bp)
app.register_blueprint(security_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(cv_bp, url_prefix='/cv-builder')
app.register_blueprint(essay_bp)
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
from chatbot import get_response, search_scholarships, load_scholarships
scholarships = load_scholarships()

@app.route('/chatbot')
@login_required
def chatbot_page():
    """Chatbot UI page."""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"reply": "👋 Hello! Please ask me about any scholarship!"})
    matched = search_scholarships(user_message)
    reply   = get_response(user_message, matched)
    return jsonify({"reply": reply})
 
 
@app.route('/list_all', methods=['GET'])
def list_all_scholarships():
    if not scholarships:
        return jsonify({"message": "No scholarships loaded", "count": 0, "scholarships": []})
    data = [
        {
            "name"       : s.get('name', 'Unknown'),
            "filename"   : s.get('filename', ''),
        }
        for s in scholarships
    ]
    return jsonify({"count": len(scholarships), "scholarships": data})

# ==============================================================
#   comparison page and API
# ==============================================================

@app.route('/comparison')
def comparison_page():
    """Render comparison page with heatmap"""
    scholarship_names = get_all_scholarship_names()
    return render_template('comparison.html', scholarships=scholarship_names)

# Add this API endpoint
@app.route('/api/scholarship/<scholarship_name>')
def get_scholarship_api(scholarship_name):
    """API endpoint to get scholarship details for comparison"""
    details = get_scholarship_details(scholarship_name)
    if details:
        return jsonify({"success": True, "data": details})
    else:
        return jsonify({"success": False, "error": "Scholarship not found"}), 404

# ==============================================================
#   Cost Estimator page and Timeline Visualizer page routes
# ==============================================================
@app.route('/cost-estimator')
def cost_estimator_page():
    """Render cost estimator page"""
    scholarships = load_all_scholarships_cost()
    return render_template('cost_estimator.html', scholarships=scholarships)


# ============ NEW ROUTE 2: Timeline Visualizer ============
@app.route('/timeline-visualizer')
def timeline_visualizer_page():
    """Render timeline visualizer page"""
    scholarships = load_all_scholarships_timeline()
    return render_template('timeline_visualizer.html', scholarships=scholarships)

# ============ NEW ROUTE 3: Scholarship Tracker ============
# Add this import
from scholarship_tracker import load_all_scholarships_tracker

# Add this route
@app.route('/tracker')
def tracker_page():
    """Scholarship application tracker with Kanban board"""
    scholarships = load_all_scholarships_tracker()
    return render_template('tracker.html', scholarships=scholarships)

# ============ NEW ROUTE 4: Deadline Calendar ============

@app.route('/deadline-calendar')
def deadline_calendar():
    scholarships = load_all_scholarships_for_calendar()
    return render_template('deadline_calendar.html', scholarships=scholarships)

# ============ NEW ROUTE 5: Checklist Generator ============

@app.route('/checklist-generator')
def checklist_generator():
    scholarships = load_all_scholarships_for_checklist()
    
    # Convert to JSON string manually
    scholarships_list = []
    for s in scholarships:
        scholarships_list.append({
            'name': s.get('name', ''),
            'documents': s.get('documents', []),
            'deadline': s.get('deadline', 'Not specified'),
            'apply_link': s.get('apply_link', '#')
        })
    
    scholarships_json = json.dumps(scholarships_list, ensure_ascii=False)
    print(f"DEBUG: JSON length: {len(scholarships_json)}")  # Debug
    
    return render_template('checklist_generator.html', 
                         scholarships=scholarships, 
                         scholarships_json=scholarships_json)

# ==============================================================
#   Helper Functions for Deadline Calendar & Checklist Generator
# ==============================================================

@app.route('/api/scholarship-documents')
def api_scholarship_documents():
    """API endpoint to get scholarship documents"""
    name = request.args.get('name', '')
    
    # Find the scholarship
    scholarships = load_all_scholarships_for_checklist()
    for s in scholarships:
        if s['name'] == name:
            return jsonify({
                'success': True,
                'documents': s['documents'],
                'deadline': s['deadline'],
                'apply_link': s['apply_link']
            })
    
    return jsonify({'success': False, 'error': 'Not found'})

# ==============================================================
@app.route('/api/scholarship-deadline')
def api_scholarship_deadline():
    """API endpoint to get scholarship deadline and country"""
    name = request.args.get('name', '')
    
    scholarships = load_all_scholarships_for_calendar()
    for s in scholarships:
        if s['name'] == name:
            return jsonify({
                'success': True,
                'deadline': s.get('deadline', 'Not specified'),
                'country': s.get('country', 'Not specified'),
                'apply_link': s.get('apply_link', '#')
            })
    
    return jsonify({'success': False, 'error': 'Not found'}), 404
# ==============================================================
#   API Endpoints for Checklist Generator
# ==============================================================

@app.route('/api/scholarship-docs')
def api_scholarship_docs():
    """API endpoint to get scholarship documents"""
    name = request.args.get('name', '')
    
    print(f"API called for: {name}")  # Debug print
    
    scholarships = load_all_scholarships_for_checklist()
    for s in scholarships:
        if s['name'] == name:
            return jsonify({
                'success': True,
                'documents': s['documents'],
                'deadline': s['deadline'],
                'apply_link': s['apply_link']
            })
    
    return jsonify({'success': False, 'error': 'Not found'}), 404


# ==============================================================
#   Mentor Page and API
# ==============================================================
from mentor import get_mentor_recommendations

@app.route('/mentor')
def mentor_page():
    """AI Mentor page"""
    return render_template('mentor.html')

@app.route('/api/mentor-analyze', methods=['POST'])
def api_mentor_analyze():
    """API endpoint for mentor analysis"""
    try:
        data = request.get_json()
        cgpa = data.get('cgpa', 0)
        ielts = data.get('ielts', 0)
        degree = data.get('degree', 'Master')
        budget = data.get('budget', 'medium')
        country_pref = data.get('country_pref', '')
        
        recommendations = get_mentor_recommendations(cgpa, ielts, degree, budget, country_pref)
        
        return jsonify({
            'success': True,
            'profile_score': recommendations['profile_score'],
            'country_scores': recommendations['country_scores'],
            'scholarships': recommendations['scholarships'],
            'action_plan': recommendations['action_plan'],
            'weaknesses': recommendations['weaknesses']
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    

# ==============================================================
#  Calculating ATS Score
# ==============================================================
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        
        if not resume_text:
            return jsonify({'error': 'Resume text is required'}), 400
        
        result = calculate_ats(resume_text, job_description)
        return jsonify(result)
        
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'ATS API is running'})
 
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
    
