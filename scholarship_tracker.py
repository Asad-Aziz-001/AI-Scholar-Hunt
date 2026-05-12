import json
import os

def load_all_scholarships_tracker():
    """Load all scholarship names for dropdown"""
    scholarships_dir = "scholarships"
    all_scholarships = []
    
    if not os.path.exists(scholarships_dir):
        return all_scholarships
    
    for filename in os.listdir(scholarships_dir):
        if filename.endswith('.json') or filename.endswith('.txt'):
            file_path = os.path.join(scholarships_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    scholarship_data = json.loads(content)
                    
                    if 'scholarship_name' in scholarship_data:
                        all_scholarships.append({
                            'name': scholarship_data['scholarship_name'],
                            'deadline': scholarship_data.get('deadline', 'Not specified'),
                            'country': scholarship_data.get('study_in', 'Not specified'),
                            'apply_link': scholarship_data.get('apply_link', '#')
                        })
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return all_scholarships