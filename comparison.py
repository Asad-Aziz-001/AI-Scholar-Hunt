import os
import json
from flask import jsonify

def load_all_scholarships():
    """Load all scholarship data from JSON files"""
    scholarships_dir = "scholarships"
    all_scholarships = {}
    
    if not os.path.exists(scholarships_dir):
        print(f"Folder '{scholarships_dir}' not found!")
        return all_scholarships
    
    for filename in os.listdir(scholarships_dir):
        if filename.endswith('.json') or filename.endswith('.txt'):
            file_path = os.path.join(scholarships_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    scholarship_data = json.loads(content)
                    
                    if 'scholarship_name' in scholarship_data:
                        scholarship_name = scholarship_data['scholarship_name']
                        all_scholarships[scholarship_name] = scholarship_data
                    else:
                        print(f"Warning: 'scholarship_name' not found in {filename}")
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in {filename}: {e}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    print(f"✅ Loaded {len(all_scholarships)} scholarships")
    return all_scholarships

def get_scholarship_details(scholarship_name):
    """Get details of a specific scholarship"""
    all_scholarships = load_all_scholarships()
    
    for name, data in all_scholarships.items():
        if name.lower() == scholarship_name.lower():
            return data
    
    return None

def get_all_scholarship_names():
    """Get sorted list of all scholarship names"""
    all_scholarships = load_all_scholarships()
    return sorted(list(all_scholarships.keys()))