# PhilHealth eKonsulta Implementation
# PHASE 1: PhilHealth Core Module

---

## Phase Overview

| Attribute | Details |
|-----------|---------|
| **Phase Number** | 1 of 5 |
| **Duration** | 1-2 Weeks |
| **Priority** | 🔴 Critical - Foundation for all PhilHealth features |
| **Dependencies** | None (this is the foundation) |
| **Outcome** | Core PhilHealth infrastructure ready |

---

## What You'll Build in This Phase

```
philhealth/                          # NEW Django App
├── __init__.py
├── admin.py                         # Admin interface for PhilHealth models
├── apps.py                          # App configuration
├── models.py                        # Core models (HCI, Reference Libraries)
├── validators.py                    # PIN validation, ATC validation
├── encryption.py                    # AES-256-CBC encryption module
├── id_generators.py                 # HciCaseNo, HciTransNo generators
├── migrations/
│   └── __init__.py
├── management/
│   └── commands/
│       └── load_philhealth_data.py  # Load reference data
└── tests/
    ├── __init__.py
    ├── test_validators.py
    └── test_encryption.py
```

---

## Why This Phase First?

### The Problem
PhilHealth requires specific data formats, validations, and encryption that don't exist in standard Django. Without these foundations, you cannot:
- Validate PhilHealth PINs correctly
- Encrypt XML payloads for API submission
- Generate proper transaction IDs
- Reference PhilHealth code libraries

### The Solution
Create a dedicated `philhealth` app that provides:
1. **Healthcare Institution (HCI) Model** - Your facility's identity
2. **Reference Libraries** - Disease codes, drug codes, lab codes
3. **Validators** - PIN and ATC validation
4. **Encryption** - AES-256-CBC for secure API communication
5. **ID Generators** - Proper PhilHealth ID formats

---

## Step-by-Step Implementation

---

## STEP 1: Create the PhilHealth App

### 1.1 Run Django Command

```bash
# In your project directory (where manage.py is located)
cd C:\Projects\PHILHEALTH_SYS_OJT\philhealth_eKonsulta

# Create the new app
python manage.py startapp philhealth
```

### 1.2 Register the App

**File: `philhealth_eKonsulta/settings.py`**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your existing apps
    'login',
    'secretary',
    'doctor',
    'finance',
    
    # NEW: PhilHealth core module
    'philhealth',
]
```

### 1.3 Why a Separate App?

| Reason | Explanation |
|--------|-------------|
| **Separation of Concerns** | PhilHealth-specific logic stays isolated |
| **Reusability** | Can be used by doctor, secretary, finance apps |
| **Maintainability** | PhilHealth changes don't affect other apps |
| **Testing** | Easier to test PhilHealth features independently |

---

## STEP 2: Healthcare Institution (HCI) Model

### 2.1 Understanding the HCI Model

The **Healthcare Institution (HCI)** represents YOUR facility in the PhilHealth system. It's the ROOT entity - everything else (patients, consultations, reports) belongs to an HCI.

```
┌─────────────────────────────────────────────────────────────────┐
│                 HEALTHCARE INSTITUTION (HCI)                     │
│                    Your Clinic/Hospital                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Identity                     API Credentials                    │
│  ─────────                    ───────────────                    │
│  • Accreditation No (9-digit) • PKA Username                    │
│  • PMCC Number (6-digit)      • PKA Password                    │
│  • Name, Address              • Cipher Key (encryption)         │
│  • Contact Info               • Software Certification ID       │
│                                                                  │
│  ID Series Counters           Status                            │
│  ─────────────────            ──────                            │
│  • Case Series                • Is Active                       │
│  • Enlistment Series          • Konsulta Accredited            │
│  • Profile Series             • Accreditation Expiry           │
│  • SOAP Series                                                  │
│  • Transmittal Series                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ owns
                              ▼
         ┌────────────────────┴────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │Patients │         │Enlistmts│         │ Reports │
    └─────────┘         └─────────┘         └─────────┘
```

### 2.2 PhilHealth ID Formats

PhilHealth uses specific ID formats. The HCI model generates these:

| ID Type | Format | Example | Used For |
|---------|--------|---------|----------|
| **HciCaseNo** | T + AccreNo(9) + YYYYMM + 4digits | T12345678920241200001 | Patient case tracking |
| **Enlistment TransNo** | E + AccreNo(9) + YYYYMM + 5digits | E1234567892024120001 | Enlistment records |
| **Profile TransNo** | P + AccreNo(9) + YYYYMM + 5digits | P1234567892024120001 | FPE records |
| **SOAP TransNo** | S + AccreNo(9) + YYYYMM + 5digits | S1234567892024120001 | Consultation records |
| **Transmittal ID** | R + AccreNo(9) + YYYYMM + 5digits | R1234567892024120001 | XML report submission |

### 2.3 The Model Code

**File: `philhealth/models.py`**

```python
from django.db import models
from django.conf import settings
from django.utils import timezone


