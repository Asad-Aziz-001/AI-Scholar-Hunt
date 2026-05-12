import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from groq import Groq
import json
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file for API keys and secrets

# ============================================
# CONFIGURATION
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # 🔑 Apni API key yahan lagao

model = SentenceTransformer('all-MiniLM-L6-v2')
client = Groq(api_key=GROQ_API_KEY)

# ============================================
# PROFESSIONAL SKILLS DATABASE (Real Skills Only)
# ============================================
REAL_SKILLS = {
    "programming": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "swift", "kotlin", "php", "ruby", "sql"],
    "web": ["react", "angular", "vue", "django", "flask", "spring", "node.js", "express", "next.js", "laravel"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "git", "github"],
    "database": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "firebase"],
    "ai_ml": ["tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "keras", "opencv", "nlp"],
    "soft": ["leadership", "communication", "teamwork", "agile", "scrum", "project management", "problem solving"],
    "design": ["figma", "adobe xd", "photoshop", "illustrator", "ui/ux"],
    "mechanical": ["cad", "solidworks", "autocad", "matlab", "simulink"],
    "medical": ["patient care", "clinical research", "diagnosis", "medical coding"]
}

ALL_REAL_SKILLS = set()
for cat in REAL_SKILLS.values():
    ALL_REAL_SKILLS.update(cat)

# ============================================
# FIELD DETECTION
# ============================================
FIELD_KEYWORDS = {
    "AI/ML Engineer": ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "computer vision", "ai", "llm"],
    "Software Developer": ["react", "angular", "django", "flask", "api", "backend", "frontend", "full stack"],
    "Data Scientist": ["data science", "analytics", "pandas", "visualization", "statistics", "tableau"],
    "Cloud Engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "devops", "ci/cd"],
    "Mechanical Engineer": ["cad", "solidworks", "autocad", "manufacturing", "thermodynamics"],
    "Medical Professional": ["clinical", "patient", "diagnosis", "healthcare", "medical"],
    "Finance Professional": ["finance", "accounting", "audit", "financial analysis", "budgeting"]
}

def detect_field(text):
    text_lower = text.lower()
    scores = {}
    for field, keywords in FIELD_KEYWORDS.items():
        score = sum(2 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[field] = score
    if scores:
        return max(scores, key=scores.get)
    return "General Professional"

# ============================================
# TEXT CLEANING
# ============================================
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ============================================
# EXTRACTION FUNCTIONS
# ============================================
def extract_name(text):
    lines = text.split('\n')[:15]
    for line in lines:
        line = line.strip()
        if len(line.split()) >= 2 and len(line.split()) <= 4:
            if all(w[0].isupper() and len(w) > 1 for w in line.split()):
                if not any(x in line.lower() for x in ['email', 'phone', 'resume', 'curriculum', 'candidate']):
                    return line
    return None

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group() if match else None

def extract_phone(text):
    patterns = [
        r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return None

def extract_linkedin(text):
    match = re.search(r'linkedin\.com/in/[\w-]+', text.lower())
    return match.group() if match else None

def extract_github(text):
    match = re.search(r'github\.com/[\w-]+', text.lower())
    return match.group() if match else None

def extract_location(text):
    # Common location patterns
    patterns = [r'Location:\s*([A-Za-z\s,]+)', r'Based in\s*([A-Za-z\s,]+)']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_real_skills(text):
    text_lower = text.lower()
    found = []
    for skill in ALL_REAL_SKILLS:
        if re.search(rf'\b{re.escape(skill)}\b', text_lower):
            found.append(skill)
    return list(dict.fromkeys(found))[:25]

def extract_companies(text):
    companies = []
    patterns = [
        r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'with\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|Ltd|LLC|Technologies|Systems|Solutions|Corp)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        companies.extend(matches)
    
    # Common company names
    common = ['Google', 'Microsoft', 'Amazon', 'Facebook', 'Apple', 'Netflix', 'Tesla', 'IBM', 'Oracle', 'Salesforce']
    for company in common:
        if company.lower() in text.lower():
            companies.append(company)
    
    return list(dict.fromkeys(companies))[:6]

def extract_universities(text):
    univs = []
    patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:University|College|Institute|School)',
        r'(University|College|Institute|School)\s+of\s+([A-Z][a-z]+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                univs.append(' '.join(match))
            else:
                univs.append(match)
    
    # Common universities
    common_univs = ['MIT', 'Harvard', 'Stanford', 'Oxford', 'Cambridge', 'UET', 'NUST', 'LUMS', 'GIKI']
    for univ in common_univs:
        if univ.lower() in text.lower():
            univs.append(univ)
    
    return list(dict.fromkeys(univs))[:4]

def extract_degrees(text):
    degrees = []
    degree_patterns = [
        r'(Bachelor|Master|PhD|B\.?[A-Z]\.?|M\.?[A-Z]\.?|BSc|MSc|BS|MS|MBA|BBA|BCA|MCA|BE|ME|B\.Tech|M\.Tech)'
    ]
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        degrees.extend(matches)
    return list(dict.fromkeys([d.upper() for d in degrees]))[:4]

def extract_job_titles(text):
    titles = []
    title_patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Engineer|Developer|Manager|Director|Analyst|Consultant|Architect|Lead)'
    ]
    for pattern in title_patterns:
        matches = re.findall(pattern, text)
        titles.extend(matches)
    return list(dict.fromkeys(titles))[:4]

