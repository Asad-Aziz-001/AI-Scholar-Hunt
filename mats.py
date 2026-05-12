import re
import json
import os
import numpy as np
from collections import Counter
from dotenv import load_dotenv

import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

load_dotenv()

# ============================================================
# INITIALIZATION
# ============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# Load spaCy model (run: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Load SentenceTransformer for semantic similarity
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ============================================================
# COMPREHENSIVE SKILLS DATABASE
# ============================================================
SKILLS_DB = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
        "rust", "swift", "kotlin", "php", "ruby", "scala", "r", "matlab", "perl",
        "shell", "bash", "powershell", "assembly", "dart", "elixir", "haskell"
    ],
    "web_frontend": [
        "react", "reactjs", "angular", "vue", "vuejs", "next.js", "nextjs", "nuxt",
        "svelte", "html", "css", "sass", "scss", "tailwind", "bootstrap", "jquery",
        "webpack", "vite", "redux", "zustand", "graphql", "rest api", "websockets"
    ],
    "web_backend": [
        "django", "flask", "fastapi", "express", "node.js", "nodejs", "spring",
        "spring boot", "laravel", "rails", "asp.net", "gin", "fiber", "nestjs",
        "microservices", "rest", "grpc", "rabbitmq", "kafka", "celery"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "jenkins", "terraform", "ansible", "gitlab ci", "github actions", "ci/cd",
        "linux", "nginx", "apache", "load balancing", "cloudformation", "helm"
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch",
        "oracle", "firebase", "sqlite", "cassandra", "dynamodb", "neo4j",
        "mariadb", "mssql", "sql server", "bigquery", "snowflake", "supabase"
    ],
    "ai_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "sklearn", "pandas", "numpy", "opencv", "nlp",
        "natural language processing", "computer vision", "transformers", "llm",
        "langchain", "rag", "bert", "gpt", "hugging face", "mlops", "data science",
        "neural networks", "reinforcement learning", "xgboost", "lightgbm"
    ],
    "data_analytics": [
        "tableau", "power bi", "excel", "sql", "data analysis", "data visualization",
        "matplotlib", "seaborn", "plotly", "apache spark", "hadoop", "etl",
        "data pipeline", "airflow", "dbt", "looker", "metabase"
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "xamarin", "ionic",
        "swift", "objective-c", "kotlin", "java android"
    ],
    "security": [
        "cybersecurity", "penetration testing", "ethical hacking", "network security",
        "cryptography", "oauth", "jwt", "ssl/tls", "firewalls", "siem", "soc"
    ],
    "design": [
        "figma", "adobe xd", "photoshop", "illustrator", "sketch", "ui/ux",
        "wireframing", "prototyping", "user research", "design systems"
    ],
    "mechanical": [
        "cad", "solidworks", "autocad", "ansys", "catia", "matlab", "simulink",
        "finite element analysis", "fea", "manufacturing", "thermodynamics",
        "fluid mechanics", "3d printing", "cnc", "plc"
    ],
    "electrical": [
        "circuit design", "pcb design", "altium", "eagle", "vhdl", "verilog",
        "fpga", "embedded systems", "arduino", "raspberry pi", "plc", "scada",
        "power systems", "signal processing"
    ],
    "medical": [
        "patient care", "clinical research", "diagnosis", "medical coding",
        "ehr", "hipaa", "icd-10", "cpt coding", "clinical trials", "pharmacology"
    ],
    "finance": [
        "financial analysis", "accounting", "audit", "budgeting", "forecasting",
        "excel", "bloomberg", "risk management", "derivatives", "portfolio management",
        "cfa", "gaap", "ifrs", "erp", "sap"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "agile", "scrum", "kanban",
        "project management", "problem solving", "critical thinking", "mentoring",
        "stakeholder management", "presentation", "negotiation", "time management"
    ],
    "certifications": [
        "aws certified", "azure certified", "google certified", "pmp", "cissp",
        "ceh", "cpa", "cfa", "comptia", "itil", "prince2", "six sigma"
    ]
}

ALL_SKILLS = {}
for category, skills in SKILLS_DB.items():
    for skill in skills:
        ALL_SKILLS[skill] = category

