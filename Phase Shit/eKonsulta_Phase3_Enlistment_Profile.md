# PhilHealth eKonsulta Implementation
# PHASE 3: Enlistment & Profile Models (First Patient Encounter)

---

## Phase Overview

| Attribute | Details |
|-----------|---------|
| **Phase Number** | 3 of 5 |
| **Duration** | 1-2 Weeks |
| **Priority** | 🔴 Critical - Required for PhilHealth Claims |
| **Dependencies** | Phase 1 & 2 |
| **Outcome** | Enlistment, Profile, and FPE data models ready |

---

## What You'll Build in This Phase

```
philhealth/models.py (ADD TO EXISTING)
├── Enlistment          # Annual patient registration
├── Profile             # First Patient Encounter (FPE)
├── MedicalHistory      # Past medical conditions
├── FamilyHistory       # Family medical conditions
├── SocialHistory       # Lifestyle factors
├── VitalSigns          # BP, Height, Weight, BMI
└── NCDRiskAssessment   # NCD questionnaire (25+ years)
```

---

## Understanding the Enlistment → Profile Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              KONSULTA ENROLLMENT WORKFLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STEP 1: ENLISTMENT (Annual Registration)                       │
│  ─────────────────────────────────────────                      │
│  • Patient chooses your facility as their Konsulta provider     │
│  • Valid for ONE calendar year                                   │
│  • Creates ENLISTMENT record                                     │
│  • Generates: HciCaseNo, HciTransNo (E prefix)                  │
│                                                                  │
│           │                                                      │
│           ▼                                                      │
│                                                                  │
│  STEP 2: PROFILE / FPE (First Patient Encounter)                │
│  ───────────────────────────────────────────────                │
│  • Done ONCE when patient first visits                          │
│  • Captures comprehensive health data                           │
│  • Creates PROFILE record                                        │
│  • Generates: HciTransNo (P prefix)                             │
│                                                                  │
│  FPE Components:                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Demographics verification                               │   │
│  │ • Medical History (MEDHIST)                              │   │
│  │ • Family History (FAMHIST)                               │   │
│  │ • Social/Personal History (SOCIALHIST)                   │   │
│  │ • Vital Signs (VITALSIGNS)                               │   │
│  │ • NCD Risk Assessment (for age 25+)                      │   │
│  │ • Photo consent                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│           │                                                      │
│           ▼                                                      │
│                                                                  │
│  STEP 3: CONSULTATIONS (Ongoing Care)                           │
│  ────────────────────────────────────                           │
│  • Multiple consultations per year                              │
│  • Each creates SOAP record                                      │
│  • Links back to Enlistment                                      │
│                                                                  │
│           │                                                      │
│           ▼                                                      │
│                                                                  │
│  STEP 4: XML SUBMISSION                                          │
│  ──────────────────────                                          │
│  • First Tranche: ENLISTMENT + PROFILE (monthly)                │
│  • Second Tranche: + SOAP + LABEXAM + ESSENTIALMED (year-end)   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why FPE is Critical

| Reason | Explanation |
|--------|-------------|
| **Triggers Payment** | First tranche (40% = ₱680) released upon validated FPE |
| **Annual Requirement** | FPE done once per provider per year |
| **Comprehensive Data** | Full health profile for proper care |
| **PhilHealth Compliance** | Required fields for XML submission |

---

## STEP 1: Enlistment Model

### 1.1 Understanding Enlistment

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENLISTMENT ENTITY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Purpose: Annual registration of patient to Konsulta Provider   │
│                                                                  │
│  Key Fields:                                                     │
│  • hci_case_no: Patient's unique case number at this facility   │
│  • hci_trans_no: Enlistment transaction number (E prefix)       │
│  • effectivity_year: Calendar year of enrollment                │
│  • enlistment_status: 1=Active, 2=Cancelled, 3=Transferred     │
│  • package_type: K=Konsulta, P=PCB1, E=ExpandedPCB             │
│                                                                  │
│  Relationships:                                                  │
│  • One Patient can have multiple Enlistments (one per year)     │
│  • One Enlistment has one Profile (FPE)                         │
│  • One Enlistment can have multiple Consultations               │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    PATIENT                               │    │
│  │                       │                                  │    │
│  │    ┌──────────────────┼──────────────────┐              │    │
│  │    ▼                  ▼                  ▼              │    │
│  │ Enlistment        Enlistment        Enlistment          │    │
│  │   2023              2024              2025              │    │
│  │    │                  │                                 │    │
│  │    ▼                  ▼                                 │    │
│  │  Profile           Profile          (future)            │    │
│  │    │                  │                                 │    │
│  │    ▼                  ▼                                 │    │
│  │  Consults          Consults                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Enlistment Model Code