def extract_years_of_experience(text):
    years = re.findall(r'\b(19|20)\d{2}\b', text)
    if years:
        return len(set(years))
    return 0

def extract_projects(text):
    projects = []
    lines = text.split('\n')
    in_projects = False
    for line in lines:
        if re.search(r'PROJECTS?|PORTFOLIO', line.upper()):
            in_projects = True
        elif in_projects and re.search(r'EXPERIENCE|EDUCATION|SKILLS', line.upper()):
            in_projects = False
        elif in_projects and line.strip() and len(line.strip()) > 10:
            if re.match(r'[•\-*]|\d+\.', line.strip()):
                projects.append(line.strip())
    return projects[:5]

# ============================================
# SCORE CALCULATION
# ============================================
def calculate_score(resume_text, skills, companies, univs, email, phone):
    resume_lower = resume_text.lower()
    
    # Skills score (35%)
    skills_score = min(len(skills) * 3.5, 100)
    
    # Contact score (10%)
    contact_score = 0
    if email: contact_score += 50
    if phone: contact_score += 50
    
    # Education score (15%)
    edu_score = 0
    if univs: edu_score += 40
    if extract_degrees(resume_text): edu_score += 60
    edu_score = min(edu_score, 100)
    
    # Experience score (20%)
    exp_score = min(len(companies) * 20, 100)
    
    # Length score (10%)
    word_count = len(resume_text.split())
    if 400 <= word_count <= 800:
        length_score = 100
    elif 250 <= word_count <= 1000:
        length_score = 70
    else:
        length_score = 40
    
    # Achievements score (10%)
    achievements_score = 0
    if re.search(r'\d+%', resume_text): achievements_score += 40
    if re.search(r'\$\d+', resume_text): achievements_score += 30
    if re.search(r'\b(increased|improved|reduced|saved|generated)\b', resume_lower): achievements_score += 30
    
    # Final weighted score
    final_score = (
        0.35 * skills_score +
        0.10 * contact_score +
        0.15 * edu_score +
        0.20 * exp_score +
        0.10 * length_score +
        0.10 * achievements_score
    )
    
    return round(final_score, 2), {
        "skills": round(skills_score, 2),
        "contact": round(contact_score, 2),
        "education": round(edu_score, 2),
        "experience": round(exp_score, 2),
        "length": round(length_score, 2),
        "achievements": round(achievements_score, 2)
    }

# ============================================
# FLAW DETECTION
# ============================================
def detect_flaws(email, phone, skills, univs, companies, projects, resume_text):
    flaws = []
    
    if not email:
        flaws.append({"issue": "Email address missing", "fix": "Add your email at the top of your resume", "severity": "high"})
    if not phone:
        flaws.append({"issue": "Phone number missing", "fix": "Add your phone number with country code", "severity": "high"})
    if len(skills) < 8:
        flaws.append({"issue": f"Only {len(skills)} skills detected", "fix": "Add 10-15 relevant technical and soft skills", "severity": "high"})
    if len(univs) == 0:
        flaws.append({"issue": "No education section found", "fix": "Add your degrees, university names, and graduation years", "severity": "high"})
    if len(companies) < 2:
        flaws.append({"issue": "Limited work experience", "fix": "Add internships, freelance work, or project experience", "severity": "medium"})
    if len(projects) < 2:
        flaws.append({"issue": "Few projects mentioned", "fix": "Add 2-3 key projects with technologies used", "severity": "medium"})
    
    # Check for metrics
    if '%' not in resume_text and len(re.findall(r'\d+', resume_text)) < 5:
        flaws.append({"issue": "Missing measurable achievements", "fix": "Add numbers: 'Increased by 30%', 'Managed team of 10'", "severity": "high"})
    
    return flaws