class HealthCareInstitution(models.Model):
    """
    Healthcare Institution (HCI) / Konsulta Package Provider (KPP)
    
    This is the ROOT entity in the PhilHealth eKonsulta system.
    Your clinic/hospital must be registered as an HCI with PhilHealth
    to participate in the Konsulta program.
    
    Maps to: PCB (root) header fields in PhilHealth XML
    
    PhilHealth XML Reference:
    - pHciAccreNo: accreditation_number
    - pPMCCNo: pmcc_number
    - pUsername: pka_username
    - pPassword: pka_password
    - pCertificationId: software_certification_id
    """
    
    # ═══════════════════════════════════════════════════════════════
    # PHILHEALTH IDENTIFIERS
    # These are assigned by PhilHealth when your facility is accredited
    # ═══════════════════════════════════════════════════════════════
    
    accreditation_number = models.CharField(
        max_length=9,
        unique=True,
        help_text="9-digit PhilHealth Accreditation Number (PAN). "
                  "Example: 123456789. Assigned by PhilHealth."
    )
    
    pmcc_number = models.CharField(
        max_length=6,
        help_text="6-digit PMCC Number. Assigned by PhilHealth."
    )
    
    # ═══════════════════════════════════════════════════════════════
    # FACILITY INFORMATION
    # Basic details about your healthcare facility
    # ═══════════════════════════════════════════════════════════════
    
    name = models.CharField(
        max_length=200,
        help_text="Official name of the healthcare facility"
    )
    
    address = models.TextField(
        help_text="Complete address of the facility"
    )
    
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    
    email = models.EmailField(
        blank=True,
        help_text="Official email address"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # PHILHEALTH API CREDENTIALS
    # These are provided by PhilHealth after software certification
    # IMPORTANT: Store encrypted in production!
    # ═══════════════════════════════════════════════════════════════
    
    pka_username = models.CharField(
        max_length=30,
        blank=True,
        help_text="Username for PhilHealth Konsulta API (PKA). "
                  "Provided by PhilHealth after certification."
    )
    
    pka_password = models.CharField(
        max_length=100,
        blank=True,
        help_text="Password for PKA. MUST be encrypted in production! "
                  "Provided by PhilHealth after certification."
    )
    
    cipher_key = models.CharField(
        max_length=200,
        blank=True,
        help_text="Cipher key/passphrase for XML encryption. "
                  "MUST be encrypted in production! "
                  "Unique per facility, provided by PhilHealth."
    )
    
    software_certification_id = models.CharField(
        max_length=30,
        blank=True,
        help_text="Software Certification ID. "
                  "Issued after passing PhilHealth software validation."
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ID SERIES COUNTERS
    # Used to generate unique PhilHealth transaction IDs
    # These auto-increment with each new record
    # ═══════════════════════════════════════════════════════════════
    
    case_series = models.IntegerField(
        default=0,
        help_text="Counter for HciCaseNo generation. Auto-increments."
    )
    
    enlistment_series = models.IntegerField(
        default=0,
        help_text="Counter for Enlistment HciTransNo generation."
    )
    
    profile_series = models.IntegerField(
        default=0,
        help_text="Counter for Profile HciTransNo generation."
    )
    
    soap_series = models.IntegerField(
        default=0,
        help_text="Counter for SOAP HciTransNo generation."
    )
    
    transmittal_series = models.IntegerField(
        default=0,
        help_text="Counter for Transmittal ID generation."
    )
    
    # ═══════════════════════════════════════════════════════════════
    # STATUS FLAGS
    # Track facility accreditation status
    # ═══════════════════════════════════════════════════════════════
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this facility currently active?"
    )
    
    konsulta_accredited = models.BooleanField(
        default=False,
        help_text="Is this facility accredited for Konsulta package?"
    )
    
    accreditation_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="When does the Konsulta accreditation expire?"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Healthcare Institution"
        verbose_name_plural = "Healthcare Institutions"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.accreditation_number})"
    
    # ═══════════════════════════════════════════════════════════════
    # ID GENERATION METHODS
    # These generate PhilHealth-compliant transaction IDs
    # ═══════════════════════════════════════════════════════════════
    
    def get_next_case_number(self) -> str:
        """
        Generate next HciCaseNo for a new patient case.
        
        Format: T + AccreNo(9) + YYYYMM + 4digits
        Example: T123456789202412-0001
        
        The 'T' prefix indicates this is a patient case/transaction number.
        
        Returns:
            str: The next HciCaseNo
        """
        self.case_series += 1
        self.save(update_fields=['case_series'])
        date_part = timezone.now().strftime('%Y%m')
        return f"T{self.accreditation_number}{date_part}{self.case_series:04d}"
    
    def get_next_enlistment_number(self) -> str:
        """
        Generate next HciTransNo for Enlistment records.
        
        Format: E + AccreNo(9) + YYYYMM + 5digits
        Example: E12345678920241200001
        
        The 'E' prefix indicates this is an Enlistment transaction.
        
        Returns:
            str: The next Enlistment HciTransNo
        """
        self.enlistment_series += 1
        self.save(update_fields=['enlistment_series'])
        date_part = timezone.now().strftime('%Y%m')
        return f"E{self.accreditation_number}{date_part}{self.enlistment_series:05d}"
    
    def get_next_profile_number(self) -> str:
        """
        Generate next HciTransNo for Profile (FPE) records.
        
        Format: P + AccreNo(9) + YYYYMM + 5digits
        Example: P12345678920241200001
        
        The 'P' prefix indicates this is a Profile/FPE transaction.
        
        Returns:
            str: The next Profile HciTransNo
        """
        self.profile_series += 1
        self.save(update_fields=['profile_series'])
        date_part = timezone.now().strftime('%Y%m')
        return f"P{self.accreditation_number}{date_part}{self.profile_series:05d}"
    
    def get_next_soap_number(self) -> str:
        """
        Generate next HciTransNo for SOAP/Consultation records.
        
        Format: S + AccreNo(9) + YYYYMM + 5digits
        Example: S12345678920241200001
        
        The 'S' prefix indicates this is a SOAP/Consultation transaction.
        
        Returns:
            str: The next SOAP HciTransNo
        """
        self.soap_series += 1
        self.save(update_fields=['soap_series'])
        date_part = timezone.now().strftime('%Y%m')
        return f"S{self.accreditation_number}{date_part}{self.soap_series:05d}"
    
    def get_next_transmittal_number(self) -> str:
        """
        Generate next TransmittalId for XML report submissions.
        
        Format: R + AccreNo(9) + YYYYMM + 5digits
        Example: R12345678920241200001
        
        The 'R' prefix indicates this is a Report transmittal.
        
        Returns:
            str: The next Transmittal ID
        """
        self.transmittal_series += 1
        self.save(update_fields=['transmittal_series'])
        date_part = timezone.now().strftime('%Y%m')
        return f"R{self.accreditation_number}{date_part}{self.transmittal_series:05d}"
    
    def reset_monthly_series(self) -> None:
        """
        Reset all series counters to 0.
        
        Call this at the start of each month if you want monthly reset.
        Most implementations keep continuous numbering, so this is optional.
        """
        self.case_series = 0
        self.enlistment_series = 0
        self.profile_series = 0
        self.soap_series = 0
        self.transmittal_series = 0
        self.save()
    
    @property
    def is_accreditation_valid(self) -> bool:
        """Check if Konsulta accreditation is still valid."""
        if not self.konsulta_accredited:
            return False
        if not self.accreditation_expiry:
            return True
        return self.accreditation_expiry >= timezone.now().date()
```

### 2.4 How ID Generation Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    ID GENERATION FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. New Patient Enrolled                                         │
│     └─► HCI.get_next_case_number()                              │
│         └─► T + 123456789 + 202412 + 0001                       │
│             │      │           │       │                         │
│             │      │           │       └── Series (4 digits)    │
│             │      │           └── Year+Month                    │
│             │      └── Accreditation Number (9 digits)          │
│             └── Prefix: T = Transaction/Case                    │
│                                                                  │
│  2. Enlistment Created                                           │
│     └─► HCI.get_next_enlistment_number()                        │
│         └─► E + 123456789 + 202412 + 00001                      │
│                                                                  │
│  3. Profile (FPE) Created                                        │
│     └─► HCI.get_next_profile_number()                           │
│         └─► P + 123456789 + 202412 + 00001                      │
│                                                                  │
│  4. Consultation (SOAP) Created                                  │
│     └─► HCI.get_next_soap_number()                              │
│         └─► S + 123456789 + 202412 + 00001                      │
│                                                                  │
│  5. XML Report Submitted                                         │
│     └─► HCI.get_next_transmittal_number()                       │
│         └─► R + 123456789 + 202412 + 00001                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## STEP 3: PhilHealth Reference Libraries

### 3.1 Understanding Reference Libraries

PhilHealth maintains standardized code libraries that ALL software must use. These ensure data consistency across all healthcare providers.

```
┌─────────────────────────────────────────────────────────────────┐
│               PHILHEALTH REFERENCE LIBRARIES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  lib_mdisease (Disease Codes)                                   │
│  ─────────────────────────────                                  │
│  Used for: Medical History, Family History                      │
│  Examples:                                                       │
│  • HTN - Hypertension                                           │
│  • DM  - Diabetes Mellitus                                      │
│  • AST - Asthma                                                 │
│                                                                  │
│  lib_labexam (Laboratory Exam Codes)                            │
│  ────────────────────────────────────                           │
│  Used for: Laboratory test orders and results                   │
│  Examples:                                                       │
│  • CBC    - Complete Blood Count                                │
│  • FBS    - Fasting Blood Sugar                                 │
│  • LIPID  - Lipid Profile                                       │
│                                                                  │
│  lib_drug (Drug Codes)                                          │
│  ─────────────────────                                          │
│  Used for: Medicine prescriptions (ESSENTIALMED)                │
│  Examples:                                                       │
│  • MET500 - Metformin 500mg Tablet                              │
│  • AMX500 - Amoxicillin 500mg Capsule                           │
│                                                                  │
│  ICD-10 (Diagnosis Codes)                                       │
│  ─────────────────────────                                      │
│  Used for: Consultation diagnosis                               │
│  Examples:                                                       │
│  • I10   - Essential hypertension                               │
│  • E11.9 - Type 2 diabetes mellitus                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Reference Library Models

**File: `philhealth/models.py`** (add to existing file)

