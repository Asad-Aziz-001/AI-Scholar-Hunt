# ==============================================================
#                    AI Scholar Hunt
#                      chatbot.py (FIXED MODELS)
# ==============================================================
import os
import glob
import json
import time
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ Updated working models (as of April 2026)
# From Groq's current available models
WORKING_MODELS = [
    "llama-3.3-70b-versatile",    # Most capable, higher rate limits
    "llama-3.1-8b-instant",       # Fast, good for simple tasks
    "llama-3.2-3b-preview",       # Small, very fast
    "gemma2-9b-it",               # Google's model
    "qwen-2.5-32b",               # Good for long context
]

# Default model (most reliable)
MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

MAX_TOKENS = 1500
MAX_CONTEXT_CHARS = 5000

client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHOLARSHIPS_FOLDER = os.path.join(BASE_DIR, "scholarships")

_scholarships_cache: list[dict] = []


# ==============================================================
#  1. LOAD SCHOLARSHIPS
# ==============================================================
def load_scholarships() -> list[dict]:
    global _scholarships_cache

    if _scholarships_cache:
        return _scholarships_cache

    if not os.path.exists(SCHOLARSHIPS_FOLDER):
        print(f"⚠️ Scholarships folder not found: {SCHOLARSHIPS_FOLDER}")
        return []

    txt_files = glob.glob(os.path.join(SCHOLARSHIPS_FOLDER, "*.txt"))
    json_files = glob.glob(os.path.join(SCHOLARSHIPS_FOLDER, "*.json"))
    all_files = txt_files + json_files

    if not all_files:
        print(f"⚠️ No files found in {SCHOLARSHIPS_FOLDER}")
        return []

    loaded = []
    for filepath in all_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                continue

            filename = os.path.basename(filepath)
            
            scholarship_data = parse_scholarship_file(content, filename)
            
            if scholarship_data:
                formatted = format_complete_scholarship(scholarship_data)
                loaded.append({
                    "name": scholarship_data.get("scholarship_name", filename.replace('.txt', '').replace('_', ' ').title()),
                    "filename": filename,
                    "content": formatted,
                    "raw_data": scholarship_data,
                    "search_text": (scholarship_data.get("scholarship_name", "") + " " + 
                                   scholarship_data.get("institution", "") + " " + 
                                   scholarship_data.get("study_in", "")).lower()
                })
                print(f"  ✅ Loaded: {scholarship_data.get('scholarship_name', filename)[:60]}")

        except Exception as e:
            print(f"  ❌ Error reading {filepath}: {e}")

    _scholarships_cache = loaded
    print(f"\n📚 Total scholarships loaded: {len(loaded)}\n")
    return loaded


# ==============================================================
#  2. PARSE SCHOLARSHIP FILE
# ==============================================================
def parse_scholarship_file(content: str, filename: str) -> dict:
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data
    except:
        pass
    
    data = {
        "scholarship_name": filename.replace('.txt', '').replace('_', ' ').replace('-', ' ').title(),
        "level_of_study": [],
        "required_documents": [],
        "additional_benefits": []
    }
    
    lines = content.split('\n')
    current_key = None
    current_value = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$', line)
        if match:
            if current_key and current_value:
                store_field(data, current_key, ' '.join(current_value))
            current_key = match.group(1).lower()
            current_value = [match.group(2)]
        else:
            if current_value:
                current_value.append(line)
    
    if current_key and current_value:
        store_field(data, current_key, ' '.join(current_value))
    
    return data


def store_field(data: dict, key: str, value: str):
    if not value:
        return
    
    key_map = {
        'scholarship_name': 'scholarship_name', 'name': 'scholarship_name',
        'level_of_study': 'level_of_study', 'level': 'level_of_study',
        'institution': 'institution', 'university': 'institution',
        'study_in': 'study_in', 'country': 'study_in',
        'courses_offered': 'courses_offered', 'courses': 'courses_offered',
        'deadline': 'deadline', 'application_deadline': 'deadline',
        'coverage': 'coverage', 'benefits': 'coverage',
        'eligibility': 'eligibility', 'requirements': 'eligibility',
        'required_documents': 'required_documents', 'documents': 'required_documents',
        'apply_link': 'apply_link', 'link': 'apply_link', 'url': 'apply_link',
        'official_website': 'official_website', 'website': 'official_website',
        'notes': 'notes', 'description': 'notes'
    }
    
    mapped = key_map.get(key, key)
    
    if mapped in ['level_of_study', 'courses_offered', 'required_documents']:
        items = [item.strip() for item in re.split(r'[,|•\-]\s*', value) if item.strip()]
        if items:
            if mapped not in data or not isinstance(data[mapped], list):
                data[mapped] = []
            data[mapped].extend(items)
    else:
        data[mapped] = value