# ============================================
# AI TIPS GENERATION
# ============================================
def get_ai_tips(resume_text, skills, flaws, field, score):
    skills_str = ", ".join(skills[:10]) if skills else "No specific skills"
    flaws_str = "\n".join([f"- {f['issue']}" for f in flaws[:3]])
    
    prompt = f"""You are an expert ATS resume coach. Give exactly 5 short, actionable tips.

FIELD: {field}
ATS SCORE: {score}/100
SKILLS FOUND: {skills_str}
ISSUES DETECTED: {flaws_str}
RESUME EXCERPT: {resume_text[:1500]}

Return JSON: {{"tips": [{{"title": "Short title (max 50 chars)", "description": "Actionable tip (max 120 chars)", "priority": "high/medium/low"}}]}}"""
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        response = completion.choices[0].message.content
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group()).get('tips', [])
    except Exception as e:
        print(f"AI error: {e}")
    
    # Fallback tips
    return [
        {"title": "🎯 Add More Keywords", "description": "Include industry-specific keywords from job descriptions", "priority": "high"},
        {"title": "📊 Quantify Achievements", "description": "Add numbers: 'Increased sales by 30%', 'Managed team of 10'", "priority": "high"},
        {"title": "📄 Improve Formatting", "description": "Use bullet points and clear section headings", "priority": "medium"},
        {"title": "🔧 Add Skills Section", "description": "Create a dedicated technical skills section", "priority": "medium"},
        {"title": "💼 Show Impact", "description": "Focus on results, not just responsibilities", "priority": "low"}
    ]

def get_ai_suggestions(resume_text, field, score):
    prompt = f"""You are an ATS expert. Give exactly 3 personalized suggestions to improve this {field} resume.

CURRENT SCORE: {score}/100
RESUME: {resume_text[:1500]}

Return JSON: {{"suggestions": [{{"title": "Short title", "description": "What to improve", "action": "How to fix"}}]}}"""
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        response = completion.choices[0].message.content
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group()).get('suggestions', [])
    except:
        pass
    
    return [
        {"title": "Customize for Each Job", "description": "Tailor keywords to match job descriptions", "action": "Copy job description keywords into your resume"},
        {"title": "Add a Summary Section", "description": "Professional summary at the top helps ATS", "action": "Write 2-3 lines about your expertise"},
        {"title": "Include Certifications", "description": "Certifications boost credibility", "action": "Add relevant certifications in a dedicated section"}
    ]

# ============================================
# MAIN FUNCTION
# ============================================
def calculate_ats(resume_text, job_desc=""):
    print("📊 Analyzing resume...")
    
    # Extract all data
    name = extract_name(resume_text)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)
    linkedin = extract_linkedin(resume_text)
    github = extract_github(resume_text)
    location = extract_location(resume_text)
    skills = extract_real_skills(resume_text)
    companies = extract_companies(resume_text)
    universities = extract_universities(resume_text)
    degrees = extract_degrees(resume_text)
    job_titles = extract_job_titles(resume_text)
    experience_years = extract_years_of_experience(resume_text)
    projects = extract_projects(resume_text)
    field = detect_field(resume_text)
    
    # Calculate score
    final_score, breakdown = calculate_score(resume_text, skills, companies, universities, email, phone)
    
    # Detect flaws
    flaws = detect_flaws(email, phone, skills, universities, companies, projects, resume_text)
    
    # Get AI tips and suggestions
    print("🤖 Getting AI recommendations...")
    ai_tips = get_ai_tips(resume_text, skills, flaws, field, final_score)
    ai_suggestions = get_ai_suggestions(resume_text, field, final_score)
    
    # Determine level
    if final_score >= 80:
        level = "excellent"
        level_text = "🚀 Excellent! Very well optimized"
    elif final_score >= 65:
        level = "good"
        level_text = "⭐ Good Score - Minor Improvements Needed"
    elif final_score >= 50:
        level = "average"
        level_text = "📈 Average Score - Needs Some Work"
    else:
        level = "poor"
        level_text = "⚠️ Needs Significant Improvement"
    
    # Prepare featured keywords (most relevant)
    featured_keywords = skills[:15]
    
    return {
        "success": True,
        "final_score": final_score,
        "score_level": level,
        "score_level_text": level_text,
        "score_breakdown": breakdown,
        "detected_field": field,
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "location": location,
        "skills": featured_keywords,
        "skills_count": len(skills),
        "total_skills_found": len(skills),
        "companies": companies,
        "universities": universities,
        "degrees": degrees,
        "job_titles": job_titles,
        "experience_years": experience_years,
        "projects_count": len(projects),
        "projects": projects[:3],
        "flaws": flaws,
        "ai_tips": ai_tips,
        "ai_suggestions": ai_suggestions,
        "word_count": len(resume_text.split())
    }