**Add to `philhealth/models.py`:**

```python
from django.db import models
from django.conf import settings
from django.utils import timezone


class Enlistment(models.Model):
    """
    Annual registration of a patient to a Konsulta Provider.
    
    A patient must be enlisted before they can receive Konsulta services.
    Enlistment is valid for one calendar year and includes:
    - Basic registration data
    - Link to patient and facility
    - Report status for PhilHealth validation
    
    PhilHealth XML Entity: ENLISTMENT
    
    Field Mappings:
    - pHciCaseNo → hci_case_no
    - pHciTransNo → hci_trans_no
    - pEffYear → effectivity_year
    - pEnlistStat → enlistment_status
    - pEnlistDate → enlistment_date
    - pPackageType → package_type
    - pMemPin → patient.philhealth_pin (if member)
    - pDepPin → patient.philhealth_pin (if dependent)
    - pReportStatus → report_status
    - pDeficiencyRemarks → deficiency_remarks
    
    Business Rules:
    - One active enlistment per patient per facility per year
    - Transfers only allowed in Q4 (except special circumstances)
    - FPE required for new enrollees and transfers
    """
    
    PACKAGE_CHOICES = [
        ('K', 'Konsulta'),
        ('P', 'PCB1'),
        ('E', 'Expanded PCB'),
    ]
    
    STATUS_CHOICES = [
        ('1', 'Active'),
        ('2', 'Cancelled'),
        ('3', 'Transferred'),
    ]
    
    REPORT_STATUS_CHOICES = [
        ('U', 'Unvalidated'),
        ('V', 'Validated'),
        ('F', 'Failed'),
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # PHILHEALTH TRANSACTION REFERENCES
    # ═══════════════════════════════════════════════════════════════
    
    hci_case_no = models.CharField(
        max_length=21,
        unique=True,
        help_text="Patient case number: T + AccreNo(9) + YYYYMM + 4digits. "
                  "Example: T12345678920241200001"
    )
    
    hci_trans_no = models.CharField(
        max_length=21,
        unique=True,
        help_text="Enlistment transaction number: E + AccreNo(9) + YYYYMM + 5digits. "
                  "Example: E1234567892024120001"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════
    
    facility = models.ForeignKey(
        'philhealth.HealthCareInstitution',
        on_delete=models.PROTECT,
        related_name='enlistments',
        help_text="The Konsulta provider facility"
    )
    
    patient = models.ForeignKey(
        'secretary.Patient',
        on_delete=models.PROTECT,
        related_name='enlistments',
        help_text="The enlisted patient"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ENLISTMENT DETAILS
    # ═══════════════════════════════════════════════════════════════
    
    effectivity_year = models.CharField(
        max_length=4,
        help_text="Year of enlistment (YYYY format)"
    )
    
    enlistment_status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='1',
        help_text="1=Active, 2=Cancelled, 3=Transferred"
    )
    
    enlistment_date = models.DateField(
        help_text="Date when patient was enlisted"
    )
    
    package_type = models.CharField(
        max_length=1,
        choices=PACKAGE_CHOICES,
        default='K',
        help_text="K=Konsulta, P=PCB1, E=Expanded PCB"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # PHILHEALTH REPORTING STATUS
    # ═══════════════════════════════════════════════════════════════
    
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
    
    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_enlistments'
    )
    
    class Meta:
        unique_together = ['patient', 'facility', 'effectivity_year']
        ordering = ['-effectivity_year', '-enlistment_date']
        verbose_name = "Enlistment"
        verbose_name_plural = "Enlistments"
    
    def __str__(self):
        return f"{self.patient} @ {self.facility.name} ({self.effectivity_year})"
    
    def save(self, *args, **kwargs):
        """Generate IDs if not set"""
        if not self.hci_case_no:
            self.hci_case_no = self.facility.get_next_case_number()
        if not self.hci_trans_no:
            self.hci_trans_no = self.facility.get_next_enlistment_number()
        super().save(*args, **kwargs)
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER PROPERTIES
    # ═══════════════════════════════════════════════════════════════
    
    @property
    def patient_pin(self):
        """Return the patient's PhilHealth PIN"""
        return self.patient.philhealth_pin
    
    @property
    def patient_type(self):
        """Return MM or DD based on patient type"""
        return self.patient.patient_type
    
    @property
    def member_pin(self):
        """Return the member's PIN (for both member and dependent)"""
        return self.patient.member_pin
    
    @property
    def is_active(self):
        """Check if enlistment is active"""
        return self.enlistment_status == '1'
    
    @property
    def has_profile(self):
        """Check if FPE has been completed"""
        return hasattr(self, 'profile')
    
    @property
    def is_validated(self):
        """Check if validated by PhilHealth"""
        return self.report_status == 'V'
    
    def get_consultations_count(self):
        """Get number of consultations for this enlistment"""
        return self.consultations.count()
```