# ============================================================
# FIELD DETECTION
# ============================================================
FIELD_PROFILES = {
    "AI/ML Engineer": {
        "keywords": ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "computer vision", "ai", "llm", "neural", "model"],
        "weight": 1.5
    },
    "Software Engineer": {
        "keywords": ["react", "angular", "django", "flask", "api", "backend", "frontend", "full stack", "microservices", "software development"],
        "weight": 1.3
    },
    "Data Scientist": {
        "keywords": ["data science", "analytics", "pandas", "visualization", "statistics", "tableau", "python", "r", "eda"],
        "weight": 1.4
    },
    "DevOps/Cloud Engineer": {
        "keywords": ["aws", "azure", "gcp", "docker", "kubernetes", "devops", "ci/cd", "terraform", "jenkins"],
        "weight": 1.3
    },
    "Mechanical Engineer": {
        "keywords": ["cad", "solidworks", "autocad", "manufacturing", "thermodynamics", "mechanical", "design engineer"],
        "weight": 1.2
    },
    "Electrical Engineer": {
        "keywords": ["circuit", "pcb", "embedded", "fpga", "vhdl", "verilog", "signal processing", "power systems"],
        "weight": 1.2
    },
    "Medical Professional": {
        "keywords": ["clinical", "patient", "diagnosis", "healthcare", "medical", "nursing", "physician"],
        "weight": 1.3
    },
    "Finance Professional": {
        "keywords": ["finance", "accounting", "audit", "financial analysis", "budgeting", "investment"],
        "weight": 1.2
    },
    "Cybersecurity Analyst": {
        "keywords": ["cybersecurity", "penetration testing", "ethical hacking", "security", "soc", "siem"],
        "weight": 1.3
    },
    "Product Manager": {
        "keywords": ["product management", "roadmap", "stakeholder", "agile", "sprint", "backlog", "user story"],
        "weight": 1.2
    },
    "UI/UX Designer": {
        "keywords": ["figma", "ui/ux", "wireframe", "prototype", "user research", "design system", "adobe xd"],
        "weight": 1.2
    }
}

