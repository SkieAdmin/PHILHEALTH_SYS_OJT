# PhilHealth eKonsulta Implementation
# PHASE 5: Documents, Testing & Certification

---

## Phase Overview

| Attribute | Details |
|-----------|---------|
| **Phase Number** | 5 of 5 |
| **Duration** | 2-3 Weeks |
| **Priority** | 🔴 Critical - Final certification |
| **Dependencies** | Phase 1, 2, 3, 4 |
| **Outcome** | PhilHealth-certified eKonsulta system |

---

## What You'll Build in This Phase

```
Final Deliverables:
├── eKAS Generator          # Electronic Konsulta Availment Slip
├── ePresS Generator        # Electronic Prescription Slip
├── Laboratory Results      # LABEXAM tracking
├── Test Suite              # Comprehensive testing
└── Certification Prep      # Stage 1 & Stage 2 readiness
```

---

## STEP 1: Electronic Documents (eKAS & ePresS)

### 1.1 Understanding eKAS

The **eKAS (Electronic Konsulta Availment Slip)** is the proof of service for each consultation. It must be generated and signed by the patient.

```
┌─────────────────────────────────────────────────────────────────┐
│                    eKAS CONTENTS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HEADER                                                          │
│  • PhilHealth Logo                                               │
│  • "ELECTRONIC KONSULTA AVAILMENT SLIP"                         │
│  • Facility Name & Accreditation Number                         │
│                                                                  │
│  TRANSACTION INFO                                                │
│  • Case Number (HciCaseNo)                                       │
│  • Transaction Number (HciTransNo)                               │
│  • Date of Service                                               │
│                                                                  │
│  PATIENT INFO                                                    │
│  • Full Name                                                     │
│  • Age                                                           │
│  • PhilHealth PIN                                                │
│  • Contact Number                                                │
│  • Membership Category (Member/Dependent)                        │
│                                                                  │
│  SERVICES RENDERED                                               │
│  • Service Type (Consultation, Lab, Medicine)                    │
│  • Service Date                                                  │
│  • Description                                                   │
│                                                                  │
│  PROVIDER                                                        │
│  • Physician Name                                                │
│  • License Number                                                │
│  • Signature                                                     │
│                                                                  │
│  PATIENT SATISFACTION                                            │
│  • Rating (1-5 scale)                                            │
│  • Comments                                                      │
│                                                                  │
│  SIGNATURES                                                      │
│  • Patient/Representative Signature                              │
│  • Date                                                          │
│                                                                  │
│  NEXT VISIT                                                      │
│  • Next Consultation Date                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 eKAS Generator Code

**File: `philhealth/documents/ekas_generator.py`**

```python
"""
eKAS (Electronic Konsulta Availment Slip) Generator

Generates PDF documents as proof of Konsulta service availment.
"""

from io import BytesIO
from datetime import datetime
from typing import Optional

from django.template.loader import render_to_string
from django.conf import settings

# For PDF generation (install: pip install weasyprint)
# Alternative: pip install reportlab
try:
    from weasyprint import HTML, CSS
    PDF_ENGINE = 'weasyprint'
except ImportError:
    PDF_ENGINE = None