---

## STEP 2: Profile (FPE) Model

### 2.1 Understanding Profile / FPE

The **Profile** captures the **First Patient Encounter (FPE)** - a comprehensive health assessment done once when a patient first enrolls or transfers to your facility.

```
┌─────────────────────────────────────────────────────────────────┐
│                  FIRST PATIENT ENCOUNTER (FPE)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  When FPE is Required:                                           │
│  ✓ First time patient enrolls at your facility                  │
│  ✓ Patient transfers from another facility                       │
│  ✓ Patient had no consultation in previous year (re-enroll)     │
│                                                                  │
│  When FPE is NOT Required:                                       │
│  ✗ Same facility, next year, had consultation last year         │
│                                                                  │
│  FPE Components:                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │  PROFILE (Core)                                          │    │
│  │  └── Demographics verification                           │    │
│  │  └── ATC validation                                      │    │
│  │                                                          │    │
│  │  MEDHIST (Medical History) - Multiple                    │    │
│  │  └── Past diseases/conditions                            │    │
│  │  └── Uses disease codes from lib_mdisease                │    │
│  │                                                          │    │
│  │  FAMHIST (Family History) - Multiple                     │    │
│  │  └── Family members' conditions                          │    │
│  │  └── Important: Diabetes triggers lab requirements       │    │
│  │                                                          │    │
│  │  SOCIALHIST (Social History) - One                       │    │
│  │  └── Smoking status                                      │    │
│  │  └── Alcohol use                                         │    │
│  │  └── Occupation                                          │    │
│  │                                                          │    │
│  │  VITALSIGNS - One (or multiple over time)                │    │
│  │  └── Blood Pressure                                      │    │
│  │  └── Height, Weight, BMI                                 │    │
│  │                                                          │    │
│  │  NCDQANS (NCD Assessment) - For patients 25+ years       │    │
│  │  └── Risk assessment questionnaire                       │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Profile Model Code

**Add to `philhealth/models.py`:**

```python
class Profile(models.Model):
    """
    First Patient Encounter (FPE) / Health Screening & Assessment.
    
    This is the comprehensive health profile captured when a patient
    first visits the facility. It includes medical history, family
    history, social history, vital signs, and NCD risk assessment.
    
    PhilHealth XML Entity: PROFILE
    
    Field Mappings:
    - pHciTransNo → hci_trans_no
    - pProfDate → profile_date
    - pPatientPin → patient_pin (property)
    - pPatientType → patient_type (property)
    - pPatientAge → patient_age
    - pMemPin → member_pin (property)
    - pEffYear → effectivity_year (property)
    - pATC → atc
    - pIsWalkedIn → is_walked_in
    - pTransDate → transaction_date
    - pReportStatus → report_status
    
    Child Entities:
    - MEDHIST (MedicalHistory)
    - FAMHIST (FamilyHistory)
    - SOCIALHIST (SocialHistory)
    - VITALSIGNS (VitalSigns)
    - NCDQANS (NCDRiskAssessment)
    """
    
    REPORT_STATUS_CHOICES = [
        ('U', 'Unvalidated'),
        ('V', 'Validated'),
        ('F', 'Failed'),
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # TRANSACTION REFERENCE
    # ═══════════════════════════════════════════════════════════════
    
    hci_trans_no = models.CharField(
        max_length=21,
        unique=True,
        help_text="Profile transaction number: P + AccreNo(9) + YYYYMM + 5digits"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIP (One-to-One with Enlistment)
    # ═══════════════════════════════════════════════════════════════
    
    enlistment = models.OneToOneField(
        Enlistment,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="The enlistment this FPE belongs to"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # PROFILE DATA
    # ═══════════════════════════════════════════════════════════════
    
    profile_date = models.DateField(
        help_text="Date when FPE was conducted"
    )
    
    patient_age = models.IntegerField(
        help_text="Patient's age at time of FPE"
    )
    
    # ATC Information
    atc = models.CharField(
        max_length=10,
        help_text="Authorization Transaction Code (or 'WALKEDIN')"
    )
    
    is_walked_in = models.BooleanField(
        default=False,
        help_text="True if patient was a walk-in"
    )
    
    transaction_date = models.DateField(
        help_text="Date when record was created"
    )
    
    # Staff who conducted the FPE
    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_profiles',
        help_text="Staff member who conducted the FPE"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # PHILHEALTH REPORTING STATUS
    # ═══════════════════════════════════════════════════════════════
    
    report_status = models.CharField(
        max_length=1,
        choices=REPORT_STATUS_CHOICES,
        default='U'
    )
    
    deficiency_remarks = models.TextField(blank=True)
    
    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profile (FPE)"
        verbose_name_plural = "Profiles (FPE)"
    
    def __str__(self):
        return f"FPE for {self.patient} on {self.profile_date}"
    
    def save(self, *args, **kwargs):
        """Generate transaction number and set defaults"""
        if not self.hci_trans_no:
            self.hci_trans_no = self.enlistment.facility.get_next_profile_number()
        
        # Auto-calculate age if not set
        if not self.patient_age:
            self.patient_age = self.patient.age
        
        # Set is_walked_in based on ATC
        if self.atc and self.atc.upper() == 'WALKEDIN':
            self.is_walked_in = True
        
        super().save(*args, **kwargs)
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER PROPERTIES
    # ═══════════════════════════════════════════════════════════════
    
    @property
    def patient(self):
        """Shortcut to patient"""
        return self.enlistment.patient
    
    @property
    def facility(self):
        """Shortcut to facility"""
        return self.enlistment.facility
    
    @property
    def patient_pin(self):
        return self.enlistment.patient_pin
    
    @property
    def patient_type(self):
        return self.enlistment.patient_type
    
    @property
    def member_pin(self):
        return self.enlistment.member_pin
    
    @property
    def effectivity_year(self):
        return self.enlistment.effectivity_year
    
    @property
    def is_complete(self):
        """Check if all required FPE components are complete"""
        return all([
            self.medical_history.exists() or True,  # Optional
            hasattr(self, 'social_history'),
            self.vital_signs.exists(),
        ])
    
    @property
    def needs_ncd_assessment(self):
        """Check if patient needs NCD assessment (25+ years)"""
        return self.patient_age >= 25
```

---

## STEP 3: Medical History Model

**Add to `philhealth/models.py`:**

```python
class MedicalHistory(models.Model):
    """
    Patient's Past Medical History.
    
    Records the patient's own medical conditions/diseases.
    Multiple conditions can be recorded per profile.
    
    PhilHealth XML Entity: MEDHIST
    
    Field Mappings:
    - pMdiseaseCode → disease_code.code
    - pReportStatus → report_status
    """
    
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='medical_history'
    )
    
    disease_code = models.ForeignKey(
        'philhealth.DiseaseCode',
        on_delete=models.PROTECT,
        help_text="Disease code from lib_mdisease"
    )
    
    diagnosis_date = models.DateField(
        null=True,
        blank=True,
        help_text="When was this condition diagnosed?"
    )
    
    is_current = models.BooleanField(
        default=True,
        help_text="Is this an ongoing condition?"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this condition"
    )
    
    report_status = models.CharField(max_length=1, default='U')
    deficiency_remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Medical History"
        verbose_name_plural = "Medical Histories"
    
    def __str__(self):
        return f"{self.profile.patient}: {self.disease_code}"
```

---

## STEP 4: Family History Model

**Add to `philhealth/models.py`:**

```python
class FamilyHistory(models.Model):
    """
    Family Medical History.
    
    Records medical conditions present in the patient's family.
    Important: If Diabetes Mellitus is present in family history,
    certain laboratory tests become required by PhilHealth.
    
    PhilHealth XML Entity: FAMHIST
    
    Field Mappings:
    - pFdiseaseCode → disease_code.code
    - pReportStatus → report_status
    """
    
    RELATIONSHIP_CHOICES = [
        ('MOTHER', 'Mother'),
        ('FATHER', 'Father'),
        ('SIBLING', 'Sibling'),
        ('GRANDMOTHER', 'Grandmother'),
        ('GRANDFATHER', 'Grandfather'),
        ('AUNT', 'Aunt'),
        ('UNCLE', 'Uncle'),
        ('OTHER', 'Other'),
    ]
    
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='family_history'
    )
    
    disease_code = models.ForeignKey(
        'philhealth.DiseaseCode',
        on_delete=models.PROTECT,
        help_text="Disease code from lib_mdisease"
    )
    
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        blank=True,
        help_text="Which family member has this condition"
    )
    
    notes = models.TextField(blank=True)
    
    report_status = models.CharField(max_length=1, default='U')
    deficiency_remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Family History"
        verbose_name_plural = "Family Histories"
    
    def __str__(self):
        rel = f" ({self.relationship})" if self.relationship else ""
        return f"{self.profile.patient}: {self.disease_code}{rel}"
