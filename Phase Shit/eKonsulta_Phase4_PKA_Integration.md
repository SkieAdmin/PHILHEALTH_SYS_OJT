# PhilHealth eKonsulta Implementation
# PHASE 4: PhilHealth Konsulta API (PKA) Integration

---

## Phase Overview

| Attribute | Details |
|-----------|---------|
| **Phase Number** | 4 of 5 |
| **Duration** | 2-3 Weeks |
| **Priority** | 🔴 Critical - Required for PhilHealth Communication |
| **Dependencies** | Phase 1, 2, 3 |
| **Outcome** | Full API integration with PhilHealth servers |

---

## What You'll Build in This Phase

```
philhealth/
├── pka_client.py           # Main API client class
├── api_services/
│   ├── __init__.py
│   ├── authentication.py   # Token management (GTM)
│   ├── registration.py     # Member validation (MDRC, ERL, ATCV)
│   └── reporting.py        # XML submission (VKR, SKR)
├── xml_generator.py        # XML report generation
└── models.py               # Add TransmittalReport model
```

---

## Understanding the PKA Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              PHILHEALTH KONSULTA API (PKA) MODULES               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MODULE 1: AUTHENTICATION                                        │
│  ─────────────────────────                                       │
│  • getToken (GTM)                                                │
│    └─ Generates access token for all API calls                  │
│    └─ Token must be in header: Key="Token", Value=<token>       │
│                                                                  │
│  MODULE 2: REGISTRATION VALIDATION                               │
│  ─────────────────────────────────                               │
│  • isMemberRegistered (MDRC)                                     │
│    └─ Verify if member/dependent is registered                  │
│  • extractRegistrationList (ERL)                                 │
│    └─ Download all registered beneficiaries                     │
│  • isATCValid (ATCV)                                             │
│    └─ Validate Authorization Transaction Code                   │
│                                                                  │
│  MODULE 3: KONSULTA REPORTING                                    │
│  ────────────────────────────                                    │
│  • validateReport (VKR)                                          │
│    └─ Pre-validate XML without uploading                        │
│  • submitReport (SKR)                                            │
│    └─ Submit encrypted XML to PhilHealth                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    API COMMUNICATION FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  YOUR SYSTEM                              PHILHEALTH PKA         │
│                                                                  │
│  1. Request Token                                                │
│     getToken(username, password, certId, accreNo)               │
│     ─────────────────────────────────────────────────────►      │
│                                                                  │
│                         ◄─────────────────────────────────      │
│                              { accessToken, expiresIn }          │
│                                                                  │
│  2. Validate Member                                              │
│     isMemberRegistered(PIN, type, year)                         │
│     Header: Token = <accessToken>                               │
│     ─────────────────────────────────────────────────────►      │
│                                                                  │
│                         ◄─────────────────────────────────      │
│                              Encrypted XML Response             │
│                                                                  │
│  3. Validate ATC                                                 │
│     isATCValid(PIN, ATC, date)                                  │
│     ─────────────────────────────────────────────────────►      │
│                                                                  │
│                         ◄─────────────────────────────────      │
│                              { valid: true/false }              │
│                                                                  │
│  4. Submit Report                                                │
│     submitReport(transmittalId, encryptedXML, tagging)          │
│     ─────────────────────────────────────────────────────►      │
│                                                                  │
│                         ◄─────────────────────────────────      │
│                              { transactionNumber }              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## STEP 1: Create the PKA Client

### 1.1 Main Client Class

**File: `philhealth/pka_client.py`**