class EKASGenerator:
    """
    Generates eKAS documents for consultations.
    
    Usage:
        generator = EKASGenerator()
        pdf_bytes = generator.generate(consultation)
    """
    
    def __init__(self):
        self.template_name = 'philhealth/documents/ekas_template.html'
    
    def generate(self, consultation) -> bytes:
        """
        Generate eKAS PDF for a consultation.
        
        Args:
            consultation: Consultation model instance
            
        Returns:
            bytes: PDF file content
        """
        context = self._build_context(consultation)
        html_content = render_to_string(self.template_name, context)
        
        if PDF_ENGINE == 'weasyprint':
            return self._generate_with_weasyprint(html_content)
        else:
            return self._generate_simple_pdf(context)
    
    def _build_context(self, consultation) -> dict:
        """Build template context from consultation"""
        patient = consultation.patient
        facility = consultation.appointment.patient.facility
        doctor = consultation.doctor
        
        # Get doctor profile
        try:
            doctor_profile = doctor.doctorprofile
        except:
            doctor_profile = None
        
        # Build services list
        services = []
        
        # Add consultation service
        services.append({
            'type': 'Consultation',
            'date': consultation.consultation_date or consultation.date.date(),
            'description': 'Primary Care Consultation'
        })
        
        # Add prescriptions
        for rx in consultation.prescriptions.all():
            if rx.is_dispensed:
                services.append({
                    'type': 'Medicine',
                    'date': rx.dispense_date,
                    'description': f"{rx.medicine.name} x{rx.quantity_dispensed}"
                })
        
        return {
            # Facility Info
            'facility_name': facility.name if facility else 'Healthcare Facility',
            'facility_accreditation': facility.accreditation_number if facility else '',
            'facility_address': facility.address if facility else '',
            
            # Transaction Info
            'case_no': consultation.enlistment.hci_case_no if consultation.enlistment else '',
            'trans_no': consultation.hci_trans_no or '',
            'service_date': consultation.consultation_date or consultation.date.date(),
            
            # Patient Info
            'patient_name': patient.full_name,
            'patient_age': patient.age,
            'patient_pin': patient.philhealth_pin or 'N/A',
            'patient_contact': patient.contact_number,
            'patient_type': 'Member' if patient.patient_type == 'MM' else 'Dependent',
            
            # Services
            'services': services,
            
            # Provider Info
            'physician_name': doctor_profile.full_name if doctor_profile else str(doctor),
            'physician_license': doctor_profile.license_number if doctor_profile else '',
            'physician_accreditation': doctor_profile.philhealth_accreditation_no if doctor_profile else '',
            
            # Follow-up
            'next_consultation': consultation.next_consultation_date,
            
            # Meta
            'generated_at': datetime.now(),
            'rating_scale': range(1, 6),  # 1-5 rating
        }
    
    def _generate_with_weasyprint(self, html_content: str) -> bytes:
        """Generate PDF using WeasyPrint"""
        css = CSS(string='''
            @page { size: A4; margin: 1cm; }
            body { font-family: Arial, sans-serif; font-size: 11pt; }
            .header { text-align: center; margin-bottom: 20px; }
            .section { margin: 15px 0; }
            .label { font-weight: bold; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .signature-line { border-top: 1px solid black; width: 200px; margin-top: 50px; }
        ''')
        
        html = HTML(string=html_content)
        pdf_file = BytesIO()
        html.write_pdf(pdf_file, stylesheets=[css])
        return pdf_file.getvalue()
    
    def _generate_simple_pdf(self, context: dict) -> bytes:
        """Fallback: Generate simple text-based PDF"""
        # This is a simplified fallback - recommend installing weasyprint
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        y = height - 50
        
        # Header
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "ELECTRONIC KONSULTA AVAILMENT SLIP (eKAS)")
        y -= 30
        
        # Facility
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Facility: {context['facility_name']}")
        y -= 15
        p.drawString(50, y, f"Accreditation No: {context['facility_accreditation']}")
        y -= 30
        
        # Patient Info
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, "PATIENT INFORMATION")
        y -= 15
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Name: {context['patient_name']}")
        y -= 15
        p.drawString(50, y, f"PIN: {context['patient_pin']}")
        y -= 15
        p.drawString(50, y, f"Age: {context['patient_age']}")
        y -= 30
        
        # Services
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, "SERVICES RENDERED")
        y -= 15
        p.setFont("Helvetica", 10)
        for service in context['services']:
            p.drawString(50, y, f"• {service['type']}: {service['description']} ({service['date']})")
            y -= 15
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()


# Convenience function
def generate_ekas(consultation) -> bytes:
    """Generate eKAS for a consultation"""
    generator = EKASGenerator()
    return generator.generate(consultation)