```

---

## STEP 5: Social History Model

**Add to `philhealth/models.py`:**

```python
class SocialHistory(models.Model):
    """
    Personal and Social History.
    
    Records lifestyle factors that may affect health:
    smoking, alcohol use, occupation, etc.
    
    PhilHealth XML Entity: SOCIALHIST
    
    One SocialHistory per Profile (OneToOne relationship).
    """
    
    SMOKER_CHOICES = [
        ('Y', 'Yes - Current Smoker'),
        ('N', 'No - Never Smoked'),
        ('F', 'Former Smoker'),
    ]
    
    ALCOHOL_CHOICES = [
        ('Y', 'Yes - Current Drinker'),
        ('N', 'No - Never Drank'),
        ('F', 'Former Drinker'),
    ]
    
    ALCOHOL_FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('OCCASIONALLY', 'Occasionally'),
    ]
    
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='social_history'
    )
    
    # ═══════════════════════════════════════════════════════════════
    # SMOKING
    # ═══════════════════════════════════════════════════════════════
    
    smoking_status = models.CharField(
        max_length=1,
        choices=SMOKER_CHOICES,
        blank=True,
        help_text="Current smoking status"
    )
    
    smoking_sticks_per_day = models.IntegerField(
        null=True,
        blank=True,
        help_text="Average cigarettes per day (if smoker)"
    )
    
    smoking_years = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of years smoking (if smoker/former)"
    )
    
    smoking_quit_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date quit smoking (if former smoker)"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ALCOHOL
    # ═══════════════════════════════════════════════════════════════
    
    alcohol_status = models.CharField(
        max_length=1,
        choices=ALCOHOL_CHOICES,
        blank=True,
        help_text="Current alcohol consumption status"
    )
    
    alcohol_frequency = models.CharField(
        max_length=20,
        choices=ALCOHOL_FREQUENCY_CHOICES,
        blank=True,
        help_text="How often patient drinks"
    )
    
    alcohol_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of alcoholic beverages consumed"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # OCCUPATION & LIFESTYLE
    # ═══════════════════════════════════════════════════════════════
    
    occupation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Patient's occupation"
    )
    
    occupation_risks = models.TextField(
        blank=True,
        help_text="Occupational health risks"
    )
    
    exercise_frequency = models.CharField(
        max_length=50,
        blank=True,
        help_text="How often patient exercises"
    )
    
    diet_description = models.TextField(
        blank=True,
        help_text="Description of typical diet"
    )
    
    report_status = models.CharField(max_length=1, default='U')
    deficiency_remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Social History"
        verbose_name_plural = "Social Histories"
    
    def __str__(self):
        return f"Social History for {self.profile.patient}"
    
    @property
    def is_smoker(self):
        return self.smoking_status == 'Y'
    
    @property
    def is_drinker(self):
        return self.alcohol_status == 'Y'
    
    @property
    def pack_years(self):
        """Calculate pack-years for smokers"""
        if self.smoking_sticks_per_day and self.smoking_years:
            packs_per_day = self.smoking_sticks_per_day / 20
            return packs_per_day * self.smoking_years
        return 0