```python
# Add these models after HealthCareInstitution

class DiseaseCode(models.Model):
    """
    PhilHealth Disease Code Library (lib_mdisease)
    
    These codes are used to record:
    - Patient's past medical history (MEDHIST)
    - Family medical history (FAMHIST)
    
    PhilHealth XML Reference:
    - pMdiseaseCode: code field
    
    IMPORTANT: Disease codes must match PhilHealth's official library.
    Using incorrect codes will cause XML validation to fail.
    
    Examples:
    - HTN: Hypertension
    - DM: Diabetes Mellitus
    - AST: Asthma
    - CAD: Coronary Artery Disease
    - CKD: Chronic Kidney Disease
    """
    
    code = models.CharField(
        max_length=10,
        primary_key=True,
        help_text="PhilHealth disease code (e.g., 'HTN', 'DM')"
    )
    
    description = models.CharField(
        max_length=500,
        help_text="Full description of the disease/condition"
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Category grouping (e.g., 'Cardiovascular', 'Endocrine')"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this code currently active in PhilHealth system?"
    )
    
    class Meta:
        verbose_name = "Disease Code"
        verbose_name_plural = "Disease Codes"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.description}"


class LaboratoryExamCode(models.Model):
    """
    PhilHealth Laboratory Exam Code Library (lib_labexam)
    
    These codes are used to record:
    - Laboratory test orders
    - Laboratory test results (LABEXAM, DIAGNOSTICEXAMRESULT)
    
    PhilHealth XML Reference:
    - pLabCode: code field
    
    Konsulta Covered Tests (15+):
    - CBC: Complete Blood Count with Platelet
    - LIPID: Lipid Profile
    - FBS: Fasting Blood Sugar
    - OGTT: Oral Glucose Tolerance Test
    - HBA1C: Hemoglobin A1c
    - CREAT: Creatinine
    - URINE: Urinalysis
    - FECAL: Fecalysis
    - FOBT: Fecal Occult Blood Test
    - SPUTUM: Sputum Microscopy
    - PAP: Pap Smear
    - ECG: Electrocardiogram
    - CXR: Chest X-Ray
    - MAMMO: Mammogram (2024+)
    - UTZ: Ultrasound (2024+)
    """
    
    code = models.CharField(
        max_length=20,
        primary_key=True,
        help_text="PhilHealth laboratory exam code"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the laboratory test"
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Category (e.g., 'Hematology', 'Chemistry', 'Imaging')"
    )
    
    is_konsulta_covered = models.BooleanField(
        default=False,
        help_text="Is this test covered under Konsulta package?"
    )
    
    requires_fasting = models.BooleanField(
        default=False,
        help_text="Does this test require fasting?"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Additional information about the test"
    )
    
    class Meta:
        verbose_name = "Laboratory Exam Code"
        verbose_name_plural = "Laboratory Exam Codes"
        ordering = ['name']
    
    def __str__(self):
        covered = "✓" if self.is_konsulta_covered else ""
        return f"{self.code} - {self.name} {covered}"


class DrugCode(models.Model):
    """
    PhilHealth Essential Medicine Code Library (lib_drug)
    
    These codes are used to record:
    - Medicine prescriptions
    - Medicine dispensing (ESSENTIALMED)
    
    PhilHealth XML Reference:
    - pDrugCode: code field
    - pGenericName: generic_name
    - pBrandName: brand_name
    - pStrength: strength
    - pForm: form
    
    Konsulta Covered Medicine Categories:
    - Antimicrobials: Amoxicillin, Co-Amoxiclav, Cotrimoxazole, etc.
    - Anti-diabetics: Metformin, Gliclazide
    - Anti-hypertensives: Enalapril, Metoprolol, Amlodipine, etc.
    - Anti-asthma: Salbutamol, Prednisone, Fluticasone+Salmeterol
    - Anti-dyslipidemia: Simvastatin
    - Anti-thrombotic: Aspirin
    - Others: Paracetamol, Chlorpheniramine, ORS
    """
    
    code = models.CharField(
        max_length=20,
        primary_key=True,
        help_text="PhilHealth drug code"
    )
    
    generic_name = models.CharField(
        max_length=500,
        help_text="Generic name of the medicine"
    )
    
    brand_name = models.CharField(
        max_length=500,
        blank=True,
        help_text="Brand name (if applicable)"
    )
    
    category = models.CharField(
        max_length=100,
        help_text="Drug category (e.g., 'Antimicrobial', 'Anti-diabetic')"
    )
    
    strength = models.CharField(
        max_length=100,
        help_text="Dosage strength (e.g., '500mg', '10mg/5ml')"
    )
    
    form = models.CharField(
        max_length=100,
        help_text="Dosage form (e.g., 'Tablet', 'Capsule', 'Syrup')"
    )
    
    is_konsulta_covered = models.BooleanField(
        default=False,
        help_text="Is this medicine covered under Konsulta?"
    )
    
    class Meta:
        verbose_name = "Drug Code"
        verbose_name_plural = "Drug Codes"
        ordering = ['generic_name']
    
    def __str__(self):
        covered = "✓" if self.is_konsulta_covered else ""
        return f"{self.generic_name} {self.strength} ({self.form}) {covered}"


class DiagnosisCode(models.Model):
    """
    ICD-10 Diagnosis Codes
    
    International Classification of Diseases, 10th Revision
    Used for recording consultation diagnoses.
    
    PhilHealth requires ICD-10 codes for proper claims processing.
    
    Examples:
    - I10: Essential (primary) hypertension
    - E11.9: Type 2 diabetes mellitus without complications
    - J45.909: Unspecified asthma, uncomplicated
    - J06.9: Acute upper respiratory infection, unspecified
    """
    
    code = models.CharField(
        max_length=10,
        primary_key=True,
        help_text="ICD-10 diagnosis code"
    )
    
    description = models.CharField(
        max_length=500,
        help_text="Description of the diagnosis"
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="ICD-10 category/chapter"
    )
    
    class Meta:
        verbose_name = "Diagnosis Code (ICD-10)"
        verbose_name_plural = "Diagnosis Codes (ICD-10)"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.description}"
```

### 3.3 Loading Reference Data

You'll need to load the official PhilHealth codes. Create a management command:

**File: `philhealth/management/commands/load_philhealth_data.py`**

