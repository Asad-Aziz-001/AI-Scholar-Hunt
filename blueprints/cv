# ==================================================
#              CV Builder Blueprint
#   Handles CV generation in PDF and DOCX formats
#   for different countries and template styles
# ==================================================

from flask import Blueprint, render_template, request, send_file, jsonify
from docx import Document
from docx.shared import Inches, Mm, Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import base64
import os
from PIL import Image
import tempfile

# ==================================================
#   Blueprint Definition
#   URL prefix: /cv-builder
#   e.g. /cv-builder/, /cv-builder/cv_form/usa
# ==================================================
cv_bp = Blueprint('cv', __name__, url_prefix='/cv-builder')

# ==================================================
#   Template Configurations
#   4 types based on country requirements
# ==================================================
TEMPLATE_CONFIGS = {
    'ats': {
        'name': 'ATS-Friendly',
        'display_name': 'USA, Canada, Australia, Ireland',
        'requires_photo': False,
        'requires_personal_details': False,
        'max_pages': 2,
        'description': 'No photo needed, ATS-optimized, 1-2 pages'
    },
    'photo_personal': {
        'name': 'Photo + Personal Details',
        'display_name': 'Germany, Austria, Turkey',
        'requires_photo': True,
        'requires_personal_details': True,
        'max_pages': 3,
        'description': 'Professional photo required, include DOB, nationality, marital status'
    },
    'passport': {
        'name': 'Passport/Visa Details',
        'display_name': 'China, UAE, Japan',
        'requires_photo': True,
        'requires_personal_details': True,
        'max_pages': 2,
        'description': 'Passport photo and number required, visa status for UAE'
    },
    'europass': {
        'name': 'Europass Style',
        'display_name': 'Belgium, Denmark, Italy, France',
        'requires_photo': False,
        'requires_personal_details': False,
        'max_pages': 2,
        'description': 'Languages very important, European standard format'
    }
}

# ==================================================
#   Country to Template Mapping
# ==================================================
COUNTRY_TEMPLATE = {
    'usa':       {'name': 'USA',       'flag': '🇺🇸', 'template': 'ats',           'group': 'A'},
    'canada':    {'name': 'Canada',    'flag': '🇨🇦', 'template': 'ats',           'group': 'A'},
    'australia': {'name': 'Australia', 'flag': '🇦🇺', 'template': 'ats',           'group': 'A'},
    'ireland':   {'name': 'Ireland',   'flag': '🇮🇪', 'template': 'ats',           'group': 'A'},
    'germany':   {'name': 'Germany',   'flag': '🇩🇪', 'template': 'photo_personal','group': 'B'},
    'austria':   {'name': 'Austria',   'flag': '🇦🇹', 'template': 'photo_personal','group': 'B'},
    'turkey':    {'name': 'Turkey',    'flag': '🇹🇷', 'template': 'photo_personal','group': 'B'},
    'china':     {'name': 'China',     'flag': '🇨🇳', 'template': 'passport',      'group': 'C'},
    'uae':       {'name': 'UAE',       'flag': '🇦🇪', 'template': 'passport',      'group': 'C'},
    'japan':     {'name': 'Japan',     'flag': '🇯🇵', 'template': 'passport',      'group': 'C'},
    'belgium':   {'name': 'Belgium',   'flag': '🇧🇪', 'template': 'europass',      'group': 'D'},
    'denmark':   {'name': 'Denmark',   'flag': '🇩🇰', 'template': 'europass',      'group': 'D'},
    'italy':     {'name': 'Italy',     'flag': '🇮🇹', 'template': 'europass',      'group': 'D'},
    'france':    {'name': 'France',    'flag': '🇫🇷', 'template': 'europass',      'group': 'D'},
}

# ==================================================
#   Routes
# ==================================================

@cv_bp.route('/')
def cv_index():
    """CV Builder home — country selection page"""
    return render_template('cv-builder.html',
                           countries=COUNTRY_TEMPLATE,
                           template_configs=TEMPLATE_CONFIGS)


@cv_bp.route('/cv_form/<country_id>')
def cv_form(country_id):
    """CV Form page for selected country"""
    if country_id not in COUNTRY_TEMPLATE:
        return "Country not found", 404

    country = COUNTRY_TEMPLATE[country_id]
    template_config = TEMPLATE_CONFIGS[country['template']]

    return render_template('cv_form.html',
                           country=country,
                           template_config=template_config,
                           template_type=country['template'])


