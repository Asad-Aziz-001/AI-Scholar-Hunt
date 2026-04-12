"""
chatbot.py — Scholarship Chatbot Engine
========================================
Handles loading scholarship data from .txt files and
searching/responding to user queries.

⚠️  IMPORTANT: Do NOT create Flask() app here.
    This module is imported by app.py and used there.

Functions:
    load_scholarships()                 → Load all .txt files from scholarships/
    search_scholarships(query)          → Score and rank matching scholarships
    get_response(query, matched_list)   → Build formatted reply string
"""

import json
import os
import re


# ==============================================================
#   Global Scholarship List
#   Populated once at startup via load_scholarships()
# ==============================================================
scholarships = []


# ==============================================================
#   Load Scholarships from Files
# ==============================================================

def load_scholarships(folder: str = 'scholarships') -> list:
    """
    Load all scholarship .txt files from the given folder.
    Each file should contain JSON data, or plain text as fallback.

    Args:
        folder: Path to the scholarships folder (relative to app root).

    Returns:
        List of scholarship dictionaries.
    """
    global scholarships
    scholarships = []

    # Check if folder exists
    if not os.path.exists(folder):
        print(f"❌ '{folder}' folder not found. Creating it...")
        os.makedirs(folder)
        print(f"✅ Created '{folder}'. Please add scholarship .txt files.")
        return scholarships

    # Read each .txt file
    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(folder, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Try JSON parsing first
            if content.startswith('{'):
                data = json.loads(content)
            else:
                # Fallback: plain text wrapped in basic structure
                data = {
                    "scholarship_name": filename.replace('.txt', ''),
                    "description": content
                }

            data['_filename'] = filename
            scholarships.append(data)
            print(f"✅ Loaded: {data.get('scholarship_name', filename)}")

        except json.JSONDecodeError as e:
            print(f"❌ JSON error in {filename}: {e}")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")

    print(f"\n✅ Total {len(scholarships)} scholarships loaded.\n")
    return scholarships


# ==============================================================
#   Text Normalization
# ==============================================================

def normalize(text: str) -> str:
    """
    Lowercase, strip punctuation, and strip whitespace for comparison.

    Args:
        text: Any string.

    Returns:
        Normalized lowercase string.
    """
    return re.sub(r'[^a-z0-9\s]', '', str(text).lower().strip())


# ==============================================================
#   Scholarship Search (Scoring System)
# ==============================================================

def search_scholarships(query: str) -> list:
    """
    Search all loaded scholarships and return scored results.

    Scoring weights:
        Scholarship name match  → 100 pts
        Country match           →  50 pts
        Institution match       →  40 pts
        Level of study match    →  30 pts
        Full text word match    →  10 pts per word

    Args:
        query: User's search query string.

    Returns:
        List of (scholarship_dict, score) tuples, sorted by score (descending).
    """
    query_norm  = normalize(query)
    query_words = query_norm.split()

    scored = []

    for sch in scholarships:
        score = 0

        # Name match (highest priority)
        name = normalize(sch.get('scholarship_name', ''))
        if query_norm in name or name in query_norm:
            score += 100

        # Country match
        country = normalize(sch.get('study_in', ''))
        if any(word in country for word in query_words):
            score += 50

        # Institution match
        institution = normalize(sch.get('institution', ''))
        if any(word in institution for word in query_words):
            score += 40

        # Level of study match
        level_text = json.dumps(sch.get('level_of_study', [])).lower()
        if any(word in level_text for word in query_words):
            score += 30

        # Full JSON text match
        full_text = json.dumps(sch, ensure_ascii=False).lower()
        for word in query_words:
            if len(word) > 2 and word in full_text:
                score += 10

        if score > 0:
            scored.append((sch, score))

    # Sort by score (highest first)
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


# ==============================================================
#   Format Single Scholarship Details
# ==============================================================

def format_scholarship_detail(sch: dict) -> str:
    """
    Format a complete scholarship dictionary into readable markdown-style text.

    Args:
        sch: Scholarship dictionary.

    Returns:
        Formatted string with all available scholarship fields.
    """
    lines = []

    lines.append(f"**🎓 {sch.get('scholarship_name', 'Scholarship')}**\n")

    if sch.get('study_in'):
        lines.append(f"**🌍 Country:** {sch['study_in']}")

    if sch.get('institution'):
        lines.append(f"**🏛️ Institution:** {sch['institution']}")

    if sch.get('level_of_study'):
        levels = ', '.join(sch['level_of_study']) if isinstance(sch['level_of_study'], list) else sch['level_of_study']
        lines.append(f"**📚 Level:** {levels}")

    if sch.get('courses_offered'):
        lines.append(f"\n**📖 Courses Offered:**")
        courses = sch['courses_offered'] if isinstance(sch['courses_offered'], list) else [sch['courses_offered']]
        for course in courses[:15]:
            lines.append(f"  • {course}")
        if len(courses) > 15:
            lines.append(f"  • ... and {len(courses) - 15} more")

    if sch.get('program_period'):
        lines.append(f"\n**⏳ Duration:**")
        period = sch['program_period']
        if isinstance(period, dict):
            for level, duration in period.items():
                lines.append(f"  • {level}: {duration}")
        else:
            lines.append(f"  • {period}")

    if sch.get('deadline'):
        lines.append(f"\n**⏰ Deadline:** {sch['deadline']}")

    if sch.get('coverage'):
        lines.append(f"\n**💰 Coverage:**")
        coverage = sch['coverage']
        if isinstance(coverage, dict):
            for key, value in coverage.items():
                label = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    lines.append(f"  • {label}:")
                    for k, v in value.items():
                        lines.append(f"    - {k}: {v}")
                elif isinstance(value, list):
                    lines.append(f"  • {label}:")
                    for item in value:
                        lines.append(f"    - {item}")
                else:
                    lines.append(f"  • {label}: {value}")
        else:
            lines.append(f"  • {coverage}")

    if sch.get('eligibility'):
        lines.append(f"\n**✅ Eligibility:**")
        eligibility = sch['eligibility']
        if isinstance(eligibility, dict):
            for key, value in eligibility.items():
                label = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    lines.append(f"  • {label}:")
                    for k, v in value.items():
                        lines.append(f"    - {k}: {v}")
                elif isinstance(value, list):
                    lines.append(f"  • {label}:")
                    for item in value:
                        lines.append(f"    - {item}")
                else:
                    lines.append(f"  • {label}: {value}")
        else:
            lines.append(f"  • {eligibility}")

    if sch.get('required_documents'):
        lines.append(f"\n**📄 Required Documents:**")
        docs = sch['required_documents'] if isinstance(sch['required_documents'], list) else [sch['required_documents']]
        for doc in docs[:15]:
            lines.append(f"  • {doc}")
        if len(docs) > 15:
            lines.append(f"  • ... and {len(docs) - 15} more")

    if sch.get('apply_link'):
        lines.append(f"\n**🔗 Apply:** {sch['apply_link']}")

    if sch.get('official_website'):
        lines.append(f"\n**🌐 Website:** {sch['official_website']}")

    if sch.get('notes'):
        lines.append(f"\n**📌 Notes:** {sch['notes']}")

    # Fallback: show description if no other fields
    if sch.get('description') and len(lines) <= 2:
        lines.append(f"\n**📝 Description:** {sch['description']}")

    return '\n'.join(lines)


# ==============================================================
#   Response Builder
# ==============================================================

def get_response(user_query: str, matched_scholarships: list) -> str:
    """
    Build a formatted reply string based on search results.

    - If no results: show available scholarships list.
    - If exact match found: show full scholarship details.
    - If general query: show top 3 results with summary.

    Args:
        user_query:           The original user query.
        matched_scholarships: Output from search_scholarships().

    Returns:
        Formatted reply string (markdown-compatible).
    """
    # ── No results ───────────────────────────────────────────
    if not matched_scholarships:
        reply = f"❌ No scholarship found matching **'{user_query}'**.\n\n"
        if scholarships:
            reply += f"📚 **Available scholarships ({len(scholarships)} total):**\n"
            for s in scholarships[:10]:
                reply += f"  • {s.get('scholarship_name', 'Unknown')}\n"
            if len(scholarships) > 10:
                reply += f"  • ... and {len(scholarships) - 10} more\n"
            reply += "\n💡 **Try searching by:** scholarship name · country · study level · institution"
        else:
            reply += "📁 No scholarships are loaded yet. Please add .txt files to the **scholarships** folder."
        return reply

    # ── Exact / Specific match ────────────────────────────────
    query_lower = user_query.lower()
    specific = None
    for sch, score in matched_scholarships:
        sch_name = sch.get('scholarship_name', '').lower()
        if sch_name in query_lower or query_lower in sch_name:
            specific = sch
            break

    if specific:
        reply = f"**📚 Complete details: {specific.get('scholarship_name')}**\n\n"
        reply += format_scholarship_detail(specific)
        others = [s for s in matched_scholarships if s[0] != specific]
        if others:
            reply += f"\n\n---\n📌 **{len(others)} other related scholarships found.** Ask me about them!"
        return reply

    # ── General query: top 3 results ─────────────────────────
    top = matched_scholarships[:3]
    reply = f"🔍 **Found {len(matched_scholarships)} scholarship(s) matching '{user_query}'**\n\n"

    for i, (sch, score) in enumerate(top, 1):
        reply += f"**{i}. 🎓 {sch.get('scholarship_name', 'Scholarship')}**\n"
        if sch.get('study_in'):
            reply += f"   🌍 Country: {sch['study_in']}\n"
        if sch.get('institution'):
            reply += f"   🏛️ Institution: {sch['institution']}\n"
        if sch.get('level_of_study'):
            levels = ', '.join(sch['level_of_study']) if isinstance(sch['level_of_study'], list) else sch['level_of_study']
            reply += f"   📚 Level: {levels}\n"
        if sch.get('deadline'):
            reply += f"   ⏰ Deadline: {sch['deadline']}\n"
        reply += f"\n   💡 Ask: **\"Tell me about {sch.get('scholarship_name')}\"** for full details!\n\n"

    if len(matched_scholarships) > 3:
        reply += f"📌 ... and {len(matched_scholarships) - 3} more found.\n"

    return reply