```python
"""
Management command to load PhilHealth reference data.

Usage:
    python manage.py load_philhealth_data

This loads:
- Disease codes (lib_mdisease)
- Laboratory exam codes (lib_labexam)
- Drug codes (lib_drug)
- Common ICD-10 diagnosis codes
"""

from django.core.management.base import BaseCommand
from philhealth.models import DiseaseCode, LaboratoryExamCode, DrugCode, DiagnosisCode


class Command(BaseCommand):
    help = 'Load PhilHealth reference data (disease codes, lab codes, drug codes)'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading PhilHealth reference data...')
        
        self.load_disease_codes()
        self.load_laboratory_codes()
        self.load_drug_codes()
        self.load_diagnosis_codes()
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded all reference data!'))
    
    def load_disease_codes(self):
        """Load common disease codes for medical/family history"""
        disease_codes = [
            # Cardiovascular
            ('HTN', 'Hypertension', 'Cardiovascular'),
            ('CAD', 'Coronary Artery Disease', 'Cardiovascular'),
            ('CHF', 'Congestive Heart Failure', 'Cardiovascular'),
            ('STROKE', 'Stroke/Cerebrovascular Disease', 'Cardiovascular'),
            ('AFIB', 'Atrial Fibrillation', 'Cardiovascular'),
            
            # Endocrine
            ('DM', 'Diabetes Mellitus', 'Endocrine'),
            ('DM1', 'Type 1 Diabetes Mellitus', 'Endocrine'),
            ('DM2', 'Type 2 Diabetes Mellitus', 'Endocrine'),
            ('THYROID', 'Thyroid Disease', 'Endocrine'),
            
            # Respiratory
            ('AST', 'Asthma', 'Respiratory'),
            ('COPD', 'Chronic Obstructive Pulmonary Disease', 'Respiratory'),
            ('TB', 'Tuberculosis', 'Respiratory'),
            ('PTB', 'Pulmonary Tuberculosis', 'Respiratory'),
            
            # Renal
            ('CKD', 'Chronic Kidney Disease', 'Renal'),
            ('ESRD', 'End-Stage Renal Disease', 'Renal'),
            
            # Gastrointestinal
            ('PUD', 'Peptic Ulcer Disease', 'Gastrointestinal'),
            ('GERD', 'Gastroesophageal Reflux Disease', 'Gastrointestinal'),
            ('HEP', 'Hepatitis', 'Gastrointestinal'),
            
            # Cancer
            ('CA', 'Cancer (specify)', 'Oncology'),
            ('BREAST_CA', 'Breast Cancer', 'Oncology'),
            ('LUNG_CA', 'Lung Cancer', 'Oncology'),
            ('COLON_CA', 'Colon Cancer', 'Oncology'),
            
            # Others
            ('ALLERGY', 'Allergies', 'Immunology'),
            ('ARTHRITIS', 'Arthritis', 'Musculoskeletal'),
            ('MENTAL', 'Mental Health Disorder', 'Psychiatry'),
            ('NONE', 'No Known Medical History', 'General'),
        ]
        
        created_count = 0
        for code, description, category in disease_codes:
            obj, created = DiseaseCode.objects.get_or_create(
                code=code,
                defaults={
                    'description': description,
                    'category': category,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  Disease codes: {created_count} created')
    
    def load_laboratory_codes(self):
        """Load Konsulta-covered laboratory exam codes"""
        lab_codes = [
            # Hematology
            ('CBC', 'Complete Blood Count with Platelet', 'Hematology', True, False),
            
            # Chemistry - Lipids
            ('LIPID', 'Lipid Profile', 'Chemistry', True, True),
            ('CHOL', 'Total Cholesterol', 'Chemistry', True, True),
            ('HDL', 'HDL Cholesterol', 'Chemistry', True, True),
            ('LDL', 'LDL Cholesterol', 'Chemistry', True, True),
            ('TRIG', 'Triglycerides', 'Chemistry', True, True),
            
            # Chemistry - Glucose
            ('FBS', 'Fasting Blood Sugar', 'Chemistry', True, True),
            ('RBS', 'Random Blood Sugar', 'Chemistry', False, False),
            ('OGTT', 'Oral Glucose Tolerance Test', 'Chemistry', True, True),
            ('HBA1C', 'Hemoglobin A1c', 'Chemistry', True, False),
            
            # Chemistry - Renal
            ('CREAT', 'Creatinine', 'Chemistry', True, False),
            ('BUN', 'Blood Urea Nitrogen', 'Chemistry', False, False),
            
            # Urinalysis/Fecalysis
            ('URINE', 'Urinalysis', 'Clinical Microscopy', True, False),
            ('FECAL', 'Fecalysis', 'Clinical Microscopy', True, False),
            ('FOBT', 'Fecal Occult Blood Test', 'Clinical Microscopy', True, False),
            
            # Microbiology
            ('SPUTUM', 'Sputum Microscopy', 'Microbiology', True, False),
            
            # Cytology
            ('PAP', 'Pap Smear', 'Cytology', True, False),
            
            # Imaging
            ('ECG', 'Electrocardiogram', 'Cardiac', True, False),
            ('CXR', 'Chest X-Ray', 'Radiology', True, False),
            ('MAMMO', 'Mammogram', 'Radiology', True, False),
            ('UTZ_ABD', 'Ultrasound - Abdomen', 'Radiology', True, False),
            ('UTZ_PELV', 'Ultrasound - Pelvic', 'Radiology', True, False),
            ('UTZ_BREAST', 'Ultrasound - Breast', 'Radiology', True, False),
        ]
        
        created_count = 0
        for code, name, category, is_covered, requires_fasting in lab_codes:
            obj, created = LaboratoryExamCode.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'category': category,
                    'is_konsulta_covered': is_covered,
                    'requires_fasting': requires_fasting
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  Laboratory codes: {created_count} created')
    
    def load_drug_codes(self):
        """Load Konsulta-covered essential medicines"""
        drug_codes = [
            # Antimicrobials
            ('AMX500', 'Amoxicillin', '', 'Antimicrobial', '500mg', 'Capsule', True),
            ('AMX250', 'Amoxicillin', '', 'Antimicrobial', '250mg/5ml', 'Suspension', True),
            ('COAMOX', 'Co-Amoxiclav', '', 'Antimicrobial', '625mg', 'Tablet', True),
            ('COTRI', 'Cotrimoxazole', '', 'Antimicrobial', '800mg/160mg', 'Tablet', True),
            ('NITRO', 'Nitrofurantoin', '', 'Antimicrobial', '100mg', 'Capsule', True),
            ('CIPRO', 'Ciprofloxacin', '', 'Antimicrobial', '500mg', 'Tablet', True),
            ('CLARI', 'Clarithromycin', '', 'Antimicrobial', '500mg', 'Tablet', True),
            
            # Anti-diabetics
            ('MET500', 'Metformin', '', 'Anti-diabetic', '500mg', 'Tablet', True),
            ('MET850', 'Metformin', '', 'Anti-diabetic', '850mg', 'Tablet', True),
            ('GLIC', 'Gliclazide', '', 'Anti-diabetic', '80mg', 'Tablet', True),
            
            # Anti-hypertensives
            ('ENAL', 'Enalapril', '', 'Anti-hypertensive', '10mg', 'Tablet', True),
            ('METO', 'Metoprolol', '', 'Anti-hypertensive', '50mg', 'Tablet', True),
            ('AMLO', 'Amlodipine', '', 'Anti-hypertensive', '5mg', 'Tablet', True),
            ('AMLO10', 'Amlodipine', '', 'Anti-hypertensive', '10mg', 'Tablet', True),
            ('HCTZ', 'Hydrochlorothiazide', '', 'Anti-hypertensive', '25mg', 'Tablet', True),
            ('LOSA', 'Losartan', '', 'Anti-hypertensive', '50mg', 'Tablet', True),
            ('LOSA100', 'Losartan', '', 'Anti-hypertensive', '100mg', 'Tablet', True),
            
            # Anti-asthma
            ('SALBU', 'Salbutamol', '', 'Anti-asthma', '2mg', 'Tablet', True),
            ('SALBU_NEB', 'Salbutamol', '', 'Anti-asthma', '2.5mg/2.5ml', 'Nebule', True),
            ('PRED', 'Prednisone', '', 'Anti-asthma', '5mg', 'Tablet', True),
            ('FLUSAL', 'Fluticasone + Salmeterol', '', 'Anti-asthma', '250mcg/50mcg', 'Inhaler', True),
            
            # Anti-dyslipidemia
            ('SIMVA', 'Simvastatin', '', 'Anti-dyslipidemia', '20mg', 'Tablet', True),
            ('SIMVA40', 'Simvastatin', '', 'Anti-dyslipidemia', '40mg', 'Tablet', True),
            
            # Anti-thrombotic
            ('ASA', 'Aspirin', '', 'Anti-thrombotic', '80mg', 'Tablet', True),
            
            # Antipyretic/Analgesic
            ('PARA500', 'Paracetamol', '', 'Antipyretic', '500mg', 'Tablet', True),
            ('PARA250', 'Paracetamol', '', 'Antipyretic', '250mg/5ml', 'Syrup', True),
            
            # Antihistamine
            ('CHLOR', 'Chlorpheniramine', '', 'Antihistamine', '4mg', 'Tablet', True),
            
            # Fluids
            ('ORS', 'Oral Rehydration Salts', '', 'Fluids', '27.9g/L', 'Powder', True),
        ]
        
        created_count = 0
        for code, generic, brand, category, strength, form, is_covered in drug_codes:
            obj, created = DrugCode.objects.get_or_create(
                code=code,
                defaults={
                    'generic_name': generic,
                    'brand_name': brand,
                    'category': category,
                    'strength': strength,
                    'form': form,
                    'is_konsulta_covered': is_covered
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  Drug codes: {created_count} created')
    
    def load_diagnosis_codes(self):
        """Load common ICD-10 diagnosis codes"""
        diagnosis_codes = [
            # Hypertension
            ('I10', 'Essential (primary) hypertension', 'Circulatory'),
            ('I11.9', 'Hypertensive heart disease without heart failure', 'Circulatory'),
            
            # Diabetes
            ('E11.9', 'Type 2 diabetes mellitus without complications', 'Endocrine'),
            ('E11.65', 'Type 2 diabetes mellitus with hyperglycemia', 'Endocrine'),
            ('E10.9', 'Type 1 diabetes mellitus without complications', 'Endocrine'),
            
            # Respiratory
            ('J06.9', 'Acute upper respiratory infection, unspecified', 'Respiratory'),
            ('J45.909', 'Unspecified asthma, uncomplicated', 'Respiratory'),
            ('J44.9', 'Chronic obstructive pulmonary disease, unspecified', 'Respiratory'),
            ('J20.9', 'Acute bronchitis, unspecified', 'Respiratory'),
            ('J00', 'Acute nasopharyngitis (common cold)', 'Respiratory'),
            
            # Gastrointestinal
            ('K29.70', 'Gastritis, unspecified, without bleeding', 'Digestive'),
            ('K21.0', 'Gastro-esophageal reflux with esophagitis', 'Digestive'),
            ('A09', 'Infectious gastroenteritis and colitis, unspecified', 'Digestive'),
            
            # Urinary
            ('N39.0', 'Urinary tract infection, site not specified', 'Genitourinary'),
            
            # Musculoskeletal
            ('M54.5', 'Low back pain', 'Musculoskeletal'),
            ('M25.50', 'Pain in unspecified joint', 'Musculoskeletal'),
            
            # Skin
            ('L30.9', 'Dermatitis, unspecified', 'Skin'),
            
            # General
            ('R50.9', 'Fever, unspecified', 'Symptoms'),
            ('R51', 'Headache', 'Symptoms'),
            ('R05', 'Cough', 'Symptoms'),
            
            # Preventive
            ('Z00.00', 'Encounter for general adult medical examination', 'Preventive'),
            ('Z23', 'Encounter for immunization', 'Preventive'),
        ]
        
        created_count = 0
        for code, description, category in diagnosis_codes:
            obj, created = DiagnosisCode.objects.get_or_create(
                code=code,
                defaults={
                    'description': description,
                    'category': category
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  Diagnosis codes: {created_count} created')
```