```

### 1.3 eKAS HTML Template

**File: `templates/philhealth/documents/ekas_template.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>eKAS - Electronic Konsulta Availment Slip</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #2e7d32;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #2e7d32;
            margin: 0;
            font-size: 16pt;
        }
        .header h2 {
            color: #333;
            margin: 5px 0;
            font-size: 12pt;
        }
        .section {
            margin: 15px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .section-title {
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 10px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .row {
            display: flex;
            margin: 5px 0;
        }
        .label {
            font-weight: bold;
            width: 150px;
            flex-shrink: 0;
        }
        .value {
            flex-grow: 1;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
        }
        .signatures {
            display: flex;
            justify-content: space-between;
            margin-top: 40px;
        }
        .signature-box {
            text-align: center;
            width: 45%;
        }
        .signature-line {
            border-top: 1px solid black;
            margin-top: 50px;
            padding-top: 5px;
        }
        .rating-section {
            margin: 20px 0;
        }
        .rating-circles {
            display: flex;
            gap: 10px;
        }
        .rating-circle {
            width: 30px;
            height: 30px;
            border: 2px solid #2e7d32;
            border-radius: 50%;
            text-align: center;
            line-height: 26px;
        }
        .footer {
            margin-top: 30px;
            font-size: 9pt;
            color: #666;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>PhilHealth</h1>
        <h2>ELECTRONIC KONSULTA AVAILMENT SLIP (eKAS)</h2>
        <p>{{ facility_name }}</p>
        <p>Accreditation No: {{ facility_accreditation }}</p>
    </div>
    
    <div class="section">
        <div class="section-title">TRANSACTION INFORMATION</div>
        <div class="row">
            <span class="label">Case No:</span>
            <span class="value">{{ case_no }}</span>
        </div>
        <div class="row">
            <span class="label">Transaction No:</span>
            <span class="value">{{ trans_no }}</span>
        </div>
        <div class="row">
            <span class="label">Service Date:</span>
            <span class="value">{{ service_date }}</span>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">PATIENT INFORMATION</div>
        <div class="row">
            <span class="label">Name:</span>
            <span class="value">{{ patient_name }}</span>
        </div>
        <div class="row">
            <span class="label">Age:</span>
            <span class="value">{{ patient_age }} years old</span>
        </div>
        <div class="row">
            <span class="label">PhilHealth PIN:</span>
            <span class="value">{{ patient_pin }}</span>
        </div>
        <div class="row">
            <span class="label">Contact No:</span>
            <span class="value">{{ patient_contact }}</span>
        </div>
        <div class="row">
            <span class="label">Category:</span>
            <span class="value">{{ patient_type }}</span>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">SERVICES RENDERED</div>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {% for service in services %}
                <tr>
                    <td>{{ service.type }}</td>
                    <td>{{ service.description }}</td>
                    <td>{{ service.date }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">ATTENDING PHYSICIAN</div>
        <div class="row">
            <span class="label">Name:</span>
            <span class="value">{{ physician_name }}</span>
        </div>
        <div class="row">
            <span class="label">License No:</span>
            <span class="value">{{ physician_license }}</span>
        </div>
    </div>
    
    <div class="rating-section">
        <div class="section-title">PATIENT SATISFACTION RATING</div>
        <p>Please rate your experience (1-5, with 5 being highest):</p>
        <div class="rating-circles">
            {% for i in rating_scale %}
            <div class="rating-circle">{{ i }}</div>
            {% endfor %}
        </div>
    </div>
    
    {% if next_consultation %}
    <div class="section">
        <div class="section-title">NEXT CONSULTATION</div>
        <p>Recommended follow-up: <strong>{{ next_consultation }}</strong></p>
    </div>
    {% endif %}
    
    <div class="signatures">
        <div class="signature-box">
            <div class="signature-line">
                <p>Provider's Signature</p>
            </div>
        </div>
        <div class="signature-box">
            <div class="signature-line">
                <p>Patient/Representative's Signature</p>
                <p>Date: _______________</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated: {{ generated_at }}</p>
        <p>This is a computer-generated document. No signature required if electronically transmitted.</p>
    </div>
</body>
</html>
```

### 1.4 ePresS Generator (Similar Structure)

**File: `philhealth/documents/epress_generator.py`**

```python
"""
ePresS (Electronic Prescription Slip) Generator

Generates PDF documents for medicine prescriptions/dispensing.
"""

from io import BytesIO
from datetime import datetime

from django.template.loader import render_to_string


class EPressGenerator:
    """
    Generates ePresS documents for prescriptions.
    
    Usage:
        generator = EPressGenerator()
        pdf_bytes = generator.generate(consultation)
    """
    
    def __init__(self):
        self.template_name = 'philhealth/documents/epress_template.html'
    
    def generate(self, consultation) -> bytes:
        """Generate ePresS PDF for a consultation"""
        context = self._build_context(consultation)
        html_content = render_to_string(self.template_name, context)
        
        # Use same PDF generation logic as eKAS
        from .ekas_generator import EKASGenerator
        generator = EKASGenerator()
        return generator._generate_with_weasyprint(html_content)
    
    def _build_context(self, consultation) -> dict:
        """Build template context"""
        patient = consultation.patient
        facility = consultation.appointment.patient.facility
        
        # Build medicines list
        medicines = []
        for rx in consultation.prescriptions.all():
            medicines.append({
                'name': rx.medicine.name,
                'generic_name': rx.medicine.generic_name or rx.medicine.name,
                'strength': rx.medicine.strength or '',
                'form': rx.medicine.form or '',
                'quantity_prescribed': rx.quantity,
                'quantity_dispensed': rx.quantity_dispensed,
                'instructions': rx.doctor_prescription or '',
                'dispense_date': rx.dispense_date,
                'is_dispensed': rx.is_dispensed,
            })
        
        return {
            # Facility
            'facility_name': facility.name if facility else '',
            'facility_accreditation': facility.accreditation_number if facility else '',
            
            # Patient
            'patient_name': patient.full_name,
            'patient_pin': patient.philhealth_pin or 'N/A',
            'patient_age': patient.age,
            
            # Prescription
            'prescription_date': consultation.consultation_date or consultation.date.date(),
            'medicines': medicines,
            
            # Prescriber
            'prescriber_name': str(consultation.doctor),
            'prescriber_license': getattr(consultation.doctor, 'doctorprofile', None),
            
            # Meta
            'generated_at': datetime.now(),
        }


def generate_epress(consultation) -> bytes:
    """Generate ePresS for a consultation"""
    generator = EPressGenerator()
    return generator.generate(consultation)
```

---

## STEP 2: Laboratory Results Model

**Add to `philhealth/models.py`:**

```python
class LaboratoryRequest(models.Model):
    """
    Laboratory/Diagnostic test request.
    
    Created when a doctor orders a test during consultation.
    """
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('D', 'Done'),
        ('N', 'Not yet done'),
        ('X', 'Deferred'),
        ('W', 'Waived'),
    ]
    
    consultation = models.ForeignKey(
        'doctor.Consultation',
        on_delete=models.CASCADE,
        related_name='lab_requests'
    )
    
    lab_code = models.ForeignKey(
        LaboratoryExamCode,
        on_delete=models.PROTECT
    )
    
    request_date = models.DateField()
    
    requesting_physician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    referral_facility = models.CharField(
        max_length=200,
        blank=True,
        help_text="If test done at another facility"
    )
    
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='P'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.lab_code.name} for {self.consultation.patient}"


class LaboratoryResult(models.Model):
    """
    Laboratory/Diagnostic test results.
    
    PhilHealth XML Entity: LABEXAM / DIAGNOSTICEXAMRESULT
    """
    request = models.OneToOneField(
        LaboratoryRequest,
        on_delete=models.CASCADE,
        related_name='result'
    )
    
    result_date = models.DateField()
    
    # Generic result fields
    findings = models.TextField(blank=True)
    result_value = models.CharField(max_length=500, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    
    interpretation = models.CharField(
        max_length=20,
        choices=[
            ('NORMAL', 'Normal'),
            ('ABNORMAL', 'Abnormal'),
            ('CRITICAL', 'Critical'),
        ],
        blank=True
    )
    
    diagnostic_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    performed_by = models.CharField(max_length=200, blank=True)
    verified_by = models.CharField(max_length=200, blank=True)
    
    report_status = models.CharField(max_length=1, default='U')
    deficiency_remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-result_date']
    
    def __str__(self):
        return f"Result: {self.request.lab_code.name}"
```

---

## STEP 3: PhilHealth Certification Checklist

### 3.1 Stage 1 - Regional Office Testing

**Data Completeness (A):**
```
□ A.1  Captures Provider Accreditation Number
       → HealthCareInstitution.accreditation_number
       
□ A.2  Captures Member PIN (12 digits)
       → Patient.philhealth_pin with validation
       
□ A.3  Captures Dependent PIN (if applicable)
       → Patient.philhealth_pin for dependents
       
□ A.4  Captures Health Screening & Assessment Data
       → Profile, MedicalHistory, FamilyHistory, 
         SocialHistory, VitalSigns
       
□ A.5  Captures Consultation, Medicine, Diagnostic Exam
       → Consultation (SOAP), Prescription, LaboratoryResult
       
□ A.6  Compliance to PhilHealth Libraries
       → DiseaseCode, DrugCode, LaboratoryExamCode
       
□ A.7  Implements recommended services per age group
       → NCDRiskAssessment (25+), age-based screening
```

**Process Requirements (B):**
```
□ B.1  Download/Upload Registration Masterlist (XML)
       → PKAClient.extract_registration_list()
       
□ B.2  Validates Member/Dependent Registration
       → PKAClient.is_member_registered()
       
□ B.3  Validates Authorization Transaction Code (ATC)
       → PKAClient.is_atc_valid()
       
□ B.4  Generates Transmittal ID per XML Submission
       → HCI.get_next_transmittal_number()
       
□ B.5  Submit First Tranche Konsulta Report (XML)
       → KonsultaXMLGenerator.generate_first_tranche()
         PKAClient.submit_report(tagging='1')
       
□ B.6  Submit Second Tranche Konsulta Report (XML)
       → KonsultaXMLGenerator.generate_second_tranche()
         PKAClient.submit_report(tagging='2')
       
□ B.7  Captures Transaction Number upon submission
       → TransmittalReport.transaction_number
       
□ B.8  Generates and prints eKAS
       → EKASGenerator.generate()
       
□ B.9  Generates and prints ePresS
       → EPressGenerator.generate()
       
□ B.10 Upload XML for data transfer/migration
       → XML import functionality
```

**Controls/Validation (C):**
```
□ C.1  PIN length = 12
       → validate_philhealth_pin()
       
□ C.2  All data in UPPERCASE
       → validate_uppercase() in save methods
       
□ C.3  PIN required for beneficiary
       → Patient.philhealth_pin required
       
□ C.4  Patient type defined (MM/DD)
       → Patient.patient_type
       
□ C.5  Implementation of Cipher Key
       → PhilHealthEncryption class
       
□ C.6  Implementation of ATC
       → Appointment.atc, PKAClient.is_atc_valid()
```

### 3.2 Stage 2 - Central Office Testing

**Security (D):**
```
□ D.1  Implementation of Token
       → PKAClient.get_token()
       
□ D.2  Implementation of Username/Password
       → HCI.pka_username, HCI.pka_password
       
□ D.3  Encryption of XML
       → PhilHealthEncryption.encrypt_xml()
       
□ D.4  Decryption of XML
       → PhilHealthEncryption.decrypt_xml()
```

**Encrypted XML (E):**
```
□ E.1  Can be decrypted by PhilHealth utility
       → Test with PhilHealth's decryption tool
       
□ E.2  Decrypted XML matches raw data
       → Encryption roundtrip test
       
□ E.3  Filename convention compliance
       → TransmittalId as filename
```

**Konsulta Data (F):**
```
□ F.1  XML data matches database
       → XML generator produces accurate data
```

---

## STEP 4: Testing Suite

**File: `philhealth/tests/test_certification.py`**

```python
"""
PhilHealth Certification Tests

Run these tests before submitting for PhilHealth certification.

Usage:
    python manage.py test philhealth.tests.test_certification
"""

from django.test import TestCase
from datetime import date, datetime

from philhealth.models import (
    HealthCareInstitution, Enlistment, Profile,
    DiseaseCode, DrugCode, LaboratoryExamCode
)
from philhealth.validators import (
    validate_philhealth_pin, validate_atc,
    validate_uppercase, generate_pin_check_digit
)
from philhealth.encryption import (
    PhilHealthEncryption, encrypt_xml_payload, decrypt_xml_payload
)
from secretary.models import Patient


class PINValidationTests(TestCase):
    """Test C.1: PIN length = 12 with mod-11 check"""
    
    def test_valid_pin(self):
        """Valid 12-digit PIN with correct check digit"""
        pin = generate_pin_check_digit("01234567890")
        result = validate_philhealth_pin(pin)
        self.assertEqual(len(result), 12)
    
    def test_pin_with_dashes(self):
        """PIN with dashes should be cleaned"""
        pin = generate_pin_check_digit("01234567890")
        formatted = f"{pin[:2]}-{pin[2:11]}-{pin[11]}"
        result = validate_philhealth_pin(formatted)
        self.assertEqual(result, pin)
    
    def test_invalid_pin_length(self):
        """PIN with wrong length should fail"""
        with self.assertRaises(Exception):
            validate_philhealth_pin("123456789")  # 9 digits
    
    def test_invalid_check_digit(self):
        """PIN with wrong check digit should fail"""
        with self.assertRaises(Exception):
            validate_philhealth_pin("012345678999")  # Wrong check


class UppercaseValidationTests(TestCase):
    """Test C.2: All data in UPPERCASE"""
    
    def test_uppercase_conversion(self):
        """Text should be converted to uppercase"""
        result = validate_uppercase("juan dela cruz")
        self.assertEqual(result, "JUAN DELA CRUZ")
    
    def test_patient_name_uppercase(self):
        """Patient names saved in uppercase"""
        patient = Patient(
            first_name="juan",
            last_name="dela cruz",
            birth_date=date(1990, 1, 1),
            gender="M",
            contact_number="09171234567"
        )
        patient.save()
        
        self.assertEqual(patient.first_name, "JUAN")
        self.assertEqual(patient.last_name, "DELA CRUZ")


class ATCValidationTests(TestCase):
    """Test C.6: ATC Implementation"""
    
    def test_valid_atc(self):
        """Valid 10-character ATC"""
        result = validate_atc("ABC1234567")
        self.assertEqual(len(result), 10)
    
    def test_walkin_atc(self):
        """WALKEDIN is valid"""
        result = validate_atc("walkedin")
        self.assertEqual(result, "WALKEDIN")
    
    def test_invalid_atc_length(self):
        """ATC with wrong length should fail"""
        with self.assertRaises(Exception):
            validate_atc("ABC123")  # Too short


class EncryptionTests(TestCase):
    """Test D.3/D.4: XML Encryption/Decryption"""
    
    def setUp(self):
        self.cipher_key = "test-cipher-key-12345"
        self.test_xml = """<?xml version="1.0"?>
        <PCB>
            <pHciAccreNo>123456789</pHciAccreNo>
            <ENLISTMENT>
                <pMemPin>012345678901</pMemPin>
            </ENLISTMENT>
        </PCB>"""
    
    def test_encryption_produces_json(self):
        """Encryption should produce valid JSON"""
        import json
        encrypted = encrypt_xml_payload(self.test_xml, self.cipher_key)
        data = json.loads(encrypted)
        
        self.assertIn('doc', data)
        self.assertIn('iv', data)
        self.assertIn('hash', data)
    
    def test_decryption_recovers_original(self):
        """Decryption should recover original XML"""
        encrypted = encrypt_xml_payload(self.test_xml, self.cipher_key)
        decrypted, valid = decrypt_xml_payload(encrypted, self.cipher_key)
        
        self.assertTrue(valid)
        self.assertIn('012345678901', decrypted)
    
    def test_integrity_check(self):
        """Hash verification should work"""
        encrypted = encrypt_xml_payload(self.test_xml, self.cipher_key)
        decrypted, integrity = decrypt_xml_payload(encrypted, self.cipher_key)
        
        self.assertTrue(integrity)


class IDGenerationTests(TestCase):
    """Test B.4: Transmittal ID Generation"""
    
    def setUp(self):
        self.facility = HealthCareInstitution.objects.create(
            accreditation_number="123456789",
            pmcc_number="123456",
            name="Test Facility",
            address="Test Address"
        )
    
    def test_case_number_format(self):
        """HciCaseNo: T + AccreNo(9) + YYYYMM + 4digits"""
        case_no = self.facility.get_next_case_number()
        
        self.assertTrue(case_no.startswith('T'))
        self.assertIn('123456789', case_no)
        self.assertEqual(len(case_no), 20)  # T + 9 + 6 + 4
    
    def test_enlistment_number_format(self):
        """HciTransNo: E + AccreNo(9) + YYYYMM + 5digits"""
        trans_no = self.facility.get_next_enlistment_number()
        
        self.assertTrue(trans_no.startswith('E'))
        self.assertEqual(len(trans_no), 21)  # E + 9 + 6 + 5
    
    def test_transmittal_id_format(self):
        """TransmittalId: R + AccreNo(9) + YYYYMM + 5digits"""
        transmittal = self.facility.get_next_transmittal_number()
        
        self.assertTrue(transmittal.startswith('R'))
        self.assertEqual(len(transmittal), 21)


class XMLGenerationTests(TestCase):
    """Test B.5/B.6: XML Report Generation"""
    
    def setUp(self):
        # Create test facility
        self.facility = HealthCareInstitution.objects.create(
            accreditation_number="123456789",
            pmcc_number="123456",
            name="Test Facility",
            address="Test Address",
            pka_username="testuser",
            software_certification_id="CERT12345"
        )
        
        # Create test patient
        self.patient = Patient.objects.create(
            first_name="JUAN",
            last_name="DELA CRUZ",
            philhealth_pin=generate_pin_check_digit("01234567890"),
            birth_date=date(1990, 1, 1),
            gender="M",
            contact_number="09171234567",
            patient_type="MM",
            facility=self.facility
        )
        
        # Create enlistment
        self.enlistment = Enlistment.objects.create(
            facility=self.facility,
            patient=self.patient,
            effectivity_year="2024",
            enlistment_date=date.today(),
            package_type="K"
        )
    
    def test_first_tranche_xml_structure(self):
        """First tranche XML has required elements"""
        from philhealth.xml_generator import KonsultaXMLGenerator
        
        generator = KonsultaXMLGenerator(self.facility)
        xml = generator.generate_first_tranche("2024-12")
        
        self.assertIn('<PCB>', xml)
        self.assertIn('<ENLISTMENT>', xml)
        self.assertIn('<pHciAccreNo>123456789</pHciAccreNo>', xml)
```

---

## STEP 5: Deployment Checklist

### Pre-Deployment Requirements

```
Infrastructure:
□ Dedicated internet (minimum 1 Mbps)
□ Public IP address (submitted to PhilHealth)
□ SSL certificate installed
□ Backup system configured
□ Monitoring configured

PhilHealth Credentials:
□ PKA username obtained
□ PKA password obtained
□ Software Certification ID obtained
□ Cipher key obtained
□ Public IP registered with PhilHealth

Database:
□ All migrations applied
□ Reference data loaded (disease codes, drug codes, lab codes)
□ Healthcare Institution record created
□ Test data cleared

Security:
□ Production secrets configured
□ DEBUG = False
□ Allowed hosts configured
□ HTTPS enforced
```

### Go-Live Checklist

```
Week Before:
□ Final Stage 2 testing passed
□ Staff training completed
□ Support contacts documented
□ Rollback plan prepared

Day Before:
□ Final backup taken
□ Monitoring alerts configured
□ On-call support arranged

Go-Live:
□ Deploy application
□ Verify all services running
□ Test login functionality
□ Test patient registration
□ Test consultation workflow
□ Test XML submission (with test data)
□ Monitor for errors

Post Go-Live:
□ Monitor first real submissions
□ Address any issues immediately
□ Collect user feedback
□ Document lessons learned
```

---

## Summary: Complete Implementation

After completing all 5 phases, you will have:

| Phase | Components |
|-------|------------|
| **Phase 1** | PhilHealth app, HCI model, encryption, validators, reference libraries |
| **Phase 2** | Enhanced Patient, Appointment, Consultation, Medicine, Prescription |
| **Phase 3** | Enlistment, Profile, Medical/Family/Social History, VitalSigns, NCD Assessment |
| **Phase 4** | PKA Client, XML Generator, TransmittalReport |
| **Phase 5** | eKAS/ePresS generators, Laboratory models, Test suite, Certification prep |

---

## Final Notes

### Important Reminders

1. **Never hardcode credentials** - Use environment variables
2. **Test encryption** with PhilHealth's decryption utility before submission
3. **All patient names must be UPPERCASE**
4. **PIN validation is critical** - Invalid PINs will fail submission
5. **Keep transaction logs** for audit purposes
6. **Regular backups** - XML submissions are time-sensitive

### Support Contacts

- **PhilHealth Action Center:** (02) 8441-7442
- **Email:** actioncenter@philhealth.gov.ph
- **Website:** www.philhealth.gov.ph

---

*Congratulations! You have completed the PhilHealth eKonsulta Implementation Guide.*