# ==============================================================
#  3. FORMAT SCHOLARSHIP DETAILS
# ==============================================================
def format_complete_scholarship(data: dict) -> str:
    parts = []
    
    parts.append("=" * 55)
    parts.append(f"🎓 {data.get('scholarship_name', 'Scholarship Information')}")
    parts.append("=" * 55)
    
    parts.append("\n📌 BASIC INFORMATION")
    if data.get("institution"):
        parts.append(f"   • Institution: {data['institution']}")
    if data.get("study_in"):
        parts.append(f"   • Country: {data['study_in']}")
    if data.get("level_of_study"):
        levels = ", ".join(data["level_of_study"]) if isinstance(data["level_of_study"], list) else data["level_of_study"]
        parts.append(f"   • Level: {levels}")
    
    if data.get("deadline"):
        parts.append(f"\n⏰ DEADLINE")
        parts.append(f"   • {data['deadline']}")
    
    if data.get("coverage"):
        parts.append(f"\n💰 COVERAGE & BENEFITS")
        coverage = data["coverage"]
        if isinstance(coverage, dict):
            for k, v in coverage.items():
                if k != 'additional_benefits':
                    parts.append(f"   • {k.replace('_', ' ').title()}: {v}")
        else:
            parts.append(f"   • {coverage}")
    
    if data.get("eligibility"):
        parts.append(f"\n✅ ELIGIBILITY")
        parts.append(f"   • {data['eligibility']}")
    
    if data.get("required_documents"):
        parts.append(f"\n📄 REQUIRED DOCUMENTS")
        docs = data["required_documents"]
        if isinstance(docs, list):
            for doc in docs[:8]:
                parts.append(f"   • {doc}")
        else:
            parts.append(f"   • {docs}")
    
    if data.get("apply_link"):
        parts.append(f"\n🔗 APPLICATION LINK")
        parts.append(f"   • {data['apply_link']}")
    if data.get("official_website") and data.get("official_website") != data.get("apply_link"):
        parts.append(f"   • Official Website: {data['official_website']}")
    
    parts.append("\n" + "=" * 55)
    
    return "\n".join(parts)


# ==============================================================
#  4. SEARCH SCHOLARSHIPS
# ==============================================================
def search_scholarships(user_message: str, max_results: int = 1) -> list[dict]:
    scholarships = load_scholarships()
    if not scholarships:
        return []
    
    user_lower = user_message.lower()
    
    keywords = []
    important_terms = ['harvard', 'daad', 'fulbright', 'bilkent', 'csc', 'chevening', 
                       'germany', 'usa', 'canada', 'turkey', 'uk', 'australia', 'dubai']
    
    for term in important_terms:
        if term in user_lower:
            keywords.append(term)
    
    if not keywords:
        keywords = [w for w in user_lower.split() if len(w) > 3]
    
    scored = []
    for s in scholarships:
        score = 0
        search_text = s.get('search_text', s['name'].lower())
        
        for kw in keywords:
            if kw in search_text or kw in s['name'].lower():
                score += 10
            if kw in s['content'].lower():
                score += 3
        
        if score > 0:
            scored.append((score, s))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:max_results]]


# ==============================================================
#  5. GET RESPONSE (WITH MODEL FALLBACK)
# ==============================================================
def get_response(user_message: str, matched_scholarships: list[dict] = None) -> str:
    if matched_scholarships is None:
        matched_scholarships = search_scholarships(user_message)
    
    if matched_scholarships:
        context_block = matched_scholarships[0]['content']
        instruction = "Provide COMPLETE details from the scholarship data above."
    else:
        context_block = "No matching scholarship found."
        instruction = "Politely say no matching scholarship found."
    
    if len(user_message) > 500:
        user_message = user_message[:500]
    
    system_prompt = f"""You are "AI Scholar Hunt" - a scholarship assistant for Pakistani students.

SCHOLARSHIP DATA:
{context_block}

INSTRUCTIONS:
1. Answer in SAME language as user
2. Give COMPLETE details - don't skip anything
3. Include apply link if present
4. Use emojis and bullet points
5. {instruction}

Be thorough and helpful!"""

    # Try multiple models in sequence
    models_to_try = [MODEL] + [m for m in WORKING_MODELS if m != MODEL]
    
    for model_attempt in models_to_try[:3]:  # Try up to 3 different models
        for retry in range(2):
            try:
                response = client.chat.completions.create(
                    model=model_attempt,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=MAX_TOKENS,
                    temperature=0.5,
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e).lower()
                if "model" in error_msg and ("decommissioned" in error_msg or "not found" in error_msg):
                    print(f"⚠️ Model {model_attempt} failed, trying next...")
                    break  # Try next model
                elif "rate_limit" in error_msg or "tokens" in error_msg:
                    print(f"⚠️ Rate limit on {model_attempt}, retry {retry+1}")
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ Error with {model_attempt}: {e}")
                    break
    
    # If all models fail, return raw scholarship data
    if matched_scholarships:
        return matched_scholarships[0]['content']
    
    return "I'm having trouble connecting. Please try again in a moment."


# ==============================================================
#  6. HELPER FUNCTIONS
# ==============================================================
def get_all_scholarship_names() -> list:
    scholarships = load_scholarships()
    return [s["name"] for s in scholarships]

def clear_cache():
    global _scholarships_cache
    _scholarships_cache = []
    print("✅ Cache cleared")