---

## STEP 4: PIN Validator

### 4.1 Understanding PhilHealth PIN

The **PhilHealth Identification Number (PIN)** is a 12-digit unique identifier for every PhilHealth member.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHILHEALTH PIN FORMAT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│         1  2  3  4  5  6  7  8  9  10  11  12                   │
│         ┴──┴──┴──┴──┴──┴──┴──┴──┴──┴───┴───┘                    │
│         │                          │    │                        │
│         │                          │    └── Check Digit          │
│         │                          │        (Mod-11)             │
│         │                          │                             │
│         └──────────────────────────┴── Unique Identifier         │
│                                        (11 digits)               │
│                                                                  │
│  Example: 01-234567890-1                                        │
│           └──┘ └──────┘ └── Check digit                         │
│             │      │                                             │
│             │      └── Sequence number                          │
│             └── Region code                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Mod-11 Check Digit Algorithm

The last digit is a **check digit** calculated using the Modulus-11 algorithm:

```
PIN: 0 1 2 3 4 5 6 7 8 9 0 ?
     × × × × × × × × × × ×
     11 10 9 8 7 6 5 4 3 2 1  (weights)
     ─────────────────────────
     = 0+10+18+24+28+30+30+28+24+18+0 = 210

210 ÷ 11 = 19 remainder 1
Check digit = 11 - 1 = 10 → Use 0 (special case)
```

### 4.3 The Validator Code

**File: `philhealth/validators.py`**