```python
"""
PhilHealth Konsulta API (PKA) Client

This module provides the main interface for communicating with
PhilHealth's Konsulta API. It handles authentication, token
management, and all API operations.

Usage:
    from philhealth.pka_client import PKAClient
    from philhealth.models import HealthCareInstitution
    
    facility = HealthCareInstitution.objects.get(id=1)
    client = PKAClient(facility)
    
    # Validate a member
    result = client.is_member_registered(
        pin="012345678901",
        member_type="MM",
        effectivity_year="2024"
    )
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
from django.conf import settings
from django.utils import timezone

from .encryption import PhilHealthEncryption
from .models import HealthCareInstitution

logger = logging.getLogger(__name__)


class PKAClientError(Exception):
    """Base exception for PKA client errors"""
    pass


class PKAAuthenticationError(PKAClientError):
    """Authentication failed"""
    pass


class PKAValidationError(PKAClientError):
    """Validation error from PhilHealth"""
    pass


class PKAClient:
    """
    PhilHealth Konsulta API Client.
    
    Provides methods for all PKA operations:
    - Authentication (getToken)
    - Registration validation (isMemberRegistered, extractRegistrationList, isATCValid)
    - Reporting (validateReport, submitReport)
    
    All XML data is automatically encrypted/decrypted using AES-256-CBC.
    Token management is handled automatically.
    
    Attributes:
        facility: The HealthCareInstitution making API calls
        base_url: PKA base URL from settings
        timeout: Request timeout in seconds
    """
    
    # Default timeout for API requests (seconds)
    DEFAULT_TIMEOUT = 30
    
    # Token refresh buffer (refresh 5 minutes before expiry)
    TOKEN_REFRESH_BUFFER = 300
    
    def __init__(self, facility: HealthCareInstitution):
        """
        Initialize PKA Client for a specific facility.
        
        Args:
            facility: The HCI making API calls. Must have valid
                     PKA credentials configured.
        """
        self.facility = facility
        self.base_url = getattr(settings, 'PKA_BASE_URL', 'https://pka.philhealth.gov.ph/api')
        self.timeout = getattr(settings, 'PKA_TIMEOUT', self.DEFAULT_TIMEOUT)
        
        # Token management
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        
        # Encryption handler
        self._encryption: Optional[PhilHealthEncryption] = None
        
        # Validate facility has required credentials
        self._validate_facility()
    
    def _validate_facility(self):
        """Ensure facility has required PKA credentials"""
        if not self.facility.pka_username:
            raise PKAClientError("Facility missing PKA username")
        if not self.facility.pka_password:
            raise PKAClientError("Facility missing PKA password")
        if not self.facility.software_certification_id:
            raise PKAClientError("Facility missing Software Certification ID")
        if not self.facility.cipher_key:
            raise PKAClientError("Facility missing cipher key for encryption")
    
    @property
    def encryption(self) -> PhilHealthEncryption:
        """Lazy-load encryption handler"""
        if self._encryption is None:
            self._encryption = PhilHealthEncryption(self.facility.cipher_key)
        return self._encryption
    
    # ═══════════════════════════════════════════════════════════════════════
    # MODULE 1: AUTHENTICATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_token(self, force_refresh: bool = False) -> str:
        """
        Get access token for PKA API calls.
        
        Implements GTM (Get Token Method). Tokens are cached and
        automatically refreshed when expired.
        
        Args:
            force_refresh: If True, get new token even if current is valid
            
        Returns:
            str: Access token
            
        Raises:
            PKAAuthenticationError: If authentication fails
        """
        # Return cached token if still valid
        if not force_refresh and self._is_token_valid():
            return self._token
        
        logger.info(f"Requesting new PKA token for {self.facility.accreditation_number}")
        
        try:
            response = requests.post(
                f"{self.base_url}/getToken",
                json={
                    "pUserName": self.facility.pka_username,
                    "pUserPassword": self.facility.pka_password,
                    "pSoftwareCertificationId": self.facility.software_certification_id,
                    "pHospitalCode": self.facility.accreditation_number,
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'accessToken' not in data:
                error_msg = data.get('message', 'Unknown error')
                raise PKAAuthenticationError(f"Token request failed: {error_msg}")
            
            self._token = data['accessToken']
            expires_in = data.get('expiresIn', 3600)
            self._token_expiry = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info(f"PKA token obtained, expires in {expires_in} seconds")
            return self._token
            
        except requests.RequestException as e:
            logger.error(f"PKA token request failed: {e}")
            raise PKAAuthenticationError(f"Failed to get token: {e}")
    
    def _is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self._token or not self._token_expiry:
            return False
        
        # Add buffer to ensure token doesn't expire mid-request
        buffer = timedelta(seconds=self.TOKEN_REFRESH_BUFFER)
        return timezone.now() < (self._token_expiry - buffer)
    
    def _ensure_token(self):
        """Ensure we have a valid token before making API calls"""
        if not self._is_token_valid():
            self.get_token()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        self._ensure_token()
        return {
            "Content-Type": "application/json",
            "Token": self._token
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # MODULE 2: REGISTRATION VALIDATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def is_member_registered(
        self,
        pin: str,
        member_type: str,
        effectivity_year: str
    ) -> Dict[str, Any]:
        """
        Check if a member/dependent is registered with this facility.
        
        Implements MDRC (Member/Dependent Registration Check).
        
        Args:
            pin: 12-digit PhilHealth PIN
            member_type: 'MM' for member, 'DD' for dependent
            effectivity_year: Year to check (YYYY format)
            
        Returns:
            dict: Decrypted member information
            
        Raises:
            PKAValidationError: If member not found or invalid
        """
        logger.info(f"Checking member registration: PIN={pin[:4]}**** Type={member_type}")
        
        try:
            response = requests.post(
                f"{self.base_url}/isMemberRegistered",
                json={
                    "pPIN": pin,
                    "pMemberType": member_type,
                    "pEffectivityYear": effectivity_year,
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Check for error response
            if 'error' in data:
                raise PKAValidationError(data['error'])
            
            # Decrypt XML response if encrypted
            if 'doc' in data:
                decrypted_xml, valid = self.encryption.decrypt_xml(
                    response.text
                )
                return self._parse_member_xml(decrypted_xml)
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Member registration check failed: {e}")
            raise PKAClientError(f"API request failed: {e}")
    
    def extract_registration_list(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> list:
        """
        Download list of registered beneficiaries within date range.
        
        Implements ERL (Extract Registration List).
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            list: List of registered members/dependents
        """
        logger.info(f"Extracting registration list: {start_date} to {end_date}")
        
        try:
            response = requests.post(
                f"{self.base_url}/extractRegistrationList",
                json={
                    "pStartDate": start_date.strftime("%m/%d/%Y"),
                    "pEndDate": end_date.strftime("%m/%d/%Y"),
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Decrypt XML response
            decrypted_xml, valid = self.encryption.decrypt_xml(response.text)
            return self._parse_registration_list_xml(decrypted_xml)
            
        except requests.RequestException as e:
            logger.error(f"Registration list extraction failed: {e}")
            raise PKAClientError(f"API request failed: {e}")
    
    def is_atc_valid(
        self,
        pin: str,
        atc: str,
        effectivity_date: datetime
    ) -> bool:
        """
        Validate Authorization Transaction Code (ATC).
        
        Implements ATCV (Authorization Transaction Code Validation).
        Must be called before providing Konsulta services.
        
        Args:
            pin: Patient's PhilHealth PIN
            atc: Authorization Transaction Code (or 'WALKEDIN')
            effectivity_date: Date of service
            
        Returns:
            bool: True if ATC is valid
            
        Note:
            Walk-in patients should use 'WALKEDIN' as the ATC value.
        """
        # Walk-in patients are always valid
        if atc and atc.upper() == 'WALKEDIN':
            logger.info(f"Walk-in patient, ATC validation skipped")
            return True
        
        logger.info(f"Validating ATC: PIN={pin[:4]}**** ATC={atc}")
        
        try:
            response = requests.post(
                f"{self.base_url}/isATCValid",
                json={
                    "pPIN": pin,
                    "pATC": atc,
                    "pEffectivityDate": effectivity_date.strftime("%m/%d/%Y"),
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            is_valid = data.get('valid', False)
            logger.info(f"ATC validation result: {is_valid}")
            
            return is_valid
            
        except requests.RequestException as e:
            logger.error(f"ATC validation failed: {e}")
            raise PKAClientError(f"API request failed: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # MODULE 3: KONSULTA REPORTING
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_report(
        self,
        xml_report: str,
        report_tagging: str
    ) -> Tuple[str, bool, str]:
        """
        Pre-validate Konsulta report without uploading.
        
        Implements VKR (Validate Konsulta Report).
        Use this to check for errors before actual submission.
        
        Args:
            xml_report: Raw XML report data
            report_tagging: '1' for first tranche, '2' for second tranche
            
        Returns:
            Tuple of:
            - Validated XML (with updated report statuses)
            - Success boolean
            - Error message (if failed)
        """
        logger.info(f"Validating report (tagging={report_tagging})")
        
        try:
            # Encrypt the XML payload
            encrypted_payload = self.encryption.encrypt_xml(xml_report)
            
            response = requests.post(
                f"{self.base_url}/validateReport",
                json={
                    "pReport": encrypted_payload,
                    "pReportTagging": report_tagging,
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Decrypt response
            decrypted_xml, valid = self.encryption.decrypt_xml(response.text)
            
            # Check validation status
            success = self._check_validation_status(decrypted_xml)
            error_msg = "" if success else self._extract_errors(decrypted_xml)
            
            logger.info(f"Report validation: success={success}")
            return decrypted_xml, success, error_msg
            
        except requests.RequestException as e:
            logger.error(f"Report validation failed: {e}")
            raise PKAClientError(f"API request failed: {e}")
    
    def submit_report(
        self,
        transmittal_id: str,
        xml_report: str,
        report_tagging: str
    ) -> Dict[str, Any]:
        """
        Submit Konsulta report to PhilHealth.
        
        Implements SKR (Submit Konsulta Report).
        Should only be called after successful validation.
        
        Args:
            transmittal_id: Your generated transmittal ID
                           Format: R + AccreNo(9) + YYYYMM + 5digits
            xml_report: Raw XML report data
            report_tagging: '1' for first tranche, '2' for second tranche
            
        Returns:
            dict: Contains 'transactionNumber' on success
            
        Raises:
            PKAValidationError: If submission fails
        """
        logger.info(f"Submitting report: transmittal={transmittal_id} tagging={report_tagging}")
        
        try:
            # Encrypt the XML payload
            encrypted_payload = self.encryption.encrypt_xml(xml_report)
            
            response = requests.post(
                f"{self.base_url}/submitReport",
                json={
                    "pTransmittalId": transmittal_id,
                    "pReport": encrypted_payload,
                    "pReportTagging": report_tagging,
                },
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'transactionNumber' in data:
                logger.info(f"Report submitted: txn={data['transactionNumber']}")
                return data
            
            # Handle error
            error_msg = data.get('message', 'Unknown error')
            logger.error(f"Report submission failed: {error_msg}")
            raise PKAValidationError(error_msg)
            
        except requests.RequestException as e:
            logger.error(f"Report submission failed: {e}")
            raise PKAClientError(f"API request failed: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _parse_member_xml(self, xml_string: str) -> Dict[str, Any]:
        """Parse member information from XML response"""
        import xml.etree.ElementTree as ET
        # Implementation depends on PhilHealth's XML structure
        # This is a placeholder
        return {"raw_xml": xml_string}
    
    def _parse_registration_list_xml(self, xml_string: str) -> list:
        """Parse registration list from XML response"""
        import xml.etree.ElementTree as ET
        # Implementation depends on PhilHealth's XML structure
        return []
    
    def _check_validation_status(self, xml_string: str) -> bool:
        """Check if all records in XML have status 'V' (Validated)"""
        return 'pReportStatus="F"' not in xml_string
    
    def _extract_errors(self, xml_string: str) -> str:
        """Extract error messages from validated XML"""
        import re
        errors = re.findall(r'pDeficiencyRemarks="([^"]*)"', xml_string)
        return "; ".join(filter(None, errors))
```