@cv_bp.route('/generate_cv', methods=['POST'])
def generate_cv():
    """Generate CV in PDF or DOCX format"""
    data = request.json
    country_id   = data.get('country_id')
    template_type = data.get('template_type')
    cv_data      = data.get('cv_data')
    format_type  = data.get('format', 'pdf')
    photo_data   = data.get('photo_data', None)  # Base64 encoded photo

    if format_type == 'pdf':
        return generate_pdf(template_type, cv_data, country_id, photo_data)
    else:
        return generate_doc(template_type, cv_data, country_id, photo_data)


# ==================================================
#   Helper Functions — Image Resizing
# ==================================================

def resize_image_for_pdf(image_data, max_width=80, max_height=100):
    """Resize and convert image for PDF embedding"""
    try:
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes))

        # Convert RGBA → RGB (PDF doesn't support transparency)
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img

        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return output
    except Exception as e:
        print(f"❌ Error resizing image for PDF: {e}")
        return None


def resize_image_for_doc(image_data, width_inches=1.2, height_inches=1.5):
    """Resize and convert image for DOCX embedding"""
    try:
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(image_bytes))

        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img

        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return output
    except Exception as e:
        print(f"❌ Error resizing image for DOC: {e}")
        return None


# ==================================================
#   PDF Generation
# ==================================================

