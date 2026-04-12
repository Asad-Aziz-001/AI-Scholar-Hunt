uae_template = {
    'name': 'UAE',
    'format': 'UAE Standard CV',
    'max_pages': 2,
    'requires_photo': False,
    'requires_personal_details': True,
    'sections': [
        {
            'name': 'personal',
            'label': 'Personal Information',
            'fields': [
                {'name': 'full_name', 'label': 'Full Name', 'type': 'text', 'required': True},
                {'name': 'nationality', 'label': 'Nationality', 'type': 'text', 'required': True},
                {'name': 'visa_status', 'label': 'Visa Status (if in UAE)', 'type': 'text', 'required': False},
                {'name': 'email', 'label': 'Email', 'type': 'email', 'required': True},
                {'name': 'phone', 'label': 'Phone (with country code)', 'type': 'tel', 'required': True}
            ]
        },
        {
            'name': 'education',
            'label': 'Education',
            'fields': [
                {'name': 'degree', 'label': 'Degree', 'type': 'text', 'required': True},
                {'name': 'university', 'label': 'University', 'type': 'text', 'required': True},
                {'name': 'gpa', 'label': 'GPA', 'type': 'text', 'required': True}
            ]
        },
        {
            'name': 'experience',
            'label': 'Work/Internship Experience',
            'fields': [
                {'name': 'experience', 'label': 'Experience Details', 'type': 'textarea', 'required': True}
            ]
        }
    ]
}