---

## STEP 2: XML Generator Service

### 2.1 Understanding XML Structure

PhilHealth requires XML reports in a specific format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PCB>
    <!-- Header -->
    <pUsername>HCI_USER</pUsername>
    <pPassword>ENCRYPTED</pPassword>
    <pHciAccreNo>123456789</pHciAccreNo>
    <pPMCCNo>123456</pPMCCNo>
    <pCertificationId>CERT123456789012345</pCertificationId>
    <pHciTransmittalNumber>R12345678920241200001</pHciTransmittalNumber>
    <pEnlistTotalCnt>100</pEnlistTotalCnt>
    <pProfileTotalCnt>100</pProfileTotalCnt>
    <pSoapTotalCnt>50</pSoapTotalCnt>
    
    <!-- Enlistment Records -->
    <ENLISTMENT>
        <pHciCaseNo>T123456789202412-0001</pHciCaseNo>
        <pHciTransNo>E12345678920241200001</pHciTransNo>
        <!-- ... more fields ... -->
        
        <PROFILE>
            <pHciTransNo>P12345678920241200001</pHciTransNo>
            <!-- ... profile fields ... -->
            
            <MEDHIST>
                <pMdiseaseCode>HTN</pMdiseaseCode>
                <pReportStatus>U</pReportStatus>
            </MEDHIST>
            
            <VITALSIGNS>
                <pBP_Systolic>120</pBP_Systolic>
                <pBP_Diastolic>80</pBP_Diastolic>
                <!-- ... -->
            </VITALSIGNS>
        </PROFILE>
        
        <!-- For Second Tranche -->
        <SOAP>
            <pHciTransNo>S12345678920241200001</pHciTransNo>
            <!-- ... SOAP fields ... -->
        </SOAP>
        
        <ESSENTIALMED>
            <pDrugCode>MET500</pDrugCode>
            <!-- ... medicine fields ... -->
        </ESSENTIALMED>
    </ENLISTMENT>