def generate_pdf(template_type, cv_data, country_id, photo_data):
    """Generate a PDF CV using ReportLab"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    config = TEMPLATE_CONFIGS.get(template_type, {})

    y = 750  # Start from top

    # --- Name ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, cv_data.get('full_name', 'NAME NOT PROVIDED'))

    # --- Contact ---
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50,  y, f"Email: {cv_data.get('email', '')}")
    c.drawString(250, y, f"Phone: {cv_data.get('phone', '')}")

    # --- Photo (if required) ---
    if config.get('requires_photo') and photo_data:
        try:
            img_bytes = resize_image_for_pdf(photo_data)
            if img_bytes:
                c.drawImage(ImageReader(img_bytes), 450, 700, width=80, height=100, preserveAspectRatio=True)
        except Exception as e:
            print(f"❌ PDF photo error: {e}")
            c.drawString(450, 745, "[Photo error]")
    elif config.get('requires_photo'):
        c.drawString(450, 745, "[Photo not provided]")

    # --- Personal Details ---
    if config.get('requires_personal_details'):
        fields = ['dob', 'nationality', 'marital_status', 'passport_no', 'visa_status']
        labels = ['Date of Birth', 'Nationality', 'Marital Status', 'Passport No', 'Visa Status']
        if any(cv_data.get(f) for f in fields):
            y -= 50
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "PERSONAL DETAILS")
            c.line(50, y - 5, 500, y - 5)
            y -= 25
            c.setFont("Helvetica", 10)
            for field, label in zip(fields, labels):
                if cv_data.get(field):
                    c.drawString(50, y, f"{label}: {cv_data[field]}")
                    y -= 20

    # --- Education ---
    if cv_data.get('degree') or cv_data.get('university'):
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "EDUCATION")
        c.line(50, y - 5, 500, y - 5)
        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(50,  y, cv_data.get('degree', ''))
        c.drawString(250, y, cv_data.get('university', ''))
        if cv_data.get('gpa') or cv_data.get('graduation_year'):
            y -= 20
            c.drawString(50,  y, f"GPA: {cv_data.get('gpa', '')}")
            c.drawString(250, y, f"Expected: {cv_data.get('graduation_year', '')}")

    # --- Projects ---
    if cv_data.get('projects'):
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "PROJECTS")
        c.line(50, y - 5, 500, y - 5)
        y -= 25
        c.setFont("Helvetica", 10)
        for line in cv_data['projects'].split('\n')[:4]:
            if line.strip():
                c.drawString(50, y, f"• {line.lstrip('•-* ').strip()[:70]}")
                y -= 20
                if y < 100:
                    c.showPage(); y = 750

    # --- Skills ---
    if cv_data.get('skills') and y > 150:
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "SKILLS")
        c.line(50, y - 5, 500, y - 5)
        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(50, y, cv_data['skills'][:100])

    # --- Languages ---
    if cv_data.get('languages') and y > 120:
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "LANGUAGES")
        c.line(50, y - 5, 500, y - 5)
        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(50, y, cv_data['languages'][:100])

    # --- Work Experience ---
    if cv_data.get('work_experience') and y > 150:
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "WORK EXPERIENCE")
        c.line(50, y - 5, 500, y - 5)
        y -= 25
        c.setFont("Helvetica", 10)
        for line in cv_data['work_experience'].split('\n')[:3]:
            if line.strip():
                c.drawString(50, y, f"• {line[:70]}")
                y -= 20

    # --- Certifications ---
    if cv_data.get('certifications') and y > 120:
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "CERTIFICATIONS")
        c.line(50, y - 5, 500, y - 5)
        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(50, y, cv_data['certifications'][:100])

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"CV_{country_id}_{cv_data.get('full_name', 'scholar')}.pdf",
                     mimetype='application/pdf')


# ==================================================
#   DOCX Generation
# ==================================================

def generate_doc(template_type, cv_data, country_id, photo_data):
    """Generate a DOCX CV using python-docx"""
    doc = Document()
    config = TEMPLATE_CONFIGS.get(template_type, {})

    # --- Header with Photo (if required) ---
    if config.get('requires_photo'):
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False
        table.columns[0].width = Cm(12)
        table.columns[1].width = Cm(4)

        left = table.cell(0, 0)
        name_para = left.paragraphs[0]
        run = name_para.add_run(cv_data.get('full_name', 'Curriculum Vitae'))
        run.bold = True
        run.font.size = Pt(16)

        contact = left.add_paragraph()
        contact.add_run(f"Email: {cv_data.get('email', '')} | Phone: {cv_data.get('phone', '')}")

        right = table.cell(0, 1)
        if photo_data:
            try:
                img_bytes = resize_image_for_doc(photo_data)
                if img_bytes:
                    photo_para = right.add_paragraph()
                    photo_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    photo_para.add_run().add_picture(img_bytes, width=Cm(3.5), height=Cm(4.5))
            except Exception as e:
                print(f"❌ DOC photo error: {e}")
                right.add_paragraph("[Photo error]")
        doc.add_paragraph()
    else:
        # Standard header without photo
        doc.add_heading(cv_data.get('full_name', 'Curriculum Vitae'), 0)
        doc.add_paragraph(f"Email: {cv_data.get('email', '')} | Phone: {cv_data.get('phone', '')}")
        if cv_data.get('linkedin'): doc.add_paragraph(f"LinkedIn: {cv_data['linkedin']}")
        if cv_data.get('github'):   doc.add_paragraph(f"GitHub: {cv_data['github']}")
        doc.add_paragraph()

    # --- Personal Details ---
    if config.get('requires_personal_details'):
        fields = {
            'dob': 'Date of Birth', 'nationality': 'Nationality',
            'marital_status': 'Marital Status', 'passport_no': 'Passport Number',
            'visa_status': 'Visa Status'
        }
        details = [f"{label}: {cv_data[key]}" for key, label in fields.items() if cv_data.get(key)]
        if details:
            doc.add_heading('PERSONAL INFORMATION', level=1)
            for d in details:
                doc.add_paragraph(d)
            doc.add_paragraph()

    # --- Education ---
    if cv_data.get('degree') or cv_data.get('university'):
        doc.add_heading('EDUCATION', level=1)
        doc.add_paragraph(f"{cv_data.get('degree', '')} - {cv_data.get('university', '')}")
        if cv_data.get('gpa') or cv_data.get('graduation_year'):
            doc.add_paragraph(f"GPA: {cv_data.get('gpa', 'N/A')} | Expected: {cv_data.get('graduation_year', 'N/A')}")
        if cv_data.get('coursework'):
            doc.add_paragraph(f"Coursework: {cv_data['coursework']}")
        doc.add_paragraph()

    # --- Work Experience ---
    if cv_data.get('work_experience'):
        doc.add_heading('WORK EXPERIENCE', level=1)
        for line in cv_data['work_experience'].split('\n'):
            if line.strip():
                doc.add_paragraph(f"• {line}", style='List Bullet')
        doc.add_paragraph()

    # --- Projects ---
    if cv_data.get('projects'):
        doc.add_heading('PROJECTS', level=1)
        for line in cv_data['projects'].split('\n'):
            if line.strip():
                doc.add_paragraph(f"• {line.lstrip('•-* ').strip()}", style='List Bullet')
        doc.add_paragraph()

    # --- Skills ---
    if cv_data.get('skills'):
        doc.add_heading('SKILLS', level=1)
        doc.add_paragraph(cv_data['skills'])
        doc.add_paragraph()

    # --- Languages ---
    if cv_data.get('languages'):
        doc.add_heading('LANGUAGES', level=1)
        doc.add_paragraph(cv_data['languages'])
        doc.add_paragraph()

    # --- Certifications ---
    if cv_data.get('certifications'):
        doc.add_heading('CERTIFICATIONS', level=1)
        doc.add_paragraph(cv_data['certifications'])

    # --- Publications ---
    if cv_data.get('publications'):
        doc.add_heading('PUBLICATIONS', level=1)
        doc.add_paragraph(cv_data['publications'])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"CV_{country_id}_{cv_data.get('full_name', 'scholar')}.docx",
                     mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
