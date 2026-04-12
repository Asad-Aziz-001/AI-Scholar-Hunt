usa_template = {
    'name': 'United States',
    'format': 'ATS-Friendly Academic CV',
    'max_pages': 2,
    'requires_photo': False,
    'requires_personal_details': False,
    'sections': [
        {
            'name': 'contact',
            'label': 'Contact Information',
            'fields': [
                {'name': 'full_name', 'label': 'Full Name', 'type': 'text', 'required': True},
                {'name': 'email', 'label': 'Email', 'type': 'email', 'required': True},
                {'name': 'phone', 'label': 'Phone (with country code)', 'type': 'tel', 'required': True},
                {'name': 'linkedin', 'label': 'LinkedIn URL', 'type': 'url', 'required': False},
                {'name': 'github', 'label': 'GitHub URL', 'type': 'url', 'required': False}
            ]
        },
        {
            'name': 'education',
            'label': 'Education',
            'fields': [
                {'name': 'degree', 'label': 'Degree (e.g., BS Artificial Intelligence)', 'type': 'text', 'required': True},
                {'name': 'university', 'label': 'University Name', 'type': 'text', 'required': True},
                {'name': 'gpa', 'label': 'GPA (out of 4.0)', 'type': 'text', 'required': True},
                {'name': 'graduation_year', 'label': 'Expected Graduation Year', 'type': 'text', 'required': True},
                {'name': 'coursework', 'label': 'Relevant Coursework (comma separated)', 'type': 'textarea', 'required': False}
            ]
        },
        {
            'name': 'research',
            'label': 'Research Experience',
            'fields': [
                {'name': 'research', 'label': 'Research Experience (describe projects, publications)', 'type': 'textarea', 'required': True}
            ]
        },
        {
            'name': 'projects',
            'label': 'Projects',
            'fields': [
                {'name': 'projects', 'label': 'Projects (one per line)', 'type': 'textarea', 'required': True}
            ]
        },
        {
            'name': 'skills',
            'label': 'Skills',
            'fields': [
                {'name': 'skills', 'label': 'Technical Skills (Python, ML, DL, etc.)', 'type': 'textarea', 'required': True}
            ]
        },
        {
            'name': 'publications',
            'label': 'Publications (if any)',
            'fields': [
                {'name': 'publications', 'label': 'Publications', 'type': 'textarea', 'required': False}
            ]
        },
        {
            'name': 'certifications',
            'label': 'Certifications',
            'fields': [
                {'name': 'certifications', 'label': 'Certifications (one per line)', 'type': 'textarea', 'required': False}
            ]
        }
    ]
}