```python
"""
PhilHealth Validators

This module contains validation functions for PhilHealth-specific data:
- PhilHealth PIN (12-digit with mod-11 check)
- Authorization Transaction Code (ATC)
- Uppercase text validation
- Date format validation

These validators are used as Django field validators and can also
be called directly for manual validation.
"""

from django.core.exceptions import ValidationError
import re
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
# PHILHEALTH PIN VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_philhealth_pin(pin: str) -> str:
    """
    Validate PhilHealth Identification Number (PIN).
    
    Rules:
    1. Must be exactly 12 digits
    2. Last digit is a mod-11 check digit
    3. Only numeric characters allowed (dashes/spaces are stripped)
    
    Args:
        pin: The PhilHealth PIN to validate (can include dashes/spaces)
        
    Returns:
        str: The cleaned 12-digit PIN (no dashes/spaces)
        
    Raises:
        ValidationError: If the PIN is invalid
        
    Examples:
        >>> validate_philhealth_pin("01-234567890-1")
        "012345678901"
        >>> validate_philhealth_pin("123456789012")
        "123456789012"
        >>> validate_philhealth_pin("12345")  # Too short
        ValidationError: PhilHealth PIN must be exactly 12 digits
    """
    if not pin:
        raise ValidationError(
            "PhilHealth PIN is required.",
            code='required'
        )
    
    # Remove any spaces, dashes, or other separators
    cleaned_pin = re.sub(r'[\s\-]', '', str(pin))
    
    # Check length
    if len(cleaned_pin) != 12:
        raise ValidationError(
            f"PhilHealth PIN must be exactly 12 digits. "
            f"You entered {len(cleaned_pin)} digits.",
            code='invalid_length'
        )
    
    # Check if all digits
    if not cleaned_pin.isdigit():
        raise ValidationError(
            "PhilHealth PIN must contain only numbers.",
            code='invalid_characters'
        )
    
    # Validate mod-11 check digit
    if not _validate_mod11_check_digit(cleaned_pin):
        raise ValidationError(
            "Invalid PhilHealth PIN. The check digit does not match. "
            "Please verify the PIN is correct.",
            code='invalid_check_digit'
        )
    
    return cleaned_pin


def _validate_mod11_check_digit(pin: str) -> bool:
    """
    Validate the mod-11 check digit of a PhilHealth PIN.
    
    Algorithm:
    1. Take the first 11 digits
    2. Multiply each digit by a weight (11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)
    3. Sum all the products
    4. Calculate: sum mod 11
    5. Check digit = 11 - remainder (or 0 if remainder is 0 or 1)
    
    Args:
        pin: 12-digit PIN string
        
    Returns:
        bool: True if check digit is valid, False otherwise
    """
    try:
        # Weights for mod-11 calculation (positions 1-11)
        weights = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        
        # Get first 11 digits
        digits = [int(d) for d in pin[:11]]
        
        # Calculate weighted sum
        weighted_sum = sum(d * w for d, w in zip(digits, weights))
        
        # Calculate remainder
        remainder = weighted_sum % 11
        
        # Determine expected check digit
        if remainder == 0:
            expected_check = 0
        elif remainder == 1:
            # Special case: some implementations use 0, others use X
            # PhilHealth typically uses 0 for this case
            expected_check = 0
        else:
            expected_check = 11 - remainder
        
        # Get actual check digit (12th digit)
        actual_check = int(pin[11])
        
        return actual_check == expected_check
        
    except (ValueError, IndexError):
        return False


def generate_pin_check_digit(pin_11: str) -> str:
    """
    Generate the check digit for an 11-digit PIN base.
    
    This is useful for testing or generating valid PINs.
    
    Args:
        pin_11: First 11 digits of the PIN
        
    Returns:
        str: Complete 12-digit PIN with check digit
        
    Example:
        >>> generate_pin_check_digit("01234567890")
        "012345678901"
    """
    if len(pin_11) != 11 or not pin_11.isdigit():
        raise ValueError("Input must be exactly 11 digits")
    
    weights = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    digits = [int(d) for d in pin_11]
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    remainder = weighted_sum % 11
    
    if remainder == 0 or remainder == 1:
        check_digit = 0
    else:
        check_digit = 11 - remainder
    
    return pin_11 + str(check_digit)


# ═══════════════════════════════════════════════════════════════════════════
# ATC (AUTHORIZATION TRANSACTION CODE) VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_atc(atc: str) -> str:
    """
    Validate Authorization Transaction Code (ATC).
    
    Rules:
    1. Must be exactly 10 characters, OR
    2. Must be 'WALKEDIN' for walk-in patients
    
    The ATC is required before a patient can avail Konsulta services.
    It can be generated via:
    - PhilHealth Member Portal
    - LHIO Office
    - PhilHealth Hotline
    - Walk-in at facility (use 'WALKEDIN')
    
    Args:
        atc: The ATC to validate
        
    Returns:
        str: The validated ATC (uppercase)
        
    Raises:
        ValidationError: If ATC is invalid
    """
    if not atc:
        raise ValidationError(
            "Authorization Transaction Code (ATC) is required.",
            code='required'
        )
    
    # Clean and uppercase
    cleaned_atc = atc.strip().upper()
    
    # Special case: Walk-in patients
    if cleaned_atc == 'WALKEDIN':
        return 'WALKEDIN'
    
    # Normal ATC: exactly 10 characters
    if len(cleaned_atc) != 10:
        raise ValidationError(
            f"ATC must be exactly 10 characters or 'WALKEDIN'. "
            f"You entered {len(cleaned_atc)} characters.",
            code='invalid_length'
        )
    
    # ATC should be alphanumeric
    if not cleaned_atc.isalnum():
        raise ValidationError(
            "ATC must contain only letters and numbers.",
            code='invalid_characters'
        )
    
    return cleaned_atc


def is_walk_in(atc: str) -> bool:
    """
    Check if the ATC indicates a walk-in patient.
    
    Args:
        atc: The ATC value
        
    Returns:
        bool: True if walk-in, False otherwise
    """
    return atc and atc.strip().upper() == 'WALKEDIN'


# ═══════════════════════════════════════════════════════════════════════════
# TEXT VALIDATION (UPPERCASE REQUIREMENT)
# ═══════════════════════════════════════════════════════════════════════════

def validate_uppercase(value: str) -> str:
    """
    Convert text to uppercase.
    
    PhilHealth requires all text data (names, addresses, etc.) 
    to be in UPPERCASE format.
    
    Args:
        value: Text to convert
        
    Returns:
        str: Uppercase text, or empty string if None
    """
    if value:
        return value.upper().strip()
    return ''


def ensure_uppercase_field(value: Optional[str], field_name: str) -> str:
    """
    Validate and convert a field to uppercase with error context.
    
    Args:
        value: The field value
        field_name: Name of the field (for error messages)
        
    Returns:
        str: Uppercase value
    """
    if not value:
        return ''
    
    converted = value.upper().strip()
    
    # Check for special characters that shouldn't be in names
    if field_name in ['first_name', 'last_name', 'middle_name']:
        # Allow letters, spaces, hyphens, periods, apostrophes
        if not re.match(r'^[A-Z\s\-\.\'\ñÑ]+$', converted, re.UNICODE):
            raise ValidationError(
                f"{field_name.replace('_', ' ').title()} contains invalid characters. "
                f"Only letters, spaces, hyphens, periods, and apostrophes are allowed.",
                code='invalid_characters'
            )
    
    return converted


# ═══════════════════════════════════════════════════════════════════════════
# DATE FORMAT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_date_format(date_str: str, expected_format: str = '%Y-%m-%d') -> bool:
    """
    Validate that a date string matches the expected format.
    
    PhilHealth uses YYYY-MM-DD format for dates.
    
    Args:
        date_str: Date string to validate
        expected_format: Expected format (default: YYYY-MM-DD)
        
    Returns:
        bool: True if valid, False otherwise
    """
    from datetime import datetime
    
    try:
        datetime.strptime(date_str, expected_format)
        return True
    except (ValueError, TypeError):
        return False


# ═══════════════════════════════════════════════════════════════════════════
# PATIENT TYPE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_patient_type(patient_type: str) -> str:
    """
    Validate patient type code.
    
    Valid values:
    - 'MM': Member (principal PhilHealth member)
    - 'DD': Dependent (dependent of a member)
    
    Args:
        patient_type: The patient type code
        
    Returns:
        str: Validated patient type (uppercase)
        
    Raises:
        ValidationError: If invalid
    """
    if not patient_type:
        raise ValidationError(
            "Patient type is required.",
            code='required'
        )
    
    cleaned = patient_type.strip().upper()
    
    if cleaned not in ['MM', 'DD']:
        raise ValidationError(
            f"Invalid patient type '{cleaned}'. "
            f"Must be 'MM' (Member) or 'DD' (Dependent).",
            code='invalid_choice'
        )
    
    return cleaned


# ═══════════════════════════════════════════════════════════════════════════
# REPORT STATUS VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_report_status(status: str) -> str:
    """
    Validate PhilHealth report status code.
    
    Valid values:
    - 'U': Unvalidated (default, not yet sent to PhilHealth)
    - 'V': Validated (passed PhilHealth validation)
    - 'F': Failed (failed PhilHealth validation)
    
    Args:
        status: The status code
        
    Returns:
        str: Validated status code (uppercase)
        
    Raises:
        ValidationError: If invalid
    """
    if not status:
        return 'U'  # Default to Unvalidated
    
    cleaned = status.strip().upper()
    
    if cleaned not in ['U', 'V', 'F']:
        raise ValidationError(
            f"Invalid report status '{cleaned}'. "
            f"Must be 'U' (Unvalidated), 'V' (Validated), or 'F' (Failed).",
            code='invalid_choice'
        )
    
    return cleaned
```

---

## STEP 5: AES-256-CBC Encryption Module

### 5.1 Why Encryption is Required

PhilHealth mandates that ALL XML data sent to and received from their API must be encrypted using **AES-256-CBC** (Advanced Encryption Standard, 256-bit key, Cipher Block Chaining mode).

