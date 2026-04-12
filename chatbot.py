from flask import Flask, render_template, request, jsonify
import json
import os
import re

app = Flask(__name__)

# Global list to store all scholarships
scholarships = []

def load_scholarships():
    global scholarships        # ← yeh line ADD karo sabse pehle
    scholarships = []          # ab yeh global ko update karega
    folder = 'scholarships' # Folder containing scholarship .txt files
    
    # Check if scholarships folder exists
    if not os.path.exists(folder):
        print(f"❌ '{folder}' folder not found! Creating folder...")
        os.makedirs(folder)
        print(f"✅ Created '{folder}' folder. Please add scholarship .txt files.")
        return scholarships  # Return empty list

    # Iterate through all txt files in the folder
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            try:
                filepath = os.path.join(folder, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                    # Try to parse as JSON if content starts with {
                    if content.startswith('{'):
                        data = json.loads(content)
                    else:
                        # If not JSON, create basic structure from plain text
                        data = {
                            "scholarship_name": filename.replace('.txt', ''),
                            "description": content,
                            "_filename": filename
                        }
                    
                    # Add filename to data for reference
                    data['_filename'] = filename
                    scholarships.append(data)
                    print(f"✅ Loaded: {data.get('scholarship_name', filename)}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error in {filename}: {e}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")

    print(f"\n✅ Total {len(scholarships)} scholarships loaded successfully!\n")
    return scholarships  # Return the list

def normalize(text):
    """Normalize text for case-insensitive searching"""
    return re.sub(r'[^a-z0-9\s]', '', str(text).lower().strip())

def search_scholarships(query):
    """Search all scholarships based on user query and return scored results"""
    query_norm = normalize(query)
    query_words = query_norm.split()
    
    scored_results = []
    
    for sch in scholarships:
        score = 0
        
        # Check scholarship name (highest priority - 100 points)
        name = normalize(sch.get('scholarship_name', ''))
        if query_norm in name or name in query_norm:
            score += 100
        
        # Check country (50 points)
        country = normalize(sch.get('study_in', ''))
        if any(word in country for word in query_words):
            score += 50
        
        # Check institution (40 points)
        institution = normalize(sch.get('institution', ''))
        if any(word in institution for word in query_words):
            score += 40
        
        # Check level of study (30 points)
        level = json.dumps(sch.get('level_of_study', [])).lower()
        if any(word in level for word in query_words):
            score += 30
        
        # Check full text content (10 points per word match)
        full_text = json.dumps(sch, ensure_ascii=False).lower()
        for word in query_words:
            if len(word) > 2 and word in full_text:
                score += 10
        
        # Only include scholarships with a positive score
        if score > 0:
            scored_results.append((sch, score))
    
    # Sort by score in descending order (highest first)
    scored_results.sort(key=lambda x: x[1], reverse=True)
    return scored_results

def get_complete_scholarship_text(sch):
    """Convert complete scholarship data to formatted text for display"""
    lines = []
    
    # Scholarship name
    lines.append(f"**🎓 {sch.get('scholarship_name', 'Scholarship')}**\n")
    
    # Country
    if sch.get('study_in'):
        lines.append(f"**🌍 Country:** {sch['study_in']}")
    
    # Institution
    if sch.get('institution'):
        lines.append(f"**🏛️ Institution:** {sch['institution']}")
    
    # Level of study
    if sch.get('level_of_study'):
        levels = ', '.join(sch['level_of_study']) if isinstance(sch['level_of_study'], list) else sch['level_of_study']
        lines.append(f"**📚 Level:** {levels}")
    
    # Courses offered
    if sch.get('courses_offered'):
        lines.append(f"\n**📖 Courses Offered:**")
        courses = sch['courses_offered'] if isinstance(sch['courses_offered'], list) else [sch['courses_offered']]
        for course in courses[:15]:
            lines.append(f"  • {course}")
        if len(courses) > 15:
            lines.append(f"  • ... and {len(courses)-15} more")
    
    # Program duration
    if sch.get('program_period'):
        lines.append(f"\n**⏳ Duration:**")
        if isinstance(sch['program_period'], dict):
            for level, duration in sch['program_period'].items():
                lines.append(f"  • {level}: {duration}")
        else:
            lines.append(f"  • {sch['program_period']}")
    
    # Deadline
    if sch.get('deadline'):
        lines.append(f"\n**⏰ Deadline:** {sch['deadline']}")
    
    # Financial coverage
    if sch.get('coverage'):
        lines.append(f"\n**💰 Coverage:**")
        if isinstance(sch['coverage'], dict):
            for key, value in sch['coverage'].items():
                if isinstance(value, dict):
                    lines.append(f"  • {key.replace('_', ' ').title()}:")
                    for sub_k, sub_v in value.items():
                        lines.append(f"    - {sub_k}: {sub_v}")
                elif isinstance(value, list):
                    lines.append(f"  • {key.replace('_', ' ').title()}:")
                    for item in value:
                        lines.append(f"    - {item}")
                else:
                    lines.append(f"  • {key.replace('_', ' ').title()}: {value}")
        else:
            lines.append(f"  • {sch['coverage']}")
    
    # Eligibility criteria
    if sch.get('eligibility'):
        lines.append(f"\n**✅ Eligibility:**")
        if isinstance(sch['eligibility'], dict):
            for key, value in sch['eligibility'].items():
                if isinstance(value, dict):
                    lines.append(f"  • {key.replace('_', ' ').title()}:")
                    for sub_k, sub_v in value.items():
                        lines.append(f"    - {sub_k}: {sub_v}")
                elif isinstance(value, list):
                    lines.append(f"  • {key.replace('_', ' ').title()}:")
                    for item in value:
                        lines.append(f"    - {item}")
                else:
                    lines.append(f"  • {key.replace('_', ' ').title()}: {value}")
        else:
            lines.append(f"  • {sch['eligibility']}")
    
    # Required documents
    if sch.get('required_documents'):
        lines.append(f"\n**📄 Required Documents:**")
        docs = sch['required_documents'] if isinstance(sch['required_documents'], list) else [sch['required_documents']]
        for doc in docs[:15]:
            lines.append(f"  • {doc}")
        if len(docs) > 15:
            lines.append(f"  • ... and {len(docs)-15} more")
    
    # Application link
    if sch.get('apply_link'):
        lines.append(f"\n**🔗 Apply:** {sch['apply_link']}")
    
    # Official website
    if sch.get('official_website'):
        lines.append(f"\n**🌐 Website:** {sch['official_website']}")
    
    # Additional notes
    if sch.get('notes'):
        lines.append(f"\n**📌 Notes:** {sch['notes']}")
    
    # Description (fallback field)
    if sch.get('description') and not any(lines[1:]):
        lines.append(f"\n**📝 Description:** {sch['description']}")
    
    return '\n'.join(lines)

def get_response(user_query, matched_scholarships):
    """Generate response using search results"""
    
    if not matched_scholarships:
        # No matches found - show available scholarships
        all_names = [sch.get('scholarship_name', 'Unknown') for sch in scholarships[:15]]
        reply = f"❌ No scholarship found matching '{user_query}' in my database.\n\n"
        
        if scholarships:
            reply += f"📚 **I have {len(scholarships)} scholarships available:**\n"
            for name in all_names[:10]:
                reply += f"  • {name}\n"
            if len(scholarships) > 10:
                reply += f"  • ... and {len(scholarships)-10} more\n"
            reply += "\n💡 **Try searching by:**\n• Scholarship name\n• Country name\n• Study level\n• Institution name"
        else:
            reply += "📁 **No scholarships loaded yet!**\n\n"
            reply += "Please add scholarship data files to the 'scholarships' folder.\n"
            reply += "Each file should be a .txt file with scholarship information."
        
        return reply
    
    # Check if user is asking about a specific scholarship by name
    query_lower = user_query.lower()
    specific_scholarship = None
    
    # Try to find exact match by name
    for sch, score in matched_scholarships:
        sch_name = sch.get('scholarship_name', '').lower()
        if sch_name in query_lower or query_lower in sch_name:
            specific_scholarship = sch
            break
    
    # If asking about specific scholarship, show complete details
    if specific_scholarship:
        reply = f"**📚 Complete details for: {specific_scholarship.get('scholarship_name')}**\n\n"
        reply += get_complete_scholarship_text(specific_scholarship)
        
        # Show other related scholarships
        other_matches = [s for s in matched_scholarships if s[0] != specific_scholarship]
        if other_matches:
            reply += f"\n\n---\n📌 **Found {len(other_matches)} other related scholarships.** Ask me about them!"
        
        return reply
    
    # General query - show top matches with summaries
    top_matches = matched_scholarships[:3]
    
    reply = f"🔍 **Found {len(matched_scholarships)} scholarship(s) matching '{user_query}'**\n\n"
    
    for i, (sch, score) in enumerate(top_matches, 1):
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
        
        reply += f"\n   💡 **Ask me:** \"Tell me more about {sch.get('scholarship_name')}\" for complete details!\n\n"
    
    if len(matched_scholarships) > 3:
        reply += f"📌 ... and {len(matched_scholarships)-3} more scholarships found.\n"
    
    return reply


if __name__ == '__main__':
    load_scholarships()
    
    print("\n" + "="*50)
    print("🎓 AI SCHOLAR HUNT")
    print("="*50)
    print(f"📚 Total scholarships loaded: {len(scholarships)}")
    print("🌐 Server running at: http://127.0.0.1:5000")
    print("💡 Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)