</PCB>
```

### 2.2 XML Generator Code

**File: `philhealth/xml_generator.py`**

```python
"""
PhilHealth Konsulta XML Report Generator

Generates XML reports in PhilHealth-compliant format for:
- First Tranche: ENLISTMENT + PROFILE data
- Second Tranche: + SOAP + LABEXAM + ESSENTIALMED

Usage:
    from philhealth.xml_generator import KonsultaXMLGenerator
    
    generator = KonsultaXMLGenerator(facility)
    xml = generator.generate_first_tranche('2024-12')
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import List, Optional
from django.db.models import QuerySet

from .models import (
    HealthCareInstitution, Enlistment, Profile,
    MedicalHistory, FamilyHistory, SocialHistory, VitalSigns
)


class KonsultaXMLGenerator:
    """
    Generates PhilHealth Konsulta XML reports.
    
    Supports both First Tranche (monthly FPE data) and
    Second Tranche (year-end complete data) reports.
    """
    
    def __init__(self, facility: HealthCareInstitution):
        """
        Initialize generator for a facility.
        
        Args:
            facility: The HCI generating the report
        """
        self.facility = facility
    
    def generate_first_tranche(
        self,
        year_month: str,
        enlistments: Optional[QuerySet] = None
    ) -> str:
        """
        Generate First Tranche XML (pReportTagging = '1').
        
        First tranche contains:
        - PCB header
        - ENLISTMENT records
        - PROFILE (FPE) data
        - MEDHIST, FAMHIST, SOCIALHIST, VITALSIGNS
        
        Does NOT include: SOAP, LABEXAM, ESSENTIALMED
        
        Args:
            year_month: Report period (YYYY-MM format)
            enlistments: Optional queryset of specific enlistments
                        If None, includes all for the period
                        
        Returns:
            str: XML string (not encrypted)
        """
        # Get enlistments if not provided
        if enlistments is None:
            enlistments = self._get_enlistments_for_period(year_month)
        
        # Build XML
        root = self._create_root()
        self._add_header(root, enlistments, year_month, include_soap=False)
        
        # Add each enlistment
        for enlistment in enlistments:
            self._add_enlistment(root, enlistment, include_clinical=False)
        
        return self._to_string(root)
    
    def generate_second_tranche(
        self,
        year: str,
        enlistments: Optional[QuerySet] = None
    ) -> str:
        """
        Generate Second Tranche XML (pReportTagging = '2').
        
        Second tranche contains everything in first tranche PLUS:
        - SOAP consultation records
        - LABEXAM diagnostic results
        - ESSENTIALMED medicine dispensing
        - DOCUMENT attachments (eKAS, ePresS URLs)
        
        Args:
            year: Report year (YYYY format)
            enlistments: Optional queryset of specific enlistments
            
        Returns:
            str: XML string (not encrypted)
        """
        if enlistments is None:
            enlistments = self._get_enlistments_for_year(year)
        
        root = self._create_root()
        self._add_header(root, enlistments, f"{year}-12", include_soap=True)
        
        for enlistment in enlistments:
            self._add_enlistment(root, enlistment, include_clinical=True)
        
        return self._to_string(root)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE METHODS - XML BUILDING
    # ═══════════════════════════════════════════════════════════════════════
    
    def _create_root(self) -> ET.Element:
        """Create the root PCB element"""
        return ET.Element('PCB')
    
    def _add_header(
        self,
        root: ET.Element,
        enlistments: QuerySet,
        year_month: str,
        include_soap: bool
    ):
        """Add PCB header elements"""
        ET.SubElement(root, 'pUsername').text = self.facility.pka_username
        ET.SubElement(root, 'pPassword').text = '[ENCRYPTED]'
        ET.SubElement(root, 'pHciAccreNo').text = self.facility.accreditation_number
        ET.SubElement(root, 'pPMCCNo').text = self.facility.pmcc_number
        ET.SubElement(root, 'pCertificationId').text = self.facility.software_certification_id
        ET.SubElement(root, 'pHciTransmittalNumber').text = self.facility.get_next_transmittal_number()
        
        # Counts
        ET.SubElement(root, 'pEnlistTotalCnt').text = str(enlistments.count())
        ET.SubElement(root, 'pProfileTotalCnt').text = str(
            enlistments.filter(profile__isnull=False).count()
        )
        
        if include_soap:
            from doctor.models import Consultation
            soap_count = Consultation.objects.filter(
                enlistment__in=enlistments
            ).count()
            ET.SubElement(root, 'pSoapTotalCnt').text = str(soap_count)
        else:
            ET.SubElement(root, 'pSoapTotalCnt').text = '0'
    
    def _add_enlistment(
        self,
        root: ET.Element,
        enlistment: Enlistment,
        include_clinical: bool
    ):
        """Add ENLISTMENT element with all child elements"""
        enlist_elem = ET.SubElement(root, 'ENLISTMENT')
        
        # Enlistment fields
        ET.SubElement(enlist_elem, 'pHciCaseNo').text = enlistment.hci_case_no
        ET.SubElement(enlist_elem, 'pHciTransNo').text = enlistment.hci_trans_no
        ET.SubElement(enlist_elem, 'pEffYear').text = enlistment.effectivity_year
        ET.SubElement(enlist_elem, 'pEnlistStat').text = enlistment.enlistment_status
        ET.SubElement(enlist_elem, 'pEnlistDate').text = enlistment.enlistment_date.strftime('%Y-%m-%d')
        ET.SubElement(enlist_elem, 'pPackageType').text = enlistment.package_type
        
        # Member info
        patient = enlistment.patient
        ET.SubElement(enlist_elem, 'pMemPin').text = patient.member_pin or patient.philhealth_pin
        ET.SubElement(enlist_elem, 'pMemFname').text = patient.first_name
        ET.SubElement(enlist_elem, 'pMemMname').text = patient.middle_name or ''
        ET.SubElement(enlist_elem, 'pMemLname').text = patient.last_name
        ET.SubElement(enlist_elem, 'pMemBdate').text = patient.birth_date.strftime('%Y-%m-%d')
        ET.SubElement(enlist_elem, 'pMemSex').text = patient.gender
        
        # Dependent info if applicable
        if patient.patient_type == 'DD':
            ET.SubElement(enlist_elem, 'pDepPin').text = patient.philhealth_pin
            ET.SubElement(enlist_elem, 'pDepFname').text = patient.first_name
            ET.SubElement(enlist_elem, 'pDepMname').text = patient.middle_name or ''
            ET.SubElement(enlist_elem, 'pDepLname').text = patient.last_name
            ET.SubElement(enlist_elem, 'pDepBdate').text = patient.birth_date.strftime('%Y-%m-%d')
            ET.SubElement(enlist_elem, 'pDepSex').text = patient.gender
            ET.SubElement(enlist_elem, 'pRelCode').text = patient.relationship_code
        
        ET.SubElement(enlist_elem, 'pReportStatus').text = enlistment.report_status
        
        # Add Profile (FPE) if exists
        if hasattr(enlistment, 'profile'):
            self._add_profile(enlist_elem, enlistment.profile)
        
        # Add clinical data for second tranche
        if include_clinical:
            self._add_consultations(enlist_elem, enlistment)
            self._add_medicines(enlist_elem, enlistment)
    
    def _add_profile(self, parent: ET.Element, profile: Profile):
        """Add PROFILE element with medical history, family history, vitals"""
        profile_elem = ET.SubElement(parent, 'PROFILE')
        
        ET.SubElement(profile_elem, 'pHciTransNo').text = profile.hci_trans_no
        ET.SubElement(profile_elem, 'pProfDate').text = profile.profile_date.strftime('%Y-%m-%d')
        ET.SubElement(profile_elem, 'pPatientPin').text = profile.patient_pin
        ET.SubElement(profile_elem, 'pPatientType').text = profile.patient_type
        ET.SubElement(profile_elem, 'pPatientAge').text = str(profile.patient_age)
        ET.SubElement(profile_elem, 'pMemPin').text = profile.member_pin
        ET.SubElement(profile_elem, 'pEffYear').text = profile.effectivity_year
        ET.SubElement(profile_elem, 'pATC').text = profile.atc
        ET.SubElement(profile_elem, 'pIsWalkedIn').text = 'Y' if profile.is_walked_in else 'N'
        ET.SubElement(profile_elem, 'pTransDate').text = profile.transaction_date.strftime('%Y-%m-%d')
        ET.SubElement(profile_elem, 'pReportStatus').text = profile.report_status
        
        # Medical History
        for med_hist in profile.medical_history.all():
            self._add_medical_history(profile_elem, med_hist)
        
        # Family History
        for fam_hist in profile.family_history.all():
            self._add_family_history(profile_elem, fam_hist)
        
        # Social History
        if hasattr(profile, 'social_history'):
            self._add_social_history(profile_elem, profile.social_history)
        
        # Vital Signs
        for vitals in profile.vital_signs.all():
            self._add_vital_signs(profile_elem, vitals)
    
    def _add_medical_history(self, parent: ET.Element, med_hist: MedicalHistory):
        """Add MEDHIST element"""
        elem = ET.SubElement(parent, 'MEDHIST')
        ET.SubElement(elem, 'pMdiseaseCode').text = med_hist.disease_code.code
        ET.SubElement(elem, 'pReportStatus').text = med_hist.report_status
    
    def _add_family_history(self, parent: ET.Element, fam_hist: FamilyHistory):
        """Add FAMHIST element"""
        elem = ET.SubElement(parent, 'FAMHIST')
        ET.SubElement(elem, 'pFdiseaseCode').text = fam_hist.disease_code.code
        ET.SubElement(elem, 'pReportStatus').text = fam_hist.report_status
    
    def _add_social_history(self, parent: ET.Element, social: SocialHistory):
        """Add SOCIALHIST element"""
        elem = ET.SubElement(parent, 'SOCIALHIST')
        ET.SubElement(elem, 'pSmokingStatus').text = social.smoking_status or ''
        ET.SubElement(elem, 'pAlcoholStatus').text = social.alcohol_status or ''
        ET.SubElement(elem, 'pReportStatus').text = social.report_status
    
    def _add_vital_signs(self, parent: ET.Element, vitals: VitalSigns):
        """Add VITALSIGNS element"""
        elem = ET.SubElement(parent, 'VITALSIGNS')
        ET.SubElement(elem, 'pBP_Systolic').text = str(vitals.bp_systolic or '')
        ET.SubElement(elem, 'pBP_Diastolic').text = str(vitals.bp_diastolic or '')
        ET.SubElement(elem, 'pHeight').text = str(vitals.height_cm or '')
        ET.SubElement(elem, 'pWeight').text = str(vitals.weight_kg or '')
        ET.SubElement(elem, 'pBMI').text = str(vitals.bmi or '')
        ET.SubElement(elem, 'pReportStatus').text = vitals.report_status
    
    def _add_consultations(self, parent: ET.Element, enlistment: Enlistment):
        """Add SOAP elements for second tranche"""
        from doctor.models import Consultation
        
        for consult in enlistment.consultations.filter(status='COMPLETED'):
            soap_elem = ET.SubElement(parent, 'SOAP')
            ET.SubElement(soap_elem, 'pHciTransNo').text = consult.hci_trans_no or ''
            ET.SubElement(soap_elem, 'pConsultDate').text = (
                consult.consultation_date.strftime('%Y-%m-%d') 
                if consult.consultation_date else ''
            )
            ET.SubElement(soap_elem, 'pSubjective').text = consult.subjective or ''
            ET.SubElement(soap_elem, 'pObjective').text = consult.objective or ''
            ET.SubElement(soap_elem, 'pAssessment').text = consult.assessment or ''
            ET.SubElement(soap_elem, 'pPlan').text = consult.plan or ''
            ET.SubElement(soap_elem, 'pATC').text = consult.atc or ''
            ET.SubElement(soap_elem, 'pIsWalkedIn').text = 'Y' if consult.is_walked_in else 'N'
            ET.SubElement(soap_elem, 'pReportStatus').text = consult.report_status
    
    def _add_medicines(self, parent: ET.Element, enlistment: Enlistment):
        """Add ESSENTIALMED elements for second tranche"""
        from doctor.models import Prescription
        
        prescriptions = Prescription.objects.filter(
            consultation__enlistment=enlistment,
            quantity_dispensed__gt=0
        )
        
        for rx in prescriptions:
            med_elem = ET.SubElement(parent, 'ESSENTIALMED')
            
            drug_code = rx.medicine.philhealth_drug_code
            if drug_code:
                ET.SubElement(med_elem, 'pDrugCode').text = drug_code.code
                ET.SubElement(med_elem, 'pGenericName').text = drug_code.generic_name
                ET.SubElement(med_elem, 'pStrength').text = drug_code.strength
                ET.SubElement(med_elem, 'pForm').text = drug_code.form
            else:
                ET.SubElement(med_elem, 'pDrugCode').text = ''
                ET.SubElement(med_elem, 'pGenericName').text = rx.medicine.name
                ET.SubElement(med_elem, 'pStrength').text = rx.medicine.strength or ''
                ET.SubElement(med_elem, 'pForm').text = rx.medicine.form or ''
            
            ET.SubElement(med_elem, 'pQuantity').text = str(rx.quantity_dispensed)
            ET.SubElement(med_elem, 'pDispenseDate').text = (
                rx.dispense_date.strftime('%Y-%m-%d') if rx.dispense_date else ''
            )
            ET.SubElement(med_elem, 'pReportStatus').text = rx.report_status
    
    # ═══════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _get_enlistments_for_period(self, year_month: str) -> QuerySet:
        """Get enlistments for a specific month"""
        year, month = year_month.split('-')
        return Enlistment.objects.filter(
            facility=self.facility,
            effectivity_year=year,
            enlistment_date__month=int(month),
            enlistment_status='1',
            profile__isnull=False
        ).select_related('patient', 'profile')
    
    def _get_enlistments_for_year(self, year: str) -> QuerySet:
        """Get all enlistments for a year"""
        return Enlistment.objects.filter(
            facility=self.facility,
            effectivity_year=year,
            enlistment_status='1'
        ).select_related('patient', 'profile')
    
    def _to_string(self, root: ET.Element) -> str:
        """Convert XML element to formatted string"""
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding=None)
```

---

## STEP 3: TransmittalReport Model

**Add to `philhealth/models.py`:**

```python
class TransmittalReport(models.Model):
    """
    Tracks XML report submissions to PhilHealth.
    
    Records the status of each submission from generation
    through validation to final submission.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Generation'),
        ('GENERATED', 'XML Generated'),
        ('VALIDATING', 'Validating'),
        ('VALIDATED', 'Validated'),
        ('VALIDATION_FAILED', 'Validation Failed'),
        ('SUBMITTING', 'Submitting'),
        ('SUBMITTED', 'Submitted'),
        ('SUBMISSION_FAILED', 'Submission Failed'),
    ]
    
    TRANCHE_CHOICES = [
        ('1', 'First Tranche'),
        ('2', 'Second Tranche'),
    ]
    
    facility = models.ForeignKey(
        HealthCareInstitution,
        on_delete=models.CASCADE,
        related_name='transmittal_reports'
    )
    
    transmittal_id = models.CharField(
        max_length=21,
        unique=True,
        help_text="R + AccreNo(9) + YYYYMM + 5digits"
    )
    
    report_tagging = models.CharField(
        max_length=1,
        choices=TRANCHE_CHOICES
    )
    
    year_month = models.CharField(
        max_length=7,
        help_text="YYYY-MM format"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # XML Data
    raw_xml = models.TextField(
        blank=True,
        help_text="Unencrypted XML for reference"
    )
    
    # PhilHealth Response
    transaction_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Transaction number from PhilHealth"
    )
    
    validation_response = models.TextField(
        blank=True,
        help_text="Full validation response"
    )
    
    error_message = models.TextField(
        blank=True
    )
    
    # Counts
    enlistment_count = models.IntegerField(default=0)
    profile_count = models.IntegerField(default=0)
    consultation_count = models.IntegerField(default=0)
    
    # Timestamps
    generated_at = models.DateTimeField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transmittal_id} - {self.status}"
```

---

## Phase 4 Checklist

| Component | Purpose | Status |
|-----------|---------|--------|
| **PKAClient** | Main API client class | □ |
| **get_token** | Authentication (GTM) | □ |
| **is_member_registered** | Member validation (MDRC) | □ |
| **is_atc_valid** | ATC validation (ATCV) | □ |
| **validate_report** | Report validation (VKR) | □ |
| **submit_report** | Report submission (SKR) | □ |
| **KonsultaXMLGenerator** | XML report generation | □ |
| **TransmittalReport** | Submission tracking model | □ |

---

## What's Next?

**Phase 5** will cover:
- eKAS/ePresS document generation
- Laboratory results tracking
- Testing and certification preparation
- Deployment checklist

---

*Phase 4 Complete - Proceed to Phase 5: Documents & Certification*