def detect_field(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for field, profile in FIELD_PROFILES.items():
        score = sum(profile["weight"] for kw in profile["keywords"] if kw in text_lower)
        if score > 0:
            scores[field] = score
    return max(scores, key=scores.get) if scores else "General Professional"

# ============================================================
# TEXT CLEANING
# ============================================================
def clean_text(text: str) -> str:
    text = re.sub(r'\r\n|\r|\n', '\n', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s{3,}', '\n\n', text)
    return text.strip()

def normalize_text(text: str) -> str:
    t = text.lower()
    t = re.sub(r'[^a-zA-Z0-9\s\.\@\+\-\/]', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

# ============================================================
# NLP EXTRACTION USING spaCy
# ============================================================
def extract_name(text: str) -> str:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Strong heuristic: first line
    first = lines[0]
    if 2 <= len(first.split()) <= 4 and first.replace(" ", "").isalpha():
        return first
    
    # spaCy fallback
    doc = nlp(text[:1500])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()
    
    return "Not Detected"

def extract_email(text: str) -> str:
    match = re.search(r'[\w\.\+\-]+@[\w\.\-]+\.[a-zA-Z]{2,}', text)
    return match.group().lower() if match else None

def extract_phone(text: str) -> str:
    patterns = [
        r'\+?\d{1,3}[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}',
        r'\+\d{2,3}[\s\-]?\d{10,11}',
        r'0\d{10}',
        r'\d{4}[\s\-]\d{7}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group().strip()
    return None

def extract_linkedin(text: str) -> str:
    match = re.search(r'(?:linkedin\.com/in/|linkedin\.com/pub/)[\w\-]+', text.lower())
    return match.group() if match else None

def extract_github(text: str) -> str:
    match = re.search(r'github\.com/[\w\-]+', text.lower())
    return match.group() if match else None

def extract_location_spacy(text: str) -> str:
    doc = nlp(text[:3000])
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            return ent.text.strip()
    
    patterns = [
        r'(?:Location|Address|City|Based in)[:\s]+([A-Za-z\s,\.]+)',
        r'([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)+)',
    ]
    for p in patterns:
        match = re.search(p, text[:500])
        if match:
            return match.group(1).strip()
    return None

def extract_skills_advanced(text: str) -> list:
    """Multi-method skill extraction: exact match + spaCy NER + phrase matching"""
    text_lower = text.lower()
    found_skills = {}
    
    # Method 1: Exact keyword matching
    for skill, category in ALL_SKILLS.items():
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills[skill] = category
    
    # Method 2: spaCy entity-based (org names often = tools)
    doc = nlp(text[:5000])
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            ent_lower = ent.text.lower().strip()
            if ent_lower in ALL_SKILLS:
                found_skills[ent_lower] = ALL_SKILLS[ent_lower]
    
    # Organize by category
    by_category = {}
    for skill, cat in found_skills.items():
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)
    
    # Sort: technical skills first
    priority_order = ["programming", "ai_ml", "web_backend", "web_frontend", "cloud_devops",
                      "databases", "data_analytics", "mobile", "security", "soft_skills"]
    
    ordered = []
    for cat in priority_order:
        if cat in by_category:
            ordered.extend(by_category[cat])
    for cat, skills in by_category.items():
        if cat not in priority_order:
            ordered.extend(skills)
    
    return list(dict.fromkeys(ordered))[:30]

def extract_education_spacy(text: str) -> dict:
    """Extract universities and degrees using spaCy + patterns"""
    doc = nlp(text[:5000])
    
    universities = []
    # spaCy ORG entities that contain university keywords
    for ent in doc.ents:
        if ent.label_ == "ORG":
            t = ent.text.lower()
            if any(k in t for k in ['university', 'college', 'institute', 'school', 'academy']):
                universities.append(ent.text.strip())
    
    # Pattern-based fallback
    univ_patterns = [
        r'([A-Z][A-Za-z\s]+(?:University|College|Institute|School|Academy))',
        r'(University|College|Institute)\s+of\s+[A-Z][A-Za-z\s]+',
    ]
    for p in univ_patterns:
        for m in re.finditer(p, text):
            name = m.group().strip()
            if name not in universities and len(name) > 5:
                universities.append(name)
    
    # Known Pakistani/international universities
    known = ['UET', 'NUST', 'LUMS', 'FAST', 'GIKI', 'IBA', 'COMSATS', 'SZABIST',
             'MIT', 'Harvard', 'Stanford', 'Oxford', 'Cambridge', 'NED', 'UCP', 'PUCIT']
    for u in known:
        if u.lower() in text.lower() and u not in universities:
            universities.append(u)
    
    # Degrees
    degree_pattern = r'\b(Bachelor\'?s?|Master\'?s?|PhD|Ph\.D|B\.?Tech|M\.?Tech|BS|MS|BE|ME|BSc|MSc|MBA|BBA|MCA|BCA|MBBS|MD|BEng|MEng)\b'
    degrees = list(dict.fromkeys(re.findall(degree_pattern, text, re.IGNORECASE)))
    
    # GPA
    gpa_match = re.search(r'(?:GPA|CGPA)[:\s]*(\d+\.\d+)\s*(?:/\s*(\d+\.\d+))?', text, re.IGNORECASE)
    gpa = gpa_match.group(0) if gpa_match else None
    
    return {
        "universities": list(dict.fromkeys(universities))[:4],
        "degrees": degrees[:4],
        "gpa": gpa
    }

def extract_achievements(text: str) -> list:
    """Extract quantifiable achievements"""
    achievements = []
    
    # Pattern: number + impact verb or percentage
    patterns = [
        r'(?:increased|improved|reduced|saved|generated|achieved|grew|boosted|cut|decreased)\s+[^.]+\d+[%$+]?[^.]*\.',
        r'\d+[%$]\s+(?:increase|decrease|improvement|reduction|growth)',
        r'(?:team of|managed|led|supervised)\s+\d+\s+(?:people|members|engineers|employees)',
        r'\$[\d,]+(?:K|M|B)?\s+(?:revenue|savings|budget|funding)',
    ]
    
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            achievement = m.group().strip()
            if len(achievement) > 10:
                achievements.append(achievement[:150])
    
    return list(dict.fromkeys(achievements))[:5]

def extract_certifications(text: str) -> list:
    """Extract certifications"""
    cert_patterns = [
        r'(?:AWS|Azure|Google Cloud|GCP)\s+(?:Certified|Professional|Associate|Developer|Architect)[^\n]*',
        r'(?:PMP|CISSP|CEH|CPA|CFA|CISM|CISA|CompTIA[^\n]*|ITIL[^\n]*|Prince2[^\n]*)',
        r'(?:Certified|Certificate)\s+(?:in\s+)?[A-Z][A-Za-z\s]+',
    ]
    certs = []
    for p in cert_patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            cert = m.group().strip()
            if len(cert) > 8 and len(cert) < 100:
                certs.append(cert)
    return list(dict.fromkeys(certs))[:6]

def extract_languages(text: str) -> list:
    """Extract spoken languages"""
    lang_section = re.search(r'(?:Languages?|Language Skills?)[:\s]*([^\n]+(?:\n[^\n]+){0,3})', text, re.IGNORECASE)
    if lang_section:
        return [l.strip() for l in re.split(r'[,|•\-]', lang_section.group(1)) if l.strip() and len(l.strip()) > 2][:5]
    return []

def extract_projects(text: str) -> list:
    """Extract project names and descriptions"""
    projects = []
    
    proj_section = re.search(r'(?:PROJECTS?|PORTFOLIO)[:\s]*\n((?:.+\n?)+?)(?:\n[A-Z]{2,}|\Z)', text, re.IGNORECASE)
    if proj_section:
        lines = [l.strip() for l in proj_section.group(1).split('\n') if l.strip() and len(l.strip()) > 15]
        projects = lines[:5]
    
    return projects

# ============================================================
# SEMANTIC SIMILARITY SCORING (SentenceTransformer)
# ============================================================
def compute_semantic_score(resume_text: str, job_desc: str = "") -> float:
    """Compute semantic similarity between resume and a reference profile"""
    
    # If no job description, compare against ideal resume template
    if not job_desc:
        job_desc = """Experienced professional with strong technical skills, problem-solving abilities,
        relevant education, certifications, measurable achievements and leadership qualities."""
    
    try:
        embeddings = embedding_model.encode([resume_text[:3000], job_desc])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(similarity)
    except Exception:
        return 0.5

# ============================================================
# MULTI-FACTOR SCORING ENGINE
# ============================================================
def compute_ats_score(resume_text: str, parsed_data: dict, job_desc: str = "") -> dict:
    """Advanced multi-factor ATS scoring engine"""
    
    text_lower = resume_text.lower()
    skills = parsed_data.get("skills", [])
    email = parsed_data.get("email")
    phone = parsed_data.get("phone")
    education = parsed_data.get("education", {})
    achievements = parsed_data.get("achievements", [])
    certifications = parsed_data.get("certifications", [])
    word_count = len(resume_text.split())
    
    scores = {}
    
    # 1. SKILLS SCORE (25%)
    skill_count = len(skills)
    if skill_count >= 20:
        scores["skills"] = 100
    elif skill_count >= 15:
        scores["skills"] = 90
    elif skill_count >= 10:
        scores["skills"] = 75
    elif skill_count >= 6:
        scores["skills"] = 55
    elif skill_count >= 3:
        scores["skills"] = 35
    else:
        scores["skills"] = 10
    
    # 2. CONTACT INFO SCORE (10%)
    contact = 0
    if email: contact += 40
    if phone: contact += 35
    if parsed_data.get("linkedin"): contact += 15
    if parsed_data.get("github"): contact += 10
    scores["contact"] = min(contact, 100)
    
    # 3. EDUCATION SCORE (15%)
    edu_score = 0
    univs = education.get("universities", [])
    degrees = education.get("degrees", [])
    gpa = education.get("gpa")
    if univs: edu_score += 40
    if degrees: edu_score += 40
    if gpa: edu_score += 20
    scores["education"] = min(edu_score, 100)
    
    # 4. EXPERIENCE SCORE (20%)
    
    # 5. CONTENT QUALITY (15%)
    content_score = 0
    if 400 <= word_count <= 900:
        content_score += 40
    elif 250 <= word_count <= 1200:
        content_score += 25
    else:
        content_score += 10
    
    # Section headers
    section_words = ['education', 'skills', 'projects', 'summary', 'objective', 'certifications', 'achievements']
    found_sections = sum(1 for s in section_words if s in text_lower)
    content_score += min(found_sections * 8, 40)
    
    # Bullet points
    bullet_count = len(re.findall(r'[•\-\*]|\d+\.', resume_text))
    content_score += min(bullet_count * 2, 20)
    scores["content_quality"] = min(content_score, 100)
    
    # 6. ACHIEVEMENTS SCORE (10%)
    ach_score = 0
    if re.search(r'\d+%', resume_text): ach_score += 35
    if re.search(r'\$[\d,]+', resume_text): ach_score += 25
    if len(achievements) >= 3: ach_score += 25
    elif len(achievements) >= 1: ach_score += 15
    action_verbs = ['led', 'managed', 'developed', 'implemented', 'improved', 'created', 'built', 'designed', 'achieved', 'delivered']
    ach_score += min(sum(3 for v in action_verbs if re.search(rf'\b{v}\b', text_lower)), 15)
    scores["achievements"] = min(ach_score, 100)
    
    # 7. CERTIFICATIONS (15%)
    scores["certifications"] = min(len(certifications) * 25, 100)
    
    # WEIGHTED FINAL SCORE
    weights = {
        "skills": 0.25,
        "contact": 0.15,
        "education": 0.15,
        "content_quality": 0.15,
        "achievements": 0.15,
        "certifications": 0.15
    }
    
    final = sum(scores[k] * weights[k] for k in scores)
    
    # Semantic bonus (up to +5 points)
    if job_desc:
        semantic_sim = compute_semantic_score(resume_text, job_desc)
        semantic_bonus = semantic_sim * 5
        final = min(final + semantic_bonus, 100)
    
    return {
        "final_score": round(final, 1),
        "breakdown": {k: round(v, 1) for k, v in scores.items()}
    }

# ============================================================
# FLAW DETECTION ENGINE
# ============================================================
def detect_flaws(parsed_data: dict, resume_text: str) -> list:
    """Detect all resume weaknesses with severity levels"""
    flaws = []
    text_lower = resume_text.lower()
    
    email = parsed_data.get("email")
    phone = parsed_data.get("phone")
    skills = parsed_data.get("skills", [])
    education = parsed_data.get("education", {})
    achievements = parsed_data.get("achievements", [])
    word_count = len(resume_text.split())
    
    # Critical flaws
    if not email:
        flaws.append({"issue": "Email address missing", "fix": "Add professional email at the very top of your resume", "severity": "critical"})
    if not phone:
        flaws.append({"issue": "Phone number missing", "fix": "Include phone number with country code (e.g., +92-XXX-XXXXXXX)", "severity": "critical"})
    if len(skills) < 5:
        flaws.append({"issue": f"Very few skills detected ({len(skills)})", "fix": "Add a dedicated Skills section with 12-18 technical and soft skills", "severity": "critical"})
    
    # High severity
    if len(education.get("universities", [])) == 0:
        flaws.append({"issue": "No education/university detected", "fix": "Add Education section with university name, degree, and graduation year", "severity": "high"})
    if len(education.get("degrees", [])) == 0:
        flaws.append({"issue": "No degree information found", "fix": "Mention your degree clearly (e.g., Bachelor of Science in Computer Science)", "severity": "high"})
    if word_count < 250:
        flaws.append({"issue": f"Resume too short ({word_count} words)", "fix": "Aim for 400-700 words – elaborate on projects and experience", "severity": "high"})
    if word_count > 1200:
        flaws.append({"issue": f"Resume too long ({word_count} words)", "fix": "Trim to 1-2 pages – remove irrelevant details", "severity": "medium"})
    
    # Medium severity
    if len(achievements) < 2:
        flaws.append({"issue": "No quantifiable achievements", "fix": "Add numbers: 'Increased performance by 40%', 'Managed team of 8', 'Saved $10K'", "severity": "high"})
    if not parsed_data.get("linkedin"):
        flaws.append({"issue": "LinkedIn profile not included", "fix": "Add your LinkedIn URL – recruiters always check", "severity": "medium"})
    
    # Low severity
    if not parsed_data.get("github") and any(s in skills for s in ["python", "javascript", "java", "react", "django"]):
        flaws.append({"issue": "No GitHub profile (technical resume)", "fix": "Add your GitHub – shows real coding work to technical recruiters", "severity": "low"})
    
    action_verbs = ['led', 'managed', 'developed', 'implemented', 'built', 'designed', 'achieved']
    action_count = sum(1 for v in action_verbs if re.search(rf'\b{v}\b', text_lower))
    if action_count < 3:
        flaws.append({"issue": "Weak action verbs", "fix": "Start bullet points with strong verbs: Developed, Implemented, Architected, Led, Optimized", "severity": "low"})
    
    section_words = [ 'education', 'skills', 'projects']
    missing_sections = [s for s in section_words if s not in text_lower]
    if missing_sections:
        flaws.append({"issue": f"Missing key sections: {', '.join(missing_sections)}", "fix": f"Add clearly labeled sections: {', '.join(missing_sections)}", "severity": "medium"})
    
    return flaws

# ============================================================
# GROQ AI: TIPS & SUGGESTIONS
# ============================================================
def get_groq_ai_analysis(resume_text: str, parsed_data: dict, flaws: list, field: str, score: float) -> dict:
    """Get comprehensive AI analysis from Groq LLaMA"""
    
    skills_str = ", ".join(parsed_data.get("skills", [])[:12])
    flaws_str = "\n".join([f"- [{f['severity'].upper()}] {f['issue']}" for f in flaws[:5]])
    
    prompt = f"""You are a world-class ATS resume expert and career coach. Analyze this resume data and provide SPECIFIC, ACTIONABLE feedback.

CANDIDATE PROFILE:
- Field: {field}
- ATS Score: {score}/100
- Skills Found: {skills_str}
- Word Count: {len(resume_text.split())}

DETECTED ISSUES:
{flaws_str}

RESUME TEXT (first 2000 chars):
{resume_text[:2000]}

Return ONLY valid JSON (no markdown, no backticks):
{{
  "overall_verdict": "One sentence verdict about the resume quality",
  "top_strength": "The biggest strength of this resume",
  "critical_fix": "The single most important thing to fix right now",
  "tips": [
    {{
      "title": "Concise title (max 60 chars)",
      "description": "Specific, actionable tip for THIS resume (max 150 chars)",
      "priority": "high",
      "category": "keywords|formatting|content|education|skills"
    }}
  ],
  "suggestions": [
    {{
      "title": "Short improvement title",
      "description": "What exactly to improve",
      "action": "Specific action step",
      "impact": "Expected impact on ATS score"
    }}
  ],
  "missing_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "score_prediction": "What score you can reach after fixes"
}}

Generate exactly 5 tips and 3 suggestions. Be specific to this person's resume, not generic advice."""

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.65,
            max_tokens=1500
        )
        response = completion.choices[0].message.content.strip()
        
        # Clean JSON
        response = re.sub(r'^```json\s*', '', response)
        response = re.sub(r'^```\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
        
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"Groq AI error: {e}")
    
    # Structured fallback
    return {
        "overall_verdict": f"Your resume scores {score}/100 – targeted improvements can boost it significantly.",
        "top_strength": "Technical skills foundation present",
        "critical_fix": "Add quantifiable achievements with specific numbers",
        "tips": [
            {"title": "Add Measurable Achievements", "description": "Use format: Action + Number + Result. e.g., 'Built API serving 10K daily users'", "priority": "high", "category": "content"},
            {"title": "Keyword Optimization", "description": "Mirror exact keywords from target job descriptions in your skills section", "priority": "high", "category": "keywords"},
            {"title": "Professional Summary", "description": "Add 3-line summary at top: role + years + top 3 skills + goal", "priority": "medium", "category": "formatting"},
            {"title": "Quantify Education", "description": "Add CGPA if above 3.0/4.0 or 70% – strong academic scores impress ATS", "priority": "medium", "category": "education"},
            {"title": "Action Verb Upgrade", "description": "Replace passive language with: Engineered, Architected, Spearheaded, Delivered", "priority": "low", "category": "content"}
        ],
        "suggestions": [
            {"title": "Tailor for Each Application", "description": "Customize skills section per job posting", "action": "Copy 5-8 keywords from the JD and naturally integrate them", "impact": "+10-15 ATS points"},
            {"title": "LinkedIn Profile Link", "description": "Recruiters verify candidates on LinkedIn", "action": "Add linkedin.com/in/yourname in contact section", "impact": "+5 ATS points"},
            {"title": "Projects Section", "description": "Real projects prove skills better than claims", "action": "Add 2-3 projects with: name, tech stack, and measurable outcome", "impact": "+8-12 ATS points"}
        ],
        "missing_keywords": ["professional summary", "leadership", "collaboration", "agile", "communication"],
        "score_prediction": f"Can reach {min(int(score) + 20, 95)}/100 with targeted improvements"
    }

# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================
def calculate_ats(resume_text: str, job_desc: str = "") -> dict:
    """
    Master ATS analysis pipeline:
    Text → Clean → spaCy NLP → Embedding → Scoring → Groq AI → Results
    """
    print("🔍 Starting ATS analysis pipeline...")
    
    # Step 1: Clean text
    clean = clean_text(resume_text)
    
    # Step 2: NLP Extraction (spaCy)
    print("  → Running spaCy NLP extraction...")
    name = extract_name(clean)
    email = extract_email(clean)
    phone = extract_phone(clean)
    linkedin = extract_linkedin(clean)
    github = extract_github(clean)
    location = extract_location_spacy(clean)
    skills = extract_skills_advanced(clean)
    education = extract_education_spacy(clean)
    achievements = extract_achievements(clean)
    certifications = extract_certifications(clean)
    languages = extract_languages(clean)
    projects = extract_projects(clean)
    field = detect_field(clean)
    
    # Step 3: Compile parsed data
    parsed_data = {
        "name": name, "email": email, "phone": phone,
        "linkedin": linkedin, "github": github, "location": location,
        "skills": skills, "education": education,
        "achievements": achievements, "certifications": certifications,
        "languages": languages, "projects": projects
    }
    
    # Step 4: Semantic embedding + multi-factor scoring
    print("  → Computing ATS score (Sentence Transformers + multi-factor)...")
    score_result = compute_ats_score(clean, parsed_data, job_desc)
    final_score = score_result["final_score"]
    score_breakdown = score_result["breakdown"]
    
    # Step 5: Flaw detection
    flaws = detect_flaws(parsed_data, clean)
    
    # Step 6: Groq AI analysis
    print("  → Getting Groq AI recommendations...")
    ai_analysis = get_groq_ai_analysis(clean, parsed_data, flaws, field, final_score)
    
    # Step 7: Determine level
    if final_score >= 85: level, level_text = "exceptional", "🏆 Exceptional – Top 5% resumes"
    elif final_score >= 75: level, level_text = "excellent", "🚀 Excellent – Well optimized"
    elif final_score >= 65: level, level_text = "good", "⭐ Good – Minor improvements needed"
    elif final_score >= 50: level, level_text = "average", "📈 Average – Significant improvements needed"
    else: level, level_text = "poor", "⚠️ Needs Major Improvement"
    
    print(f"  ✅ Analysis complete. Score: {final_score}/100")
    
    return {
        "success": True,
        
        # Score
        "final_score": final_score,
        "score_level": level,
        "score_level_text": level_text,
        "score_breakdown": score_breakdown,
        
        # Field
        "detected_field": field,
        
        # Candidate Info
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "location": location,
        
        # Skills
        "skills": skills[:20],
        "skills_count": len(skills),
        
        # Education
        "universities": education["universities"],
        "degrees": education["degrees"],
        "gpa": education["gpa"],
        
        # Content
        "certifications": certifications,
        "achievements": achievements,
        "projects": projects[:3],
        "projects_count": len(projects),
        "languages": languages,
        "word_count": len(clean.split()),
        
        # Flaws
        "flaws": flaws,
        
        # AI Analysis
        "overall_verdict": ai_analysis.get("overall_verdict", ""),
        "top_strength": ai_analysis.get("top_strength", ""),
        "critical_fix": ai_analysis.get("critical_fix", ""),
        "ai_tips": ai_analysis.get("tips", []),
        "ai_suggestions": ai_analysis.get("suggestions", []),
        "missing_keywords": ai_analysis.get("missing_keywords", []),
        "score_prediction": ai_analysis.get("score_prediction", ""),
    }