```
┌─────────────────────────────────────────────────────────────────┐
│               ENCRYPTION FLOW FOR PHILHEALTH                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  YOUR SYSTEM                              PHILHEALTH PKA        │
│  ──────────                               ──────────────        │
│                                                                  │
│  1. Generate Raw XML                                             │
│     │                                                            │
│     ▼                                                            │
│  2. Compute SHA-256 Hash ─────────────────────────┐             │
│     │                                              │             │
│     ▼                                              │             │
│  3. Generate Random IV (16 bytes)                  │             │
│     │                                              │             │
│     ▼                                              │             │
│  4. Encrypt with AES-256-CBC ───┐                 │             │
│     │                           │                  │             │
│     ▼                           ▼                  ▼             │
│  5. Build JSON Payload:   {"doc": "...", "iv": "...", "hash": "..."}
│     │                                                            │
│     ▼                                                            │
│  6. Send to PhilHealth ────────────────────────────────────────►│
│                                                                  │
│                          ◄──────────────────────────────────────│
│                                                                  │
│  7. Receive Encrypted Response                                   │
│     │                                                            │
│     ▼                                                            │
│  8. Parse JSON, Decode Base64                                    │
│     │                                                            │
│     ▼                                                            │
│  9. Decrypt with AES-256-CBC                                     │
│     │                                                            │
│     ▼                                                            │
│  10. Verify Hash ─────────────────────────────────┘             │
│     │                                                            │
│     ▼                                                            │
│  11. Process XML Response                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 The Encrypted JSON Format

PhilHealth expects/returns encrypted data in this JSON structure:

```json
{
    "docMimeType": "text/xml",
    "hash": "a1b2c3d4e5f6...",      // SHA-256 hash of original XML
    "key1": "",                      // Reserved (empty)
    "key2": "",                      // Reserved (empty)
    "iv": "Base64EncodedIV...",     // Initialization Vector
    "doc": "Base64EncodedData..."   // Encrypted XML data
}
```

### 5.3 The Encryption Module Code

**File: `philhealth/encryption.py`**

```python
"""
PhilHealth XML Encryption Module

This module handles encryption and decryption of XML payloads for 
the PhilHealth Konsulta API (PKA).

Encryption Specification:
- Algorithm: AES-256-CBC
- Key: SHA-256 hash of cipher key (first 32 bytes)
- IV: Random 16 bytes (128 bits)
- Padding: PKCS7
- Output: JSON with Base64-encoded encrypted data

IMPORTANT: 
- The cipher key is unique per Healthcare Institution (HCI)
- It is provided by PhilHealth after software certification
- NEVER log or expose the cipher key

Requirements:
    pip install pycryptodome

Usage:
    from philhealth.encryption import PhilHealthEncryption
    
    # Initialize with your facility's cipher key
    encryptor = PhilHealthEncryption("your-cipher-key-from-philhealth")
    
    # Encrypt XML for submission
    encrypted_json = encryptor.encrypt_xml(raw_xml_string)
    
    # Decrypt response from PhilHealth
    decrypted_xml, is_valid = encryptor.decrypt_xml(encrypted_json_response)
"""

import json
import base64
import hashlib
import os
import logging
from typing import Tuple, Optional

# PyCryptodome library for AES encryption
# Install: pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

logger = logging.getLogger(__name__)


class PhilHealthEncryptionError(Exception):
    """Custom exception for encryption/decryption errors"""
    pass


