# PhilHealth eKonsulta Implementation
# PHASE 2: Enhance Existing Models

---

## Phase Overview

| Attribute | Details |
|-----------|---------|
| **Phase Number** | 2 of 5 |
| **Duration** | 1-2 Weeks |
| **Priority** | 🔴 Critical - Patient & Clinical Data |
| **Dependencies** | Phase 1 (PhilHealth Core Module) |
| **Outcome** | Existing models enhanced for PhilHealth compliance |

---

## What You'll Modify in This Phase

This phase enhances your EXISTING models without breaking current functionality:

| App | Model | Changes |
|-----|-------|---------|
| **secretary** | Patient | Add PIN, patient_type, member link, middle_name, suffix |
| **secretary** | Appointment | Add ATC field, is_walked_in flag |
| **doctor** | Consultation | Add SOAP fields, hci_trans_no, enlistment link |
| **doctor** | Medicine | Add PhilHealth drug code link |
| **doctor** | Prescription | Add dispensing tracking fields |
| **login** | DoctorProfile | Add PhilHealth accreditation number |

---

## STEP 1: Enhance Patient Model (secretary/models.py)

### 1.1 What We're Adding

```
┌─────────────────────────────────────────────────────────────────┐
│                 PATIENT MODEL ENHANCEMENTS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  EXISTING FIELDS          NEW PHILHEALTH FIELDS                 │
│  ───────────────          ─────────────────────                 │
│  • first_name             • philhealth_pin (12 digits)          │
│  • last_name              • patient_type (MM/DD)                │
│  • birth_date             • member (FK to self for dependents)  │
│  • gender                 • relationship_code (S/C/P)           │
│  • contact_number         • middle_name                         │
│  • email                  • suffix (Jr., Sr., III)              │
│  • address                • photo (for identification)          │
│  • medical_history        • photo_consent                       │
│  • created_at             • facility (FK to HCI)                │
│                           • updated_at                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 The Enhanced Patient Model

**File: `secretary/models.py`** - Replace your Patient class with this:

```python
from django.db import models
from django.conf import settings
import uuid
import os

# Import PhilHealth validators (from Phase 1)
from philhealth.validators import validate_philhealth_pin, validate_uppercase


def document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4()}{ext}"
    return f"patient_documents/{random_filename}"


def picture_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4()}{ext}"
    return f"patient_pictures/{random_filename}"


def patient_photo_path(instance, filename):
    """Generate path for patient identification photo"""
    ext = os.path.splitext(filename)[1]
    return f"patient_photos/{uuid.uuid4()}{ext}"


