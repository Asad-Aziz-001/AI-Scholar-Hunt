import os
import re
import json

def load_all_scholarships_for_calendar():
    """Load all scholarships with deadline information"""
    scholarships_dir = "scholarships"
    all_scholarships = []
    
    if not os.path.exists(scholarships_dir):
        return all_scholarships
    
    for filename in os.listdir(scholarships_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(scholarships_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    continue
                
                scholarship = parse_scholarship_deadline(content, filename)
                
                if scholarship:
                    all_scholarships.append(scholarship)
                    print(f"✅ Loaded: {scholarship['name'][:50]} - {scholarship['deadline'][:30]}")
                    
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    print(f"📅 Total scholarships with deadlines: {len(all_scholarships)}")
    return all_scholarships


def parse_scholarship_deadline(content, filename):
    """Parse scholarship file to extract deadline and country info"""
    
    scholarship = {
        'name': filename.replace('.txt', '').replace('_', ' ').title(),
        'deadline': 'Not specified',
        'country': 'Not specified',
        'apply_link': '#'
    }
    
    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            if 'deadline' in data:
                scholarship['deadline'] = data['deadline']
            if 'study_in' in data:
                scholarship['country'] = data['study_in']
            if 'apply_link' in data:
                scholarship['apply_link'] = data['apply_link']
            return scholarship
    except:
        pass
    
    # Parse as text file
    lines = content.split('\n')
    
    for line in lines[:50]:
        line_lower = line.lower().strip()
        
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip().lower()
            value = parts[1].strip()
            
            if key in ['deadline', 'application_deadline']:
                scholarship['deadline'] = value
            elif key in ['country', 'study_in']:
                scholarship['country'] = value
            elif key in ['apply_link', 'link', 'url']:
                if value.startswith('http'):
                    scholarship['apply_link'] = value
    
    return scholarship