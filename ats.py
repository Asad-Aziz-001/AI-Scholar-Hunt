from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        # Get resume text from request
        data = request.get_json()
        resume_text = data.get('resume', '')
        
        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400
        
        # Simple analysis
        word_count = len(resume_text.split())
        
        # Calculate score
        score = 50
        if re.search(r'email|phone|linkedin', resume_text.lower()):
            score += 10
        if re.search(r'education|degree|university', resume_text.lower()):
            score += 10
        if re.search(r'experience|work|position', resume_text.lower()):
            score += 15
        if re.search(r'skills|technical|proficient', resume_text.lower()):
            score += 10
        if 300 <= word_count <= 800:
            score += 10
            
        score = min(score, 100)
        
        # Extract keywords
        words = re.findall(r'\b[a-z]{4,}\b', resume_text.lower())
        common_words = ['that', 'have', 'with', 'this', 'from', 'your', 'will', 'work']
        keywords = [w for w in words if w not in common_words][:12]
        
        return jsonify({
            'score': score,
            'match_score': score,
            'word_count': word_count,
            'keywords': list(dict.fromkeys(keywords)),
            'keywords_found': list(dict.fromkeys(keywords))[:10],
            'suggestions': [
                'Add quantifiable achievements with numbers',
                'Include more industry-specific keywords',
                'Use action verbs (managed, developed, created)'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)