class Patient(models.Model):
    """
    Patient model - Enhanced for PhilHealth Konsulta compliance.
    
    Represents a patient who can receive Konsulta services.
    Can be either:
    - Member (MM): Primary PhilHealth member
    - Dependent (DD): Dependent of a member (spouse, child, parent)
    
    PhilHealth XML Mapping:
    - pMemPin/pDepPin → philhealth_pin
    - pMemFname/pDepFname → first_name (UPPERCASE)
    - pMemMname/pDepMname → middle_name (UPPERCASE)
    - pMemLname/pDepLname → last_name (UPPERCASE)
    - pMemSuffix → suffix
    - pMemBdate/pDepBdate → birth_date
    - pMemSex/pDepSex → gender
    - pRelCode → relationship_code
    """
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    PATIENT_TYPE_CHOICES = [
        ('MM', 'Member'),
        ('DD', 'Dependent'),
    ]
    
    RELATIONSHIP_CHOICES = [
        ('S', 'Spouse'),
        ('C', 'Child'),
        ('P', 'Parent'),
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # EXISTING FIELDS (Modified for PhilHealth compatibility)
    # ═══════════════════════════════════════════════════════════════
    
    first_name = models.CharField(
        max_length=100,
        help_text="First name (will be saved as UPPERCASE)"
    )
    
    last_name = models.CharField(
        max_length=100,
        help_text="Last name (will be saved as UPPERCASE)"
    )
    
    birth_date = models.DateField(
        help_text="Date of birth"
    )
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        help_text="M=Male, F=Female"
    )
    
    contact_number = models.CharField(
        max_length=15,
        help_text="Mobile or landline number"
    )
    
    email = models.EmailField(
        blank=True,
        null=True
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Complete address"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Keep for backward compatibility (new structured history in Profile model)
    medical_history = models.TextField(
        blank=True,
        null=True,
        help_text="Legacy field - use Profile.medical_history for new records"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # NEW PHILHEALTH FIELDS
    # ═══════════════════════════════════════════════════════════════
    
    philhealth_pin = models.CharField(
        max_length=12,
        unique=True,
        null=True,      # Nullable for existing records
        blank=True,     # Can be blank initially
        validators=[validate_philhealth_pin],
        help_text="12-digit PhilHealth Identification Number"
    )
    
    patient_type = models.CharField(
        max_length=2,
        choices=PATIENT_TYPE_CHOICES,
        default='MM',
        help_text="MM=Member (principal), DD=Dependent"
    )
    
    # Self-referential FK: If patient is a dependent, link to their member
    member = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependents',
        help_text="If dependent, link to the primary member"
    )
    
    relationship_code = models.CharField(
        max_length=1,
        choices=RELATIONSHIP_CHOICES,
        blank=True,
        help_text="Relationship to member: S=Spouse, C=Child, P=Parent"
    )
    
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Middle name (will be saved as UPPERCASE)"
    )
    
    suffix = models.CharField(
        max_length=10,
        blank=True,
        help_text="Suffix: Jr., Sr., III, etc."
    )
    
    photo = models.ImageField(
        upload_to=patient_photo_path,
        blank=True,
        null=True,
        help_text="Patient photo for identification"
    )
    
    photo_consent = models.BooleanField(
        default=False,
        help_text="Patient consent for photo capture"
    )
    
    facility = models.ForeignKey(
        'philhealth.HealthCareInstitution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients',
        help_text="Primary healthcare facility"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
    
    def __str__(self):
        pin_display = self.philhealth_pin or "No PIN"
        return f"{self.last_name}, {self.first_name} ({pin_display})"
    
    def save(self, *args, **kwargs):
        """
        Override save to:
        1. Convert names to UPPERCASE (PhilHealth requirement)
        2. Validate dependent has a member linked
        """
        # Convert to UPPERCASE
        self.first_name = validate_uppercase(self.first_name)
        self.last_name = validate_uppercase(self.last_name)
        self.middle_name = validate_uppercase(self.middle_name) if self.middle_name else ''
        
        # Validate dependent relationship
        if self.patient_type == 'DD' and not self.member:
            # Warning: In production, you might want to raise an error
            pass  # Allow for now during migration
        
        super().save(*args, **kwargs)
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER PROPERTIES
    # ═══════════════════════════════════════════════════════════════
    
    @property
    def full_name(self) -> str:
        """Return full name in format: FIRST MIDDLE LAST SUFFIX"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return ' '.join(parts)
    
    @property
    def age(self) -> int:
        """Calculate current age"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    @property
    def member_pin(self) -> str:
        """
        Return the member's PIN.
        - If this is a member: return their own PIN
        - If this is a dependent: return their linked member's PIN
        """
        if self.patient_type == 'MM':
            return self.philhealth_pin
        elif self.member:
            return self.member.philhealth_pin
        return None
    
    @property
    def is_konsulta_eligible(self) -> bool:
        """Check if patient has required PhilHealth data"""
        return bool(self.philhealth_pin)
    
    def get_active_enlistment(self, year: str = None):
        """Get the patient's active enlistment for a given year"""
        from philhealth.models import Enlistment
        from django.utils import timezone
        
        if year is None:
            year = str(timezone.now().year)
        
        return self.enlistments.filter(
            effectivity_year=year,
            enlistment_status='1'  # Active
        ).first()


# ═══════════════════════════════════════════════════════════════════════════
# KEEP YOUR EXISTING MODELS BELOW (PatientDocument, PatientPicture)
# ═══════════════════════════════════════════════════════════════════════════

class PatientDocument(models.Model):
    """Patient medical record documents (keep as-is)"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to=document_upload_path)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.patient} - {self.description or 'No description'}"


class PatientPicture(models.Model):
    """Patient pictures (keep as-is)"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pictures')
    picture = models.ImageField(upload_to=picture_upload_path)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture for {self.patient} - {self.caption or 'No caption'}"
```

### 1.3 How the Member-Dependent Relationship Works

```python
# Example: Creating a member and their dependents

# Create the member (principal PhilHealth holder)
member = Patient.objects.create(
    first_name="JUAN",
    last_name="DELA CRUZ",
    middle_name="SANTOS",
    birth_date="1980-01-15",
    gender="M",
    contact_number="09171234567",
    philhealth_pin="012345678901",
    patient_type="MM"  # Member
)

# Create spouse as dependent
spouse = Patient.objects.create(
    first_name="MARIA",
    last_name="DELA CRUZ",
    middle_name="REYES",
    birth_date="1982-05-20",
    gender="F",
    contact_number="09171234567",
    philhealth_pin="012345678902",
    patient_type="DD",  # Dependent
    member=member,      # Link to the member
    relationship_code="S"  # Spouse
)

# Create child as dependent
child = Patient.objects.create(
    first_name="PEDRO",
    last_name="DELA CRUZ",
    birth_date="2010-03-10",
    gender="M",
    contact_number="09171234567",
    philhealth_pin="012345678903",
    patient_type="DD",  # Dependent
    member=member,      # Link to the member
    relationship_code="C"  # Child
)

# Query: Get all dependents of a member
dependents = member.dependents.all()
print(f"Juan has {dependents.count()} dependents")

# Query: Get the member of a dependent
print(f"Pedro's member PIN: {child.member_pin}")  # Returns Juan's PIN
```

---

## STEP 2: Enhance Appointment Model

### 2.1 What We're Adding

The Appointment model needs an **ATC (Authorization Transaction Code)** field. Before a patient can receive Konsulta services, they must have a valid ATC.

```
┌─────────────────────────────────────────────────────────────────┐
│                APPOINTMENT MODEL ENHANCEMENTS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  NEW FIELDS:                                                     │
│  • atc - Authorization Transaction Code (10 chars or WALKEDIN)  │
│  • is_walked_in - Boolean flag for walk-in patients             │
│  • created_at - Timestamp for tracking                          │
│                                                                  │
│  ATC SOURCES:                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. PhilHealth Member Portal (online)                    │    │
│  │ 2. LHIO Office (in person)                              │    │
│  │ 3. PCARES Staff at facility                             │    │
│  │ 4. PhilHealth Hotline: (02) 8441-7442                  │    │
│  │ 5. Walk-in at facility → use "WALKEDIN"                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Enhanced Appointment Model

**File: `secretary/models.py`** - Update your Appointment class:

```python
class Appointment(models.Model):
    """
    Appointment model - Enhanced for PhilHealth Konsulta.
    
    Each appointment requires an ATC (Authorization Transaction Code)
    for PhilHealth Konsulta claims. Walk-in patients use "WALKEDIN".
    
    Workflow:
    1. Patient gets ATC from PhilHealth (or walks in)
    2. Secretary creates appointment with ATC
    3. System validates ATC with PhilHealth API (isATCValid)
    4. Doctor conducts consultation
    5. Consultation linked to this appointment
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # EXISTING FIELDS
    # ═══════════════════════════════════════════════════════════════
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    
    doctor = models.ForeignKey(
        'login.DoctorProfile',
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    
    date = models.DateTimeField(
        help_text="Appointment date and time"
    )
    
    time = models.TimeField(
        help_text="Appointment time"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Appointment notes or reason for visit"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # NEW PHILHEALTH FIELDS
    # ═══════════════════════════════════════════════════════════════
    
    atc = models.CharField(
        max_length=10,
        blank=True,
        help_text="Authorization Transaction Code (10 chars) or 'WALKEDIN'"
    )
    
    is_walked_in = models.BooleanField(
        default=False,
        help_text="True if patient is a walk-in (no pre-generated ATC)"
    )
    
    atc_validated = models.BooleanField(
        default=False,
        help_text="Has the ATC been validated with PhilHealth?"
    )
    
    atc_validation_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was the ATC validated?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-time']
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
    
    def __str__(self):
        return f"{self.patient} - {self.date.strftime('%Y-%m-%d')} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Auto-set is_walked_in based on ATC value"""
        if self.atc and self.atc.upper() == 'WALKEDIN':
            self.is_walked_in = True
            self.atc = 'WALKEDIN'
        super().save(*args, **kwargs)
    
    @property
    def needs_atc_validation(self) -> bool:
        """Check if ATC needs to be validated"""
        return bool(self.atc) and not self.atc_validated and not self.is_walked_in
    
    @property
    def is_konsulta_ready(self) -> bool:
        """Check if appointment is ready for Konsulta service"""
        # Must have ATC (validated or walk-in)
        if not self.atc:
            return False
        # Walk-ins are always ready
        if self.is_walked_in:
            return True
        # Non-walk-ins must be validated
        return self.atc_validated
```

---

## STEP 3: Enhance Consultation Model (doctor/models.py)

### 3.1 Understanding SOAP Notes

PhilHealth requires consultations to follow the **SOAP** format:

```
┌─────────────────────────────────────────────────────────────────┐
│                       SOAP NOTE FORMAT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  S - SUBJECTIVE                                                  │
│  ──────────────                                                  │
│  What the patient tells you:                                     │
│  • Chief complaint                                               │
│  • History of present illness                                    │
│  • Symptoms in patient's own words                              │
│  • Duration, onset, severity                                     │
│                                                                  │
│  Example: "Patient complains of fever for 2 days,               │
│           accompanied by cough and colds. No vomiting."          │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  O - OBJECTIVE                                                   │
│  ─────────────                                                   │
│  What you observe/measure:                                       │
│  • Vital signs (BP, Temp, PR, RR)                               │
│  • Physical examination findings                                 │
│  • General appearance                                            │
│  • System-specific findings                                      │
│                                                                  │
│  Example: "BP: 120/80, Temp: 38.5°C, PR: 88, RR: 20            │
│           (+) pharyngeal erythema, clear lung sounds"           │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  A - ASSESSMENT                                                  │
│  ──────────────                                                  │
│  Your clinical judgment:                                         │
│  • Diagnosis or differential diagnoses                          │
│  • ICD-10 codes                                                  │
│  • Clinical impression                                           │
│                                                                  │
│  Example: "Acute Upper Respiratory Tract Infection (J06.9)"     │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  P - PLAN                                                        │
│  ─────────                                                       │
│  Your treatment plan:                                            │
│  • Medications prescribed                                        │
│  • Laboratory tests ordered                                      │
│  • Referrals                                                     │
│  • Patient education                                             │
│  • Follow-up schedule                                            │
│                                                                  │
│  Example: "1. Paracetamol 500mg 1 tab q6h for fever             │
│           2. Increase fluid intake                               │
│           3. Return if symptoms persist > 5 days"               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Enhanced Consultation Model

**File: `doctor/models.py`** - Update your Consultation class:

```python
from django.db import models
from django.conf import settings
from secretary.models import Appointment


class Medicine(models.Model):
    """
    Medicine catalog - Enhanced with PhilHealth drug code link.
    
    Links to PhilHealth's essential medicine codes for Konsulta reporting.
    """
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ═══════════════════════════════════════════════════════════════
    # NEW PHILHEALTH FIELDS
    # ═══════════════════════════════════════════════════════════════
    
    philhealth_drug_code = models.ForeignKey(
        'philhealth.DrugCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Link to PhilHealth Essential Medicine code"
    )
    
    is_konsulta_covered = models.BooleanField(
        default=False,
        help_text="Is this medicine covered under Konsulta package?"
    )
    
    generic_name = models.CharField(
        max_length=500,
        blank=True,
        help_text="Generic name (for PhilHealth reporting)"
    )
    
    strength = models.CharField(
        max_length=100,
        blank=True,
        help_text="Dosage strength (e.g., 500mg)"
    )
    
    form = models.CharField(
        max_length=100,
        blank=True,
        help_text="Dosage form (e.g., Tablet, Capsule)"
    )

    def __str__(self):
        return f"{self.name} - ₱{self.price}"

    class Meta:
        ordering = ['name']


class Consultation(models.Model):
    """
    Consultation / SOAP Note - Enhanced for PhilHealth Konsulta.
    
    This model captures the clinical encounter using the SOAP format
    required by PhilHealth for Konsulta reporting.
    
    PhilHealth XML Mapping (SOAP entity):
    - pHciTransNo → hci_trans_no
    - pConsultDate → consultation_date
    - pSubjective → subjective
    - pObjective → objective
    - pAssessment → assessment
    - pPlan → plan
    - pATC → atc
    - pIsWalkedIn → is_walked_in
    - pReportStatus → report_status
    """
    
    STATUS_CHOICES = [
        ("ONGOING", "Ongoing"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    
    REPORT_STATUS_CHOICES = [
        ('U', 'Unvalidated'),
        ('V', 'Validated'),
        ('F', 'Failed'),
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # EXISTING FIELDS (Modified)
    # ═══════════════════════════════════════════════════════════════
    
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="consultation"
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultations"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ONGOING"
    )
    
    date = models.DateTimeField(auto_now_add=True)
    
    # ═══════════════════════════════════════════════════════════════
    # LEGACY FIELDS (Keep for backward compatibility)
    # Map these to SOAP fields in migration
    # ═══════════════════════════════════════════════════════════════
    
    diagnosis = models.TextField(
        blank=True,
        help_text="Legacy field - use 'assessment' for new records"
    )
    
    reason_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Legacy field - use 'subjective' for new records"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Legacy field - use 'plan' for new records"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # NEW PHILHEALTH SOAP FIELDS
    # ═══════════════════════════════════════════════════════════════
    
    hci_trans_no = models.CharField(
        max_length=21,
        unique=True,
        null=True,
        blank=True,
        help_text="PhilHealth Transaction No: S + AccreNo(9) + YYYYMM + 5digits"
    )
    
    enlistment = models.ForeignKey(
        'philhealth.Enlistment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations',
        help_text="Link to patient's Konsulta enlistment"
    )
    
    # SOAP NOTE FIELDS
    subjective = models.TextField(
        blank=True,
        help_text="S - Chief complaint, symptoms, patient's history"
    )
    
    objective = models.TextField(
        blank=True,
        help_text="O - Physical examination, vital signs, observations"
    )
    
    assessment = models.TextField(
        blank=True,
        help_text="A - Diagnosis, clinical impression, ICD-10 codes"
    )
    
    plan = models.TextField(
        blank=True,
        help_text="P - Treatment plan, medications, referrals, follow-up"
    )
    
    # Diagnosis Code
    primary_diagnosis_code = models.ForeignKey(
        'philhealth.DiagnosisCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations',
        help_text="Primary ICD-10 diagnosis code"
    )
    
    # ATC Information
    atc = models.CharField(
        max_length=10,
        blank=True,
        help_text="Authorization Transaction Code"
    )
    
    is_walked_in = models.BooleanField(
        default=False,
        help_text="Was this a walk-in patient?"
    )
    
    consultation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of consultation (for PhilHealth reporting)"
    )
    
    # Follow-up
    next_consultation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Recommended follow-up date"
    )
    
    referral_facility = models.CharField(
        max_length=200,
        blank=True,
        help_text="If referred, name of facility"
    )
    
    referral_reason = models.TextField(
        blank=True,
        help_text="Reason for referral"
    )
    
    # PhilHealth Reporting Status
    report_status = models.CharField(
        max_length=1,
        choices=REPORT_STATUS_CHOICES,
        default='U',
        help_text="PhilHealth validation status"
    )
    
    deficiency_remarks = models.TextField(
        blank=True,
        help_text="Validation error messages from PhilHealth"
    )
    
    # eKAS Tracking
    ekas_generated = models.BooleanField(
        default=False,
        help_text="Has eKAS been generated?"
    )
    
    ekas_generated_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"

    def __str__(self):
        return f"Consultation for {self.appointment.patient} by {self.doctor}"
    
    def save(self, *args, **kwargs):
        """
        Auto-populate fields from appointment if not set
        """
        # Copy ATC from appointment
        if not self.atc and self.appointment.atc:
            self.atc = self.appointment.atc
            self.is_walked_in = self.appointment.is_walked_in
        
        # Set consultation date
        if not self.consultation_date:
            self.consultation_date = self.date.date() if self.date else None
        
        super().save(*args, **kwargs)
    
    def get_total_amount(self):
        """Calculate total from prescriptions"""
        return sum(
            prescription.get_total_price()
            for prescription in self.prescriptions.all()
        )
    
    @property
    def patient(self):
        """Shortcut to patient"""
        return self.appointment.patient
    
    @property
    def patient_pin(self):
        """Get patient's PhilHealth PIN"""
        return self.appointment.patient.philhealth_pin
    
    @property
    def is_soap_complete(self) -> bool:
        """Check if SOAP note is complete"""
        return all([
            self.subjective,
            self.objective,
            self.assessment,
            self.plan
        ])


class Prescription(models.Model):
    """
    Prescription - Enhanced for PhilHealth ESSENTIALMED reporting.
    
    PhilHealth XML Mapping (ESSENTIALMED entity):
    - pDrugCode → medicine.philhealth_drug_code
    - pGenericName → medicine.generic_name
    - pQuantity → quantity_dispensed
    - pDispenseDate → dispense_date
    - pReportStatus → report_status
    """
    
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity prescribed"
    )
    
    doctor_prescription = models.TextField(
        blank=True,
        null=True,
        help_text="Dosage instructions (e.g., '1 tab 3x a day')"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ═══════════════════════════════════════════════════════════════
    # NEW PHILHEALTH FIELDS
    # ═══════════════════════════════════════════════════════════════
    
    quantity_dispensed = models.PositiveIntegerField(
        default=0,
        help_text="Actual quantity dispensed"
    )
    
    dispense_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date medicine was dispensed"
    )
    
    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispensed_prescriptions',
        help_text="Staff who dispensed the medicine"
    )
    
    report_status = models.CharField(
        max_length=1,
        default='U',
        help_text="PhilHealth report status: U/V/F"
    )
    
    deficiency_remarks = models.TextField(
        blank=True,
        help_text="Validation errors from PhilHealth"
    )

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity} for {self.consultation}"

    def get_total_price(self):
        """Calculate price based on quantity prescribed"""
        return self.medicine.price * self.quantity
    
    @property
    def is_dispensed(self) -> bool:
        """Check if medicine has been dispensed"""
        return self.quantity_dispensed > 0
    
    @property
    def is_fully_dispensed(self) -> bool:
        """Check if full quantity was dispensed"""
        return self.quantity_dispensed >= self.quantity
