import json
import os

def load_all_scholarships_cost():
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
                            'country': scholarship_data.get('study_in', 'Not specified'),
                            'coverage': scholarship_data.get('coverage', {})
                        })
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return all_scholarships

def calculate_application_cost(scholarship):
    """Calculate estimated cost for scholarship application"""
    
    # Base costs in PKR
    costs = {
        'ielts_toefl': 85000,      # IELTS/TOEFL fee
        'transcript_attestation': 5000,  # HEC attestation
        'courier_charges': 8000,    # Documents courier
        'application_fee': 0,       # Will be determined
        'visa_processing': 25000,    # Visa fee
        'medical_test': 5000,       # Medical examination
        'bank_statement': 2000,     # Bank statement processing
        'notary_charges': 3000,     # Document notarization
    }
    
    # Adjust based on country
    country = scholarship.get('country', '').lower()
    if 'germany' in country:
        costs['visa_processing'] = 75000  # Germany visa is expensive
        costs['application_fee'] = 0       # DAAD usually free
    elif 'usa' in country or 'united states' in country:
        costs['application_fee'] = 10000   # $60 approx
        costs['visa_processing'] = 18500   # $160 approx
    elif 'uk' in country or 'united kingdom' in country:
        costs['application_fee'] = 15000   # £50 approx
        costs['visa_processing'] = 35000   # £100 approx
    elif 'canada' in country:
        costs['application_fee'] = 12000   # CAD 100 approx
        costs['visa_processing'] = 15000   # CAD 150 approx
    elif 'uae' in country or 'dubai' in country:
        costs['application_fee'] = 5000
        costs['visa_processing'] = 12000
    elif 'china' in country:
        costs['application_fee'] = 8000
        costs['visa_processing'] = 10000
    else:
        costs['application_fee'] = 5000
        costs['visa_processing'] = 20000
    
    # Adjust based on scholarship coverage
    coverage = scholarship.get('coverage', {})
    if coverage.get('tuition'):
        tuition_text = coverage.get('tuition', '').lower()
        if 'full' in tuition_text:
            costs['application_fee'] = 0  # Full scholarship usually waives fee
    
    # Calculate total
    total = sum(costs.values())
    
    # Prepare breakdown
    breakdown = [
        {'item': 'IELTS/TOEFL Test Fee', 'cost': costs['ielts_toefl'], 'icon': '📝', 'tip': 'Official English proficiency test'},
        {'item': 'Transcript Attestation (HEC)', 'cost': costs['transcript_attestation'], 'icon': '📜', 'tip': 'HEC attestation for documents'},
        {'item': 'International Courier', 'cost': costs['courier_charges'], 'icon': '📦', 'tip': 'Sending documents to university'},
        {'item': 'Application Fee', 'cost': costs['application_fee'], 'icon': '💰', 'tip': 'Paid directly to university'},
        {'item': 'Visa Processing Fee', 'cost': costs['visa_processing'], 'icon': '🛂', 'tip': 'Student visa application fee'},
        {'item': 'Medical Examination', 'cost': costs['medical_test'], 'icon': '🏥', 'tip': 'Required for visa'},
        {'item': 'Bank Statement Processing', 'cost': costs['bank_statement'], 'icon': '🏦', 'tip': 'Bank letter for proof of funds'},
        {'item': 'Document Notary Charges', 'cost': costs['notary_charges'], 'icon': '✍️', 'tip': 'Notarization of documents'}
    ]
    
    return {
        'total': total,
        'total_usd': round(total / 280, 2),  # Approx USD conversion
        'breakdown': breakdown,
        'country': country,
        'scholarship_name': scholarship.get('name', 'Selected Scholarship')
    }

def get_cost_saving_tips(scholarship):
    """Generate cost-saving tips based on scholarship"""
    tips = []
    country = scholarship.get('country', '').lower()
    coverage = scholarship.get('coverage', {})
    
    if 'full' in str(coverage.get('tuition', '')).lower():
        tips.append("🎉 Full tuition scholarship detected! You save 100% on tuition fees.")
    
    if 'germany' in country:
        tips.append("💡 Germany has low living costs. You can survive on 850-1000€ per month.")
    
    if 'usa' in country:
        tips.append("💡 Apply for multiple scholarships simultaneously to increase chances.")
    
    tips.append("📝 Prepare documents in advance to avoid urgent courier charges (saves 3000-5000 PKR)")
    tips.append("🎯 Apply early! Early bird applications often have lower fees.")
    tips.append("📧 Email professors for application fee waivers - many universities offer this.")
    
    return tips[:4]  # Return top 4 tips