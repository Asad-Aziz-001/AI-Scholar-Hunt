import json
import os
from datetime import datetime, timedelta

def load_all_scholarships_timeline():
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
                            'country': scholarship_data.get('study_in', 'Not specified')
                        })
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return all_scholarships

def generate_timeline(scholarship):
    """Generate application timeline for a scholarship"""
    
    timeline_phases = [
        {
            'phase': 1,
            'name': 'Research & Shortlisting',
            'duration': '2-3 weeks',
            'tasks': [
                'Research universities and programs',
                'Check eligibility criteria carefully',
                'Shortlist 3-5 scholarships',
                'Note all deadlines in calendar',
                'Create a spreadsheet for tracking'
            ],
            'icon': '🔍',
            'color': '#3b82f6'
        },
        {
            'phase': 2,
            'name': 'Document Preparation',
            'duration': '3-4 weeks',
            'tasks': [
                'Request transcripts from university',
                'Contact professors for LORs (give them 2 weeks)',
                'Write and revise Statement of Purpose',
                'Prepare CV/Resume',
                'Get documents attested from HEC',
                'Take IELTS/TOEFL test'
            ],
            'icon': '📝',
            'color': '#8b5cf6'
        },
        {
            'phase': 3,
            'name': 'Application Submission',
            'duration': '1-2 weeks',
            'tasks': [
                'Fill online application form carefully',
                'Upload all required documents',
                'Pay application fee (if any)',
                'Review application multiple times',
                'Submit before deadline',
                'Save confirmation email'
            ],
            'icon': '📤',
            'color': '#10b981'
        },
        {
            'phase': 4,
            'name': 'Follow-up & Interview',
            'duration': '4-8 weeks',
            'tasks': [
                'Wait for shortlist results',
                'Prepare for interview if shortlisted',
                'Practice common interview questions',
                'Send follow-up emails if needed',
                'Check email regularly'
            ],
            'icon': '🎤',
            'color': '#f59e0b'
        },
        {
            'phase': 5,
            'name': 'Visa & Travel Preparation',
            'duration': '6-8 weeks',
            'tasks': [
                'Apply for passport (if not available)',
                'Gather visa documents',
                'Fill visa application form',
                'Schedule visa interview',
                'Book medical appointment',
                'Arrange accommodation',
                'Book flight tickets'
            ],
            'icon': '✈️',
            'color': '#ef4444'
        }
    ]
    
    # Calculate urgency based on deadline
    urgency_level = "Normal"
    urgency_color = "#10b981"
    
    deadline_text = scholarship.get('deadline', '').lower()
    if 'nov' in deadline_text or 'dec' in deadline_text or 'jan' in deadline_text:
        urgency_level = "⚠️ Urgent - Apply Soon!"
        urgency_color = "#ef4444"
    elif 'mar' in deadline_text or 'apr' in deadline_text:
        urgency_level = "🟡 Moderate - Good Time to Apply"
        urgency_color = "#f59e0b"
    else:
        urgency_level = "🟢 Flexible - Plan Properly"
        urgency_color = "#10b981"
    
    return {
        'timeline_phases': timeline_phases,
        'urgency_level': urgency_level,
        'urgency_color': urgency_color,
        'scholarship_name': scholarship.get('name', 'Selected Scholarship'),
        'deadline': scholarship.get('deadline', 'Not specified'),
        'country': scholarship.get('country', 'Not specified')
    }