```

---

## STEP 6: Vital Signs Model

**Add to `philhealth/models.py`:**

```python
class VitalSigns(models.Model):
    """
    Vital Signs captured during FPE or consultations.
    
    PhilHealth XML Entity: VITALSIGNS
    
    Field Mappings:
    - pBP_Systolic → bp_systolic
    - pBP_Diastolic → bp_diastolic
    - pHeight → height_cm
    - pWeight → weight_kg
    - pBMI → bmi (auto-calculated)
    - pReportStatus → report_status
    """
    
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='vital_signs'
    )
    
    recorded_date = models.DateField(
        help_text="Date vitals were recorded"
    )
    
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_vitals'
    )
    
    # ═══════════════════════════════════════════════════════════════
    # BLOOD PRESSURE
    # ═══════════════════════════════════════════════════════════════
    
    bp_systolic = models.IntegerField(
        null=True,
        blank=True,
        help_text="Systolic blood pressure (mmHg)"
    )
    
    bp_diastolic = models.IntegerField(
        null=True,
        blank=True,
        help_text="Diastolic blood pressure (mmHg)"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ANTHROPOMETRICS
    # ═══════════════════════════════════════════════════════════════
    
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height in centimeters"
    )
    
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kilograms"
    )
    
    bmi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Body Mass Index (auto-calculated)"
    )
    
    waist_circumference_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Waist circumference in centimeters"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # OTHER VITALS
    # ═══════════════════════════════════════════════════════════════
    
    temperature_c = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Body temperature in Celsius"
    )
    
    pulse_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Pulse rate (beats per minute)"
    )
    
    respiratory_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Respiratory rate (breaths per minute)"
    )
    
    oxygen_saturation = models.IntegerField(
        null=True,
        blank=True,
        help_text="SpO2 percentage"
    )
    
    report_status = models.CharField(max_length=1, default='U')
    deficiency_remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Vital Signs"
        verbose_name_plural = "Vital Signs"
        ordering = ['-recorded_date']
    
    def __str__(self):
        return f"Vitals for {self.profile.patient} on {self.recorded_date}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate BMI"""
        if self.height_cm and self.weight_kg:
            height_m = float(self.height_cm) / 100
            self.bmi = round(float(self.weight_kg) / (height_m ** 2), 2)
        super().save(*args, **kwargs)
    
    @property
    def bp_reading(self):
        """Return formatted BP reading"""
        if self.bp_systolic and self.bp_diastolic:
            return f"{self.bp_systolic}/{self.bp_diastolic}"
        return "Not recorded"
    
    @property
    def bp_category(self):
        """Categorize blood pressure"""
        if not self.bp_systolic or not self.bp_diastolic:
            return "Unknown"
        
        if self.bp_systolic < 120 and self.bp_diastolic < 80:
            return "Normal"
        elif self.bp_systolic < 130 and self.bp_diastolic < 80:
            return "Elevated"
        elif self.bp_systolic < 140 or self.bp_diastolic < 90:
            return "High BP Stage 1"
        elif self.bp_systolic >= 140 or self.bp_diastolic >= 90:
            return "High BP Stage 2"
        elif self.bp_systolic > 180 or self.bp_diastolic > 120:
            return "Hypertensive Crisis"
        return "Unknown"
    
    @property
    def bmi_category(self):
        """Categorize BMI"""
        if not self.bmi:
            return "Unknown"
        
        bmi = float(self.bmi)
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
```

---

## STEP 7: NCD Risk Assessment Model

**Add to `philhealth/models.py`:**

```python
class NCDRiskAssessment(models.Model):
    """
    Non-Communicable Disease Risk Assessment.
    
    Required for patients aged 25 years and above.
    Assesses risk factors for cardiovascular disease,
    diabetes, and other NCDs.
    
    PhilHealth XML Entity: NCDQANS
    
    The questionnaire has 19 questions (qid1 through qid19).
    Most are Yes/No, qid17 is a risk level (A-E).
    """
    
    RISK_LEVEL_CHOICES = [
        ('A', '<10%'),
        ('B', '10% to 20%'),
        ('C', '20% to 30%'),
        ('D', '30% to 40%'),
        ('E', '>=40%'),
    ]
    
    YES_NO_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
    ]
    
    YES_NO_DONTKNOW_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
        ('X', "Don't Know"),
    ]
    
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='ncd_assessment'
    )
    
    assessment_date = models.DateField()
    
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # ═══════════════════════════════════════════════════════════════
    # QUESTIONS 1-4: Known Conditions
    # ═══════════════════════════════════════════════════════════════
    
    qid1_yn = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        blank=True,
        verbose_name="Q1",
        help_text="Have you been diagnosed with high blood pressure?"
    )
    
    qid2_yn = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        blank=True,
        verbose_name="Q2",
        help_text="Have you been diagnosed with diabetes?"
    )
    
    qid3_yn = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        blank=True,
        verbose_name="Q3",
        help_text="Have you had heart disease or stroke?"
    )
    
    qid4_yn = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        blank=True,
        verbose_name="Q4",
        help_text="Does anyone in your family have diabetes/heart disease?"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # QUESTION 5: Blood Sugar Knowledge
    # ═══════════════════════════════════════════════════════════════
    
    qid5_ynx = models.CharField(
        max_length=1,
        choices=YES_NO_DONTKNOW_CHOICES,
        blank=True,
        verbose_name="Q5",
        help_text="Do you know your blood sugar level?"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # QUESTIONS 6-16: Lifestyle and Risk Factors
    # ═══════════════════════════════════════════════════════════════
    
    qid6_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q6", help_text="Do you smoke?"
    )
    qid7_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q7", help_text="Do you drink alcohol?"
    )
    qid8_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q8", help_text="Do you eat vegetables daily?"
    )
    qid9_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q9", help_text="Do you eat fruits daily?"
    )
    qid10_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q10", help_text="Do you do physical activity?"
    )
    qid11_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q11", help_text="Are you overweight?"
    )
    qid12_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q12"
    )
    qid13_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q13"
    )
    qid14_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q14"
    )
    qid15_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q15"
    )
    qid16_yn = models.CharField(
        max_length=1, choices=YES_NO_CHOICES, blank=True,
        verbose_name="Q16"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # QUESTION 17: Cardiovascular Risk Level
    # ═══════════════════════════════════════════════════════════════
    
    qid17_risk_level = models.CharField(
        max_length=1,
        choices=RISK_LEVEL_CHOICES,
        blank=True,
        verbose_name="Q17 - Risk Level",
        help_text="Calculated cardiovascular risk level"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # QUESTIONS 18-19: Medication
    # ═══════════════════════════════════════════════════════════════
    
    qid18_yn = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        blank=True,
        verbose_name="Q18",
        help_text="Are you taking medication for diabetes?"
    )
    
    qid19_yn = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        blank=True,
        verbose_name="Q19",
        help_text="Are you taking medication for hypertension?"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # CALCULATED SCORE
    # ═══════════════════════════════════════════════════════════════
    
    total_risk_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calculated total risk score"
    )
    
    notes = models.TextField(blank=True)
    
    report_status = models.CharField(max_length=1, default='U')
    deficiency_remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "NCD Risk Assessment"
        verbose_name_plural = "NCD Risk Assessments"
    
    def __str__(self):
        return f"NCD Assessment for {self.profile.patient}"
    
    @property
    def is_high_risk(self):
        """Check if patient is high risk (>=20%)"""
        return self.qid17_risk_level in ['C', 'D', 'E']