class PhilHealthEncryption:
    """
    Handles AES-256-CBC encryption/decryption for PhilHealth PKA.
    
    This class implements the encryption specification required by
    PhilHealth for all XML data exchange.
    
    Attributes:
        cipher_key (str): The passphrase provided by PhilHealth
        
    Example:
        >>> encryptor = PhilHealthEncryption("my-secret-key")
        >>> encrypted = encryptor.encrypt_xml("<PCB>...</PCB>")
        >>> decrypted, valid = encryptor.decrypt_xml(encrypted)
    """
    
    # AES block size is always 16 bytes (128 bits)
    BLOCK_SIZE = 16
    
    # Key size for AES-256 is 32 bytes (256 bits)
    KEY_SIZE = 32
    
    def __init__(self, cipher_key: str):
        """
        Initialize the encryption handler.
        
        Args:
            cipher_key: The passphrase/password provided by PhilHealth 
                       for this Healthcare Institution. This is unique
                       per facility.
                       
        Raises:
            PhilHealthEncryptionError: If cipher_key is empty
        """
        if not cipher_key:
            raise PhilHealthEncryptionError(
                "Cipher key is required for PhilHealth encryption"
            )
        
        self.cipher_key = cipher_key
        self._derived_key = self._derive_key(cipher_key)
        
        logger.debug("PhilHealth encryption initialized")
    
    def _derive_key(self, cipher_key: str) -> bytes:
        """
        Derive AES key from cipher key using SHA-256.
        
        The PhilHealth specification requires:
        1. Hash the cipher key using SHA-256
        2. Use the first 32 bytes as the AES key
        3. If hash is less than 32 bytes, pad with 0x00
        
        Note: SHA-256 always produces 32 bytes, so padding is
        technically not needed, but included for spec compliance.
        
        Args:
            cipher_key: The original passphrase
            
        Returns:
            bytes: 32-byte AES key
        """
        # Encode cipher key to bytes
        key_bytes = cipher_key.encode('utf-8')
        
        # Compute SHA-256 hash
        key_hash = hashlib.sha256(key_bytes).digest()
        
        # Ensure exactly 32 bytes (pad if needed)
        if len(key_hash) < self.KEY_SIZE:
            key_hash = key_hash + b'\x00' * (self.KEY_SIZE - len(key_hash))
        
        return key_hash[:self.KEY_SIZE]
    
    def encrypt_xml(self, xml_data: str) -> str:
        """
        Encrypt XML payload for PhilHealth submission.
        
        Process:
        1. Compute SHA-256 hash of raw XML (for integrity verification)
        2. Generate random 16-byte IV (Initialization Vector)
        3. Pad XML data using PKCS7
        4. Encrypt using AES-256-CBC
        5. Encode IV and encrypted data as Base64
        6. Build JSON response
        
        Args:
            xml_data: Raw XML string to encrypt
            
        Returns:
            str: JSON string containing encrypted data:
                {
                    "docMimeType": "text/xml",
                    "hash": "<SHA-256 of raw XML>",
                    "key1": "",
                    "key2": "",
                    "iv": "<Base64 IV>",
                    "doc": "<Base64 encrypted data>"
                }
                
        Raises:
            PhilHealthEncryptionError: If encryption fails
        """
        try:
            # Step 1: Convert XML to bytes
            xml_bytes = xml_data.encode('utf-8')
            
            # Step 2: Compute SHA-256 hash for integrity verification
            xml_hash = hashlib.sha256(xml_bytes).hexdigest()
            logger.debug(f"XML hash computed: {xml_hash[:16]}...")
            
            # Step 3: Generate random IV (16 bytes for AES)
            iv = os.urandom(self.BLOCK_SIZE)
            
            # Step 4: Pad the data using PKCS7
            padded_data = pad(xml_bytes, self.BLOCK_SIZE)
            
            # Step 5: Create AES cipher and encrypt
            cipher = AES.new(self._derived_key, AES.MODE_CBC, iv)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Step 6: Encode to Base64
            iv_b64 = base64.b64encode(iv).decode('utf-8')
            data_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            # Step 7: Build JSON response
            result = {
                "docMimeType": "text/xml",
                "hash": xml_hash,
                "key1": "",  # Reserved, keep empty
                "key2": "",  # Reserved, keep empty
                "iv": iv_b64,
                "doc": data_b64
            }
            
            logger.info("XML encryption successful")
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise PhilHealthEncryptionError(f"Failed to encrypt XML: {str(e)}")
    
    def decrypt_xml(self, encrypted_json: str) -> Tuple[str, bool]:
        """
        Decrypt XML payload from PhilHealth response.
        
        Process:
        1. Parse JSON response
        2. Decode IV and encrypted data from Base64
        3. Decrypt using AES-256-CBC
        4. Remove PKCS7 padding
        5. Compute hash and verify integrity
        
        Args:
            encrypted_json: JSON string with encrypted data
            
        Returns:
            Tuple[str, bool]: (decrypted_xml, integrity_verified)
            - decrypted_xml: The original XML string
            - integrity_verified: True if hash matches
            
        Raises:
            PhilHealthEncryptionError: If decryption fails
        """
        try:
            # Step 1: Parse JSON
            data = json.loads(encrypted_json)
            
            # Validate required fields
            required_fields = ['iv', 'doc']
            for field in required_fields:
                if field not in data:
                    raise PhilHealthEncryptionError(
                        f"Missing required field: {field}"
                    )
            
            # Step 2: Decode from Base64
            iv = base64.b64decode(data['iv'])
            encrypted_data = base64.b64decode(data['doc'])
            
            # Validate IV length
            if len(iv) != self.BLOCK_SIZE:
                raise PhilHealthEncryptionError(
                    f"Invalid IV length: {len(iv)} (expected {self.BLOCK_SIZE})"
                )
            
            # Step 3: Create cipher and decrypt
            cipher = AES.new(self._derived_key, AES.MODE_CBC, iv)
            decrypted_padded = cipher.decrypt(encrypted_data)
            
            # Step 4: Remove padding
            decrypted_data = unpad(decrypted_padded, self.BLOCK_SIZE)
            
            # Step 5: Convert to string
            xml_string = decrypted_data.decode('utf-8')
            
            # Step 6: Verify integrity (if hash provided)
            integrity_verified = True
            if 'hash' in data and data['hash']:
                computed_hash = hashlib.sha256(decrypted_data).hexdigest()
                integrity_verified = (computed_hash == data['hash'])
                
                if not integrity_verified:
                    logger.warning(
                        "Integrity check failed! "
                        f"Expected: {data['hash'][:16]}... "
                        f"Got: {computed_hash[:16]}..."
                    )
            
            logger.info(f"XML decryption successful (integrity: {integrity_verified})")
            return xml_string, integrity_verified
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            raise PhilHealthEncryptionError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise PhilHealthEncryptionError(f"Failed to decrypt XML: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def encrypt_xml_payload(xml_data: str, cipher_key: str) -> str:
    """
    Convenience function to encrypt XML.
    
    Args:
        xml_data: Raw XML string
        cipher_key: PhilHealth-provided cipher key
        
    Returns:
        str: JSON with encrypted data
    """
    encryptor = PhilHealthEncryption(cipher_key)
    return encryptor.encrypt_xml(xml_data)


def decrypt_xml_payload(encrypted_json: str, cipher_key: str) -> Tuple[str, bool]:
    """
    Convenience function to decrypt XML.
    
    Args:
        encrypted_json: JSON with encrypted data
        cipher_key: PhilHealth-provided cipher key
        
    Returns:
        Tuple[str, bool]: (decrypted_xml, integrity_verified)
    """
    encryptor = PhilHealthEncryption(cipher_key)
    return encryptor.decrypt_xml(encrypted_json)


# ═══════════════════════════════════════════════════════════════════════════
# TESTING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def test_encryption_roundtrip(test_xml: Optional[str] = None) -> bool:
    """
    Test that encryption/decryption works correctly.
    
    Args:
        test_xml: Optional XML to test with
        
    Returns:
        bool: True if test passes
    """
    if test_xml is None:
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <PCB>
            <pHciAccreNo>123456789</pHciAccreNo>
            <ENLISTMENT>
                <pMemPin>012345678901</pMemPin>
                <pMemFname>JUAN</pMemFname>
                <pMemLname>DELA CRUZ</pMemLname>
            </ENLISTMENT>
        </PCB>"""
    
    test_key = "test-cipher-key-for-validation"
    
    try:
        # Encrypt
        encrypted = encrypt_xml_payload(test_xml, test_key)
        print(f"✓ Encryption successful")
        print(f"  Encrypted JSON length: {len(encrypted)} bytes")
        
        # Decrypt
        decrypted, integrity = decrypt_xml_payload(encrypted, test_key)
        print(f"✓ Decryption successful")
        print(f"  Integrity verified: {integrity}")
        
        # Verify content matches
        # Note: We compare stripped versions to handle whitespace differences
        original_stripped = ''.join(test_xml.split())
        decrypted_stripped = ''.join(decrypted.split())
        
        if original_stripped == decrypted_stripped:
            print(f"✓ Content matches")
            return True
        else:
            print(f"✗ Content mismatch!")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run test when module is executed directly
    print("Testing PhilHealth Encryption Module...")
    print("=" * 50)
    test_encryption_roundtrip()
```

---

## STEP 6: Create Migrations and Test

### 6.1 Create Migrations

```bash
# Create migrations for the philhealth app
python manage.py makemigrations philhealth

# Review the migration file
# It should create: HealthCareInstitution, DiseaseCode, 
# LaboratoryExamCode, DrugCode, DiagnosisCode

# Apply migrations
python manage.py migrate
```

### 6.2 Load Reference Data

```bash
# Load PhilHealth reference data (disease codes, lab codes, drug codes)
python manage.py load_philhealth_data
```

### 6.3 Test in Django Shell

```bash
python manage.py shell
```

```python
# Test PIN validation
from philhealth.validators import validate_philhealth_pin, generate_pin_check_digit

# Generate a valid PIN
valid_pin = generate_pin_check_digit("01234567890")
print(f"Generated PIN: {valid_pin}")  # Should be 012345678901

# Validate it
try:
    result = validate_philhealth_pin(valid_pin)
    print(f"Valid PIN: {result}")
except Exception as e:
    print(f"Error: {e}")

# Test invalid PIN
try:
    validate_philhealth_pin("123456789999")  # Invalid check digit
except Exception as e:
    print(f"Expected error: {e}")
```

```python
# Test encryption
from philhealth.encryption import test_encryption_roundtrip

# Run the encryption test
test_encryption_roundtrip()
```

```python
# Test HCI model
from philhealth.models import HealthCareInstitution

# Create a test facility
hci = HealthCareInstitution.objects.create(
    accreditation_number="123456789",
    pmcc_number="123456",
    name="Test Medical Clinic",
    address="123 Test Street, Test City"
)

# Generate some IDs
print(f"Case No: {hci.get_next_case_number()}")
print(f"Enlistment No: {hci.get_next_enlistment_number()}")
print(f"Profile No: {hci.get_next_profile_number()}")
```

---

## Phase 1 Checklist

### Files to Create

| File | Purpose | Status |
|------|---------|--------|
| `philhealth/__init__.py` | App initialization | □ |
| `philhealth/admin.py` | Admin interface | □ |
| `philhealth/apps.py` | App configuration | □ |
| `philhealth/models.py` | HCI, Reference Libraries | □ |
| `philhealth/validators.py` | PIN, ATC validation | □ |
| `philhealth/encryption.py` | AES-256-CBC encryption | □ |
| `philhealth/management/commands/load_philhealth_data.py` | Data loader | □ |

### Settings to Update

| Setting | Change | Status |
|---------|--------|--------|
| `INSTALLED_APPS` | Add `'philhealth'` | □ |

### Dependencies to Install

```bash
pip install pycryptodome
```

### Tests to Run

| Test | Expected Result | Status |
|------|-----------------|--------|
| PIN validation | Valid PIN passes, invalid fails | □ |
| Encryption roundtrip | Encrypt → Decrypt = Original | □ |
| HCI ID generation | Proper format (T/E/P/S/R prefix) | □ |
| Reference data load | Disease, Lab, Drug codes loaded | □ |

---

## What's Next?

After completing Phase 1, you'll have:
- ✅ PhilHealth app structure
- ✅ Healthcare Institution model (your facility)
- ✅ Reference code libraries
- ✅ PIN and ATC validators
- ✅ AES-256-CBC encryption

**Phase 2** will enhance your existing models (Patient, Consultation) with PhilHealth-specific fields.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'Crypto'"
```bash
pip install pycryptodome
```

### "Invalid PIN (check digit failed)"
- Verify the PIN is exactly 12 digits
- Check if there are leading zeros that were stripped
- Use `generate_pin_check_digit()` to create test PINs

### "Migration errors"
```bash
# Reset migrations if needed
python manage.py migrate philhealth zero
python manage.py makemigrations philhealth
python manage.py migrate
```

---

*Phase 1 Complete - Proceed to Phase 2: Enhance Existing Models*