```

---

## STEP 4: Enhance DoctorProfile (login/models.py)

### 4.1 Add PhilHealth Accreditation Fields

**File: `login/models.py`** - Update DoctorProfile:

```python
class DoctorProfile(models.Model):
    """
    Doctor Profile - Enhanced for PhilHealth Konsulta.
    
    Doctors providing Konsulta services must be PhilHealth-accredited.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ═══════════════════════════════════════════════════════════════
    # NEW PHILHEALTH FIELDS
    # ═══════════════════════════════════════════════════════════════
    
    philhealth_accreditation_no = models.CharField(
        max_length=20,
        blank=True,
        help_text="PhilHealth Accreditation Number"
    )
    
    is_konsulta_accredited = models.BooleanField(
        default=False,
        help_text="Is this doctor accredited for Konsulta services?"
    )
    
    accreditation_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="Accreditation expiry date"
    )
    
    ptr_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Professional Tax Receipt Number"
    )
    
    s2_license_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="S2 License Number (if applicable)"
    )
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"
    
    @property
    def is_accreditation_valid(self):
        """Check if PhilHealth accreditation is still valid"""
        if not self.is_konsulta_accredited:
            return False
        if not self.accreditation_expiry:
            return True
        from django.utils import timezone
        return self.accreditation_expiry >= timezone.now().date()
```

---

## STEP 5: Create and Run Migrations

### 5.1 Create Migrations

```bash
# Create migrations for all changes
python manage.py makemigrations secretary
python manage.py makemigrations doctor  
python manage.py makemigrations login

# Review the migrations before applying
python manage.py showmigrations

# Apply all migrations
python manage.py migrate
```

### 5.2 Data Migration Script (Optional)

If you have existing patients without PhilHealth data, create a data migration:

**File: `secretary/migrations/XXXX_migrate_patient_data.py`**

```python
from django.db import migrations

def migrate_gender_field(apps, schema_editor):
    """Convert old gender values to new format"""
    Patient = apps.get_model('secretary', 'Patient')
    
    # Update Male -> M
    Patient.objects.filter(gender='Male').update(gender='M')
    
    # Update Female -> F
    Patient.objects.filter(gender='Female').update(gender='F')

def reverse_migrate(apps, schema_editor):
    """Reverse the migration"""
    Patient = apps.get_model('secretary', 'Patient')
    Patient.objects.filter(gender='M').update(gender='Male')
    Patient.objects.filter(gender='F').update(gender='Female')

class Migration(migrations.Migration):
    dependencies = [
        ('secretary', 'XXXX_previous_migration'),  # Update this
    ]
    
    operations = [
        migrations.RunPython(migrate_gender_field, reverse_migrate),
    ]
```

---

## STEP 6: Update Admin Interface

**File: `secretary/admin.py`**

```python
from django.contrib import admin
from .models import Patient, Appointment, PatientDocument, PatientPicture


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'last_name', 'first_name', 'philhealth_pin', 
        'patient_type', 'gender', 'age', 'contact_number'
    ]
    list_filter = ['patient_type', 'gender', 'facility']
    search_fields = ['first_name', 'last_name', 'philhealth_pin']
    readonly_fields = ['created_at', 'updated_at', 'age']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'suffix',
                      'birth_date', 'gender', 'contact_number', 'email', 'address')
        }),
        ('PhilHealth Information', {
            'fields': ('philhealth_pin', 'patient_type', 'member', 
                      'relationship_code', 'facility')
        }),
        ('Photo & Consent', {
            'fields': ('photo', 'photo_consent'),
            'classes': ('collapse',)
        }),
        ('Legacy Data', {
            'fields': ('medical_history',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'doctor', 'date', 'status', 
        'atc', 'is_walked_in', 'atc_validated'
    ]
    list_filter = ['status', 'is_walked_in', 'atc_validated']
    search_fields = ['patient__first_name', 'patient__last_name', 'atc']
    date_hierarchy = 'date'
```

**File: `doctor/admin.py`**

```python
from django.contrib import admin
from .models import Medicine, Consultation, Prescription


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'generic_name', 'price', 
        'is_konsulta_covered', 'philhealth_drug_code'
    ]
    list_filter = ['is_konsulta_covered', 'is_active']
    search_fields = ['name', 'generic_name']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'doctor', 'date', 'status',
        'hci_trans_no', 'report_status'
    ]
    list_filter = ['status', 'report_status', 'is_walked_in']
    search_fields = ['appointment__patient__first_name', 'hci_trans_no']
    readonly_fields = ['date', 'updated_at']
    
    fieldsets = (
        ('Appointment Info', {
            'fields': ('appointment', 'doctor', 'status', 'date')
        }),
        ('PhilHealth Info', {
            'fields': ('hci_trans_no', 'enlistment', 'atc', 'is_walked_in')
        }),
        ('SOAP Note', {
            'fields': ('subjective', 'objective', 'assessment', 'plan')
        }),
        ('Diagnosis', {
            'fields': ('primary_diagnosis_code',)
        }),
        ('Legacy Fields', {
            'fields': ('diagnosis', 'reason_notes', 'notes'),
            'classes': ('collapse',)
        }),
        ('Follow-up & Referral', {
            'fields': ('next_consultation_date', 'referral_facility', 'referral_reason'),
            'classes': ('collapse',)
        }),
        ('Reporting Status', {
            'fields': ('report_status', 'deficiency_remarks', 
                      'ekas_generated', 'ekas_generated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        'consultation', 'medicine', 'quantity', 
        'quantity_dispensed', 'is_dispensed'
    ]
    list_filter = ['report_status']
```

---

## Phase 2 Checklist

### Models Enhanced

| Model | New Fields Added | Status |
|-------|-----------------|--------|
| **Patient** | philhealth_pin, patient_type, member, relationship_code, middle_name, suffix, photo, photo_consent, facility | □ |
| **Appointment** | atc, is_walked_in, atc_validated, atc_validation_date | □ |
| **Consultation** | hci_trans_no, enlistment, subjective, objective, assessment, plan, primary_diagnosis_code, atc, is_walked_in, consultation_date, next_consultation_date, referral_facility, referral_reason, report_status, deficiency_remarks, ekas_generated | □ |
| **Medicine** | philhealth_drug_code, is_konsulta_covered, generic_name, strength, form | □ |
| **Prescription** | quantity_dispensed, dispense_date, dispensed_by, report_status, deficiency_remarks | □ |
| **DoctorProfile** | philhealth_accreditation_no, is_konsulta_accredited, accreditation_expiry, ptr_number, s2_license_number | □ |

### Migrations

| Step | Command | Status |
|------|---------|--------|
| Create secretary migrations | `python manage.py makemigrations secretary` | □ |
| Create doctor migrations | `python manage.py makemigrations doctor` | □ |
| Create login migrations | `python manage.py makemigrations login` | □ |
| Apply migrations | `python manage.py migrate` | □ |

### Tests

| Test | Expected | Status |
|------|----------|--------|
| Create patient with PIN | PIN validated, saved as UPPERCASE | □ |
| Create dependent linked to member | Relationship saved correctly | □ |
| Create appointment with ATC | is_walked_in auto-set for WALKEDIN | □ |
| Create consultation with SOAP | All fields saved | □ |

---

## What's Next?

After Phase 2, you have:
- ✅ Patient model with PhilHealth PIN and patient types
- ✅ Member-Dependent relationships
- ✅ Appointment with ATC tracking
- ✅ Consultation with SOAP structure
- ✅ Medicine with PhilHealth drug codes
- ✅ Prescription with dispensing tracking

**Phase 3** will create the Enlistment, Profile, and related models for First Patient Encounter (FPE).

---

*Phase 2 Complete - Proceed to Phase 3: Enlistment & Profile Models*