```

---

## STEP 8: Create Migrations

After adding all models, create and run migrations:

```bash
# Create migrations
python manage.py makemigrations philhealth

# Review the migration
python manage.py showmigrations philhealth

# Apply migrations
python manage.py migrate philhealth
```

---

## STEP 9: Register in Admin

**File: `philhealth/admin.py`:**

```python
from django.contrib import admin
from .models import (
    HealthCareInstitution, DiseaseCode, DrugCode, 
    LaboratoryExamCode, DiagnosisCode,
    Enlistment, Profile, MedicalHistory, FamilyHistory,
    SocialHistory, VitalSigns, NCDRiskAssessment
)


@admin.register(Enlistment)
class EnlistmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'facility', 'effectivity_year',
        'enlistment_status', 'has_profile', 'report_status'
    ]
    list_filter = ['effectivity_year', 'enlistment_status', 'report_status']
    search_fields = ['patient__first_name', 'patient__last_name', 'hci_case_no']
    readonly_fields = ['hci_case_no', 'hci_trans_no', 'created_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'profile_date', 'patient_age',
        'atc', 'is_walked_in', 'report_status'
    ]
    list_filter = ['report_status', 'is_walked_in']
    search_fields = ['enlistment__patient__first_name']
    readonly_fields = ['hci_trans_no', 'created_at']
    
    def patient(self, obj):
        return obj.enlistment.patient


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['profile', 'disease_code', 'is_current', 'report_status']
    list_filter = ['is_current', 'report_status']


