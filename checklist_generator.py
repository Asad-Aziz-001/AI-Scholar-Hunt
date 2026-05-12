import os
import re
import json

def load_all_scholarships_for_checklist():
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
                
                scholarship = parse_scholarship_documents(content, filename)
                
                if scholarship:
                    all_scholarships.append(scholarship)
                    
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return all_scholarships


def parse_scholarship_documents(content, filename):
    scholarship = {
        'name': filename.replace('.txt', '').replace('_', ' ').title(),
        'documents': [],
        'deadline': 'Not specified',
        'apply_link': '#'
    }
    
    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            if 'required_documents' in data:
                docs = data['required_documents']
                scholarship['documents'] = docs if isinstance(docs, list) else [docs]
            if 'deadline' in data:
                scholarship['deadline'] = data['deadline']
            if 'apply_link' in data:
                scholarship['apply_link'] = data['apply_link']
            return scholarship
    except:
        pass
    
    # Parse as text
    lines = content.split('\n')
    in_docs = False
    
    for line in lines:
        line_lower = line.lower().strip()
        
        if 'deadline:' in line_lower:
            parts = line.split(':', 1)
            if len(parts) > 1:
                scholarship['deadline'] = parts[1].strip()
        
        if 'apply_link:' in line_lower or 'apply link:' in line_lower:
            parts = line.split(':', 1)
            if len(parts) > 1:
                link = parts[1].strip()
                if link.startswith('http'):
                    scholarship['apply_link'] = link
        
        if 'required_documents' in line_lower or 'documents:' in line_lower:
            in_docs = True
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    val = parts[1].strip()
                    val = val.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
                    if ',' in val:
                        for d in val.split(','):
                            d = d.strip()
                            if d and len(d) > 2:
                                scholarship['documents'].append(d)
                    elif val and len(val) > 2:
                        scholarship['documents'].append(val)
            continue
        
        if in_docs and (line.startswith('-') or line.startswith('•') or line.startswith('*') or line[0].isdigit()):
            doc = line.lstrip('-•*0123456789. ').strip()
            if doc and len(doc) > 2 and not doc.lower().startswith('required'):
                scholarship['documents'].append(doc)
    
    if not scholarship['documents']:
        name_lower = scholarship['name'].lower()
        if 'phd' in name_lower or 'doctoral' in name_lower:
            scholarship['documents'] = [
                "Curriculum Vitae (CV) with publications",
                "Research proposal",
                "Writing sample",
                "PhD transcript",
                "Three letters of recommendation",
                "Cover letter"
            ]
        else:
            scholarship['documents'] = [
                "Academic transcripts",
                "Statement of Purpose (SOP)",
                "Letters of recommendation (2-3)",
                "Curriculum Vitae (CV)",
                "English proficiency test score",
                "Passport copy"
            ]
    
    return scholarship