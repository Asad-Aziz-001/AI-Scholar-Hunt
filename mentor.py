import os
import json
import re

def load_all_scholarships_for_mentor():
    """Load all scholarships for mentor recommendations"""
    scholarships_dir = "scholarships"
    all_scholarships = []
    
    if not os.path.exists(scholarships_dir):
        return all_scholarships
    
    for filename in os.listdir(scholarships_dir):
        if filename.endswith('.txt') or filename.endswith('.json'):
            file_path = os.path.join(scholarships_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    continue
                
                # Try JSON first
                try:
                    data = json.loads(content)
                except:
                    data = parse_text_file(content, filename)
                
                if data:
                    all_scholarships.append({
                        'name': data.get('scholarship_name', filename.replace('.txt', '').replace('_', ' ').title()),
                        'country': data.get('study_in', 'Not specified'),
                        'deadline': data.get('deadline', 'Not specified'),
                        'degree_level': data.get('level_of_study', []),
                        'coverage': data.get('coverage', {}),
                        'apply_link': data.get('apply_link', '#'),
                        'ielts': extract_ielts(data)
                    })
                    
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return all_scholarships


def parse_text_file(content, filename):
    """Parse text file to extract scholarship info"""
    data = {
        'scholarship_name': filename.replace('.txt', '').replace('_', ' ').title(),
        'study_in': 'Not specified',
        'deadline': 'Not specified',
        'apply_link': '#'
    }
    
    lines = content.split('\n')
    for line in lines[:50]:
        line_lower = line.lower().strip()
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()
            value = parts[1].strip()
            
            if key in ['scholarship_name', 'name']:
                data['scholarship_name'] = value
            elif key in ['study_in', 'country']:
                data['study_in'] = value
            elif key in ['deadline', 'application_deadline']:
                data['deadline'] = value
            elif key in ['apply_link', 'link', 'url']:
                if value.startswith('http'):
                    data['apply_link'] = value
            elif key in ['level_of_study', 'level']:
                data['level_of_study'] = [l.strip() for l in value.split(',')]
    
    return data


def extract_ielts(data):
    """Extract IELTS requirement from scholarship data"""
    ielts_pattern = r'ielts[\s:]*(\d+\.?\d*)'
    
    # Check in eligibility
    elig = data.get('eligibility', {})
    if isinstance(elig, dict):
        lang = elig.get('language_requirement', '')
        if lang:
            match = re.search(ielts_pattern, str(lang).lower())
            if match:
                return float(match.group(1))
    
    # Check in coverage
    coverage = data.get('coverage', {})
    if isinstance(coverage, dict):
        for key, val in coverage.items():
            match = re.search(ielts_pattern, str(val).lower())
            if match:
                return float(match.group(1))
    
    return None


def calculate_country_match(cgpa, ielts, degree, budget, scholarship):
    """Calculate match percentage for a scholarship"""
    score = 50  # Base score
    
    # Country bonus
    country = scholarship.get('country', '').lower()
    if 'germany' in country:
        score += 15
    elif 'usa' in country:
        score += 10
    elif 'canada' in country:
        score += 10
    elif 'turkey' in country:
        score += 5
    
    # CGPA check
    if cgpa >= 3.5:
        score += 20
    elif cgpa >= 3.0:
        score += 10
    elif cgpa >= 2.5:
        score += 5
    
    # IELTS check
    ielts_req = scholarship.get('ielts')
    if ielts_req:
        if ielts >= ielts_req:
            score += 15
        elif ielts >= ielts_req - 0.5:
            score += 5
    
    # Degree level match
    degree_levels = scholarship.get('degree_level', [])
    if degree_levels:
        degree_lower = degree.lower()
        if any(d.lower() in degree_lower for d in degree_levels):
            score += 10
    
    # Coverage check
    coverage = scholarship.get('coverage', {})
    if budget == 'low' and coverage:
        if 'full' in str(coverage.get('tuition', '')).lower():
            score += 10
        elif 'partial' in str(coverage.get('tuition', '')).lower():
            score += 5
    
    return min(100, score)


def get_mentor_recommendations(cgpa, ielts, degree, budget, country_pref):
    """Get personalized mentor recommendations"""
    
    scholarships = load_all_scholarships_for_mentor()
    
    if not scholarships:
        return {
            'profile_score': 0,
            'country_scores': [],
            'scholarships': [],
            'action_plan': [],
            'weaknesses': []
        }
    
    # Calculate scores for each scholarship
    scored_scholarships = []
    for s in scholarships:
        score = calculate_country_match(cgpa, ielts, degree, budget, s)
        scored_scholarships.append({
            **s,
            'match_score': score
        })
    
    # Sort by score
    scored_scholarships.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Calculate profile score (average of top 5 scholarships)
    top_scores = [s['match_score'] for s in scored_scholarships[:5]]
    profile_score = sum(top_scores) // len(top_scores) if top_scores else 0
    
    # Country-wise aggregation
    country_scores = {}
    for s in scored_scholarships:
        country = s['country']
        if country not in country_scores:
            country_scores[country] = []
        country_scores[country].append(s['match_score'])
    
    country_summary = []
    for country, scores in country_scores.items():
        avg_score = sum(scores) // len(scores)
        country_summary.append({
            'name': country,
            'score': avg_score,
            'scholarships_count': len(scores)
        })
    country_summary.sort(key=lambda x: x['score'], reverse=True)
    
    # Identify weaknesses
    weaknesses = []
    if cgpa < 3.0:
        weaknesses.append({"level": "high", "area": "CGPA", "current": cgpa, "target": "3.0+", "tip": "Focus on improving last semester grades"})
    if ielts < 6.5:
        weaknesses.append({"level": "high", "area": "IELTS", "current": ielts, "target": "6.5+", "tip": "Take IELTS preparation course"})
    elif ielts < 7.0:
        weaknesses.append({"level": "medium", "area": "IELTS", "current": ielts, "target": "7.0+", "tip": "Practice speaking and writing modules"})
    
    # Generate action plan
    action_plan = generate_action_plan(cgpa, ielts, degree)
    
    return {
        'profile_score': profile_score,
        'country_scores': country_summary[:5],
        'scholarships': scored_scholarships[:8],
        'action_plan': action_plan,
        'weaknesses': weaknesses
    }


def generate_action_plan(cgpa, ielts, degree):
    """Generate personalized action plan"""
    plan = []
    
    # IELTS improvement
    if ielts < 6.5:
        plan.append({
            'task': 'Prepare for IELTS exam',
            'deadline': '2 months',
            'priority': 'high',
            'status': 'pending'
        })
    elif ielts < 7.0:
        plan.append({
            'task': 'Improve IELTS score to 7.0',
            'deadline': '1 month',
            'priority': 'medium',
            'status': 'pending'
        })
    
    # CGPA improvement
    if cgpa < 3.0:
        plan.append({
            'task': 'Focus on improving CGPA',
            'deadline': 'Current semester',
            'priority': 'high',
            'status': 'pending'
        })
    
    # Document preparation
    plan.append({
        'task': 'Prepare Statement of Purpose (SOP)',
        'deadline': '3 weeks',
        'priority': 'high',
        'status': 'pending'
    })
    plan.append({
        'task': 'Request Letters of Recommendation (2-3)',
        'deadline': '4 weeks',
        'priority': 'high',
        'status': 'pending'
    })
    plan.append({
        'task': 'Update CV/Resume',
        'deadline': '2 weeks',
        'priority': 'medium',
        'status': 'pending'
    })
    plan.append({
        'task': 'Research universities and scholarships',
        'deadline': '2 weeks',
        'priority': 'high',
        'status': 'pending'
    })
    plan.append({
        'task': 'Prepare application documents',
        'deadline': '6 weeks',
        'priority': 'medium',
        'status': 'pending'
    })
    
    return plan