@admin.register(FamilyHistory)
class FamilyHistoryAdmin(admin.ModelAdmin):
    list_display = ['profile', 'disease_code', 'relationship', 'report_status']
    list_filter = ['relationship', 'report_status']


@admin.register(SocialHistory)
class SocialHistoryAdmin(admin.ModelAdmin):
    list_display = ['profile', 'smoking_status', 'alcohol_status', 'occupation']


@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = [
        'profile', 'recorded_date', 'bp_reading',
        'bmi', 'bmi_category', 'report_status'
    ]
    list_filter = ['report_status']


@admin.register(NCDRiskAssessment)
class NCDRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = [
        'profile', 'assessment_date', 'qid17_risk_level',
        'is_high_risk', 'report_status'
    ]
    list_filter = ['qid17_risk_level', 'report_status']
```

---

## STEP 10: Testing

**Test in Django Shell:**

```python
from datetime import date
from philhealth.models import *
from secretary.models import Patient

# Get facility and patient
facility = HealthCareInstitution.objects.first()
patient = Patient.objects.first()

# Create Enlistment
enlistment = Enlistment.objects.create(
    facility=facility,
    patient=patient,
    effectivity_year='2024',
    enlistment_date=date.today(),
    package_type='K'
)
print(f"Enlistment: {enlistment.hci_case_no}")

