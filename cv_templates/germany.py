germany_template = {
    'name': 'Germany',
    'format': 'German CV (Lebenslauf)',
    'max_pages': 3,
    'requires_photo': True,
    'requires_personal_details': True,
    'sections': [
        {
            'name': 'personal',
            'label': 'Personal Information (required in Germany)',
            'fields': [
                {'name': 'full_name', 'label': 'Full Name', 'type': 'text', 'required': True},
                {'name': 'photo', 'label': 'Passport Size Photo (upload)', 'type': 'file', 'required': True},
                {'name': 'dob', 'label': 'Date of Birth (DD/MM/YYYY)', 'type': 'date', 'required': True},
                {'name': 'nationality', 'label': 'Nationality', 'type': 'text', 'required': True},
                {'name': 'marital_status', 'label': 'Marital Status', 'type': 'text', 'required': True},
                {'name': 'email', 'label': 'Email', 'type': 'email', 'required': True},
                {'name': 'phone', 'label': 'Phone', 'type': 'tel', 'required': True},
                {'name': 'address', 'label': 'Address in Germany (if any)', 'type': 'text', 'required': False}
            ]
        },
        {
            'name': 'education',
            'label': 'Academic Background',
            'fields': [
                {'name': 'degree', 'label': 'Degree', 'type': 'text', 'required': True},
                {'name': 'university', 'label': 'University', 'type': 'text', 'required': True},
                {'name': 'duration', 'label': 'Duration (MM/YYYY - MM/YYYY)', 'type': 'text', 'required': True},
                {'name': 'gpa', 'label': 'Grade (German scale 1.0-5.0)', 'type': 'text', 'required': False}
            ]
        },
        {
            'name': 'work_experience',
            'label': 'Work Experience (Praktika/Werkstudent)',
            'fields': [
                {'name': 'work', 'label': 'Work Experience', 'type': 'textarea', 'required': False}
            ]
        },
        {
            'name': 'skills',
            'label': 'Skills & Certifications',
            'fields': [
                {'name': 'skills', 'label': 'Technical Skills', 'type': 'textarea', 'required': True},
                {'name': 'languages', 'label': 'Languages (German required for many scholarships)', 'type': 'textarea', 'required': True}
            ]
        }
    ]
}