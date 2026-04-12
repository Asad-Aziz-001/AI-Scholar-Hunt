china_template = {
    'name': 'China',
    'format': 'Chinese Scholarship CV (CSC Format)',
    'max_pages': 2,
    'requires_photo': True,
    'requires_personal_details': True,
    'sections': [
        {
            'name': 'personal',
            'label': 'Personal Information',
            'fields': [
                {'name': 'full_name', 'label': 'Full Name (as in passport)', 'type': 'text', 'required': True},
                {'name': 'photo', 'label': 'Passport Photo (white background)', 'type': 'file', 'required': True},
                {'name': 'dob', 'label': 'Date of Birth', 'type': 'date', 'required': True},
                {'name': 'nationality', 'label': 'Nationality', 'type': 'text', 'required': True},
                {'name': 'passport_no', 'label': 'Passport Number', 'type': 'text', 'required': True},
                {'name': 'email', 'label': 'Email', 'type': 'email', 'required': True},
                {'name': 'phone', 'label': 'Phone (with country code)', 'type': 'tel', 'required': True}
            ]
        },
        {
            'name': 'education',
            'label': 'Education Background',
            'fields': [
                {'name': 'degree', 'label': 'Degree', 'type': 'text', 'required': True},
                {'name': 'university', 'label': 'University', 'type': 'text', 'required': True},
                {'name': 'gpa', 'label': 'GPA or Percentage', 'type': 'text', 'required': True},
                {'name': 'graduation_year', 'label': 'Graduation Year', 'type': 'text', 'required': True}
            ]
        },
        {
            'name': 'publications',
            'label': 'Publications & Research',
            'fields': [
                {'name': 'publications', 'label': 'Research Papers / Publications', 'type': 'textarea', 'required': False}
            ]
        },
        {
            'name': 'chinese_language',
            'label': 'Chinese Proficiency',
            'fields': [
                {'name': 'chinese_level', 'label': 'HSK Level (if any)', 'type': 'text', 'required': False},
                {'name': 'english_level', 'label': 'English Proficiency (IELTS/TOEFL)', 'type': 'text', 'required': True}
            ]
        }
    ]
}