# Create Profile (FPE)
profile = Profile.objects.create(
    enlistment=enlistment,
    profile_date=date.today(),
    patient_age=patient.age,
    atc='WALKEDIN',
    transaction_date=date.today()
)
print(f"Profile: {profile.hci_trans_no}")

# Add Vital Signs
vitals = VitalSigns.objects.create(
    profile=profile,
    recorded_date=date.today(),
    bp_systolic=120,
    bp_diastolic=80,
    height_cm=170,
    weight_kg=70
)
print(f"BMI: {vitals.bmi} ({vitals.bmi_category})")

# Add Medical History
disease = DiseaseCode.objects.first()
if disease:
    med_hist = MedicalHistory.objects.create(
        profile=profile,
        disease_code=disease,
        is_current=True
    )
    print(f"Medical History: {med_hist}")
```

---

## Phase 3 Checklist

| Model | Purpose | Status |
|-------|---------|--------|
| **Enlistment** | Annual patient registration | □ |
| **Profile** | First Patient Encounter core data | □ |
| **MedicalHistory** | Patient's past conditions | □ |
| **FamilyHistory** | Family medical conditions | □ |
| **SocialHistory** | Lifestyle factors | □ |
| **VitalSigns** | BP, height, weight, BMI | □ |
| **NCDRiskAssessment** | NCD questionnaire (25+) | □ |

---

## What's Next?

After Phase 3, you have the complete data structure for:
- ✅ Patient enrollment (Enlistment)
- ✅ First Patient Encounter (Profile)
- ✅ Health history (Medical, Family, Social)
- ✅ Vital signs with auto BMI
- ✅ NCD risk assessment

**Phase 4** will implement the PKA API integration for:
- Token authentication
- Member/ATC validation
- XML generation and submission

---

*Phase 3 Complete - Proceed to Phase 4: PKA API Integration*
