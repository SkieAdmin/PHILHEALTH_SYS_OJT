# COMPREHENSIVE DJANGO SECURITY AUDIT REPORT
## PhilHealth eKonsulta Project
**Date:** December 20, 2025
**Auditor:** Claude Code Security Scanner

---

## EXECUTIVE SUMMARY

This security audit identified **23 vulnerabilities** across the PhilHealth eKonsulta Django application:
- **3 CRITICAL** issues requiring immediate attention
- **6 HIGH** severity issues
- **12 MEDIUM** severity issues
- **2 LOW** severity issues

---

## CRITICAL FINDINGS

### 1. HARDCODED CREDENTIALS AND SECRETS (CRITICAL)

**File:** `philhealth_eKonsulta/settings.py`

| Issue | Line | Value |
|-------|------|-------|
| Exposed SECRET_KEY | 23 | `'django-insecure-t6l*-(@i&a9c-7@sp_4j*(e%^+6757&w&_z7wcx6x97re&()$x'` |
| Docker DB Password | 94 | `'admin123'` |
| Live DB Password | 106 | `'password123'` |
| Windows DB Password | 118 | `'password1'` |

**Impact:** Anyone with access to the repository can compromise the database and session encryption.

**Recommendation:** Move all credentials to environment variables using python-dotenv.

---

### 2. DEBUG MODE ENABLED IN PRODUCTION (CRITICAL)

**File:** `philhealth_eKonsulta/settings.py`
**Line:** 26

```python
DEBUG = True
```

**Impact:** Exposes sensitive information in error pages including:
- Database queries
- Environment variables
- Full stack traces
- Django settings

**Recommendation:** Set `DEBUG = False` in production and use environment variable.

---

### 3. EMPTY ALLOWED_HOSTS (CRITICAL)

**File:** `philhealth_eKonsulta/settings.py`
**Line:** 30

```python
ALLOWED_HOSTS = []
```

**Impact:** Vulnerable to Host header injection attacks.

**Recommendation:** Add specific hostnames: `ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourdomain.com']`

---

## HIGH SEVERITY FINDINGS

### 4. DISABLED PASSWORD VALIDATORS (HIGH)

**File:** `philhealth_eKonsulta/settings.py`
**Lines:** 128-141

All password validators are commented out, allowing:
- Empty passwords
- Short passwords (e.g., "123")
- Common passwords (e.g., "password")
- Numeric-only passwords

**Recommendation:** Uncomment all validators in AUTH_PASSWORD_VALIDATORS.

---

### 5. MISSING ACCESS CONTROL - PATIENT DATA (HIGH)

**File:** `secretary/views.py`

| Function | Line | Issue |
|----------|------|-------|
| `patient_detail()` | 126 | No `@login_required` decorator |
| `delete_patient_document()` | 131-137 | No authentication/authorization |
| `delete_patient_picture()` | 140-146 | No authentication/authorization |

**Impact:** Any unauthenticated user can:
- View all patient records
- Delete patient medical documents
- Delete patient pictures

**Recommendation:** Add `@login_required` decorator and role verification.

---

### 6. MISSING ACCESS CONTROL - APPOINTMENTS (HIGH)

**File:** `secretary/views.py`

| Function | Line | Issue |
|----------|------|-------|
| `appointment_list()` | 152 | No login required |
| `appointment_create()` | 156 | No authentication |
| `appointment_update()` | 171 | No authentication |
| `appointment_delete()` | 179 | No authentication |

**Impact:** Unauthenticated users can view, create, modify, and delete all appointments.

**Recommendation:** Add `@login_required` decorator to all functions.

---

### 7. INSECURE INPUT HANDLING - USER REGISTRATION (HIGH)

**File:** `login/views.py`
**Lines:** 301-308, 341-348

```python
username = request.POST["username"]  # KeyError if missing
password = request.POST["password"]
```

**Impact:** Application crashes with KeyError if form fields are missing.

**Recommendation:** Use `request.POST.get('field', '')` with proper validation.

---

## MEDIUM SEVERITY FINDINGS

### 8. MASS ASSIGNMENT VULNERABILITY

**File:** `secretary/forms.py`
**Line:** 9

```python
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
```

**Impact:** All model fields exposed to mass assignment.

**Recommendation:** Explicitly list allowed fields.

---

### 9. INSUFFICIENT INPUT VALIDATION - TYPE CASTING

**File:** `doctor/views.py` - Line 159
```python
quantity=int(quantity),  # No bounds checking
```

**File:** `finance/views.py` - Line 161
```python
amount = Decimal(request.POST.get('amount', '0'))  # No validation
```

**Impact:** Negative quantities, extremely large values, or invalid formats accepted.

**Recommendation:** Add validation for range and format.

---

### 10. UNVALIDATED STATUS PARAMETER

**Files:** `doctor/views.py` (Lines 19-28), `finance/views.py` (Lines 76-81)

Status filter from GET parameter used without validation against allowed values.

**Recommendation:** Validate against a whitelist of allowed status values.

---

### 11. UNVALIDATED FILE UPLOADS

**File:** `secretary/views.py` - Lines 39-47, 84-92

```python
if 'document' in request.FILES:
    doc = request.FILES['document']
    # No file size check
    # No file type validation
    PatientDocument.objects.create(...)
```

**Impact:**
- Users can upload files of any size (DoS risk)
- Any file type accepted, including executables
- No protection against malicious files

**Recommendation:** Add file size limits, whitelist allowed extensions, implement virus scanning.

---

### 12. INSECURE JSON PARSING

**File:** `doctor/views.py` - Lines 145-163

```python
try:
    prescriptions_list = json.loads(prescriptions_json)
except json.JSONDecodeError:
    pass  # Silently ignores errors
```

**Impact:** Silently fails with no logging or user feedback.

**Recommendation:** Add proper error handling and logging.

---

### 13. MISSING ROLE-BASED ACCESS CONTROL

**File:** `doctor/views.py` - Lines 212-248
```python
def my_patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)  # No access control
```

**File:** `finance/views.py` - Lines 56-119
```python
@login_required
def billing_list(request):
    # No check if user.role == 'FINANCE'
```

**Impact:** Users with valid login but wrong role can access sensitive data.

**Recommendation:** Add role verification: `if request.user.role != "EXPECTED_ROLE": return HttpResponseForbidden()`

---

### 14. INSECURE DIRECT OBJECT REFERENCES (IDOR)

**File:** `doctor/views.py` - Lines 213-214

```python
patient = get_object_or_404(Patient, id=patient_id)  # Any doctor can view any patient
```

**Recommendation:** Add ownership verification before allowing access.

---

### 15. INCONSISTENT ERROR HANDLING - REGISTRATION

**File:** `login/views.py`

`secretary_registration` (Lines 301-327) lacks duplicate username/email checks that exist in `doctor_registration` (Lines 241-290).

**Recommendation:** Add consistent validation across all registration functions.

---

### 16. MISSING PATIENT FORM VALIDATION

**File:** `secretary/forms.py` - Lines 6-12

No validation for:
- Contact number format
- Future birth dates
- Medical history length

**Recommendation:** Add custom validators for business rules.

---

## LOW SEVERITY FINDINGS

### 17. INSECURE DEFAULT FILE UPLOAD PATH

**File:** `secretary/models.py` - Lines 12-22

Files stored in web-accessible media directory with original extension preserved.

**Recommendation:** Store files outside web root, validate extensions, use content-type verification.

---

### 18. XSS VULNERABILITY POTENTIAL

**File:** `login/templates/login/list_users.html` - Line 24

While Django auto-escapes by default, explicit escaping is recommended.

**Recommendation:** Use `|escape` filter explicitly for user-controlled content.

---

## SUMMARY TABLE

| # | Vulnerability | Severity | File | Line(s) |
|---|---------------|----------|------|---------|
| 1 | Hardcoded SECRET_KEY | CRITICAL | settings.py | 23 |
| 2 | Hardcoded DB Credentials | CRITICAL | settings.py | 94, 106, 118 |
| 3 | DEBUG=True | CRITICAL | settings.py | 26 |
| 4 | Empty ALLOWED_HOSTS | HIGH | settings.py | 30 |
| 5 | Disabled Password Validators | HIGH | settings.py | 128-141 |
| 6 | No Auth - Patient Detail | HIGH | secretary/views.py | 126 |
| 7 | No Auth - Delete Documents | HIGH | secretary/views.py | 131-146 |
| 8 | No Auth - Appointments | HIGH | secretary/views.py | 152-184 |
| 9 | Insecure Input Handling | HIGH | login/views.py | 301-348 |
| 10 | Mass Assignment | MEDIUM | secretary/forms.py | 9 |
| 11 | No Validation - Quantity | MEDIUM | doctor/views.py | 159 |
| 12 | No Validation - Amount | MEDIUM | finance/views.py | 161 |
| 13 | No File Size Validation | MEDIUM | secretary/views.py | 39-47, 84-92 |
| 14 | No File Type Validation | MEDIUM | secretary/forms.py | 17, 23 |
| 15 | JSON Parse Silent Fail | MEDIUM | doctor/views.py | 145-163 |
| 16 | Missing Role-Based Access | MEDIUM | doctor/views.py | 212-248 |
| 17 | Missing Role Check | MEDIUM | finance/views.py | 56-119 |
| 18 | IDOR - Patient Access | MEDIUM | doctor/views.py | 213-214 |
| 19 | Unvalidated Status | MEDIUM | doctor/views.py | 19-28 |
| 20 | Inconsistent Registration | MEDIUM | login/views.py | 301-327 |
| 21 | No Patient Form Validation | MEDIUM | secretary/forms.py | 6-12 |
| 22 | Insecure File Path | LOW | secretary/models.py | 12-22 |
| 23 | XSS Potential | LOW | list_users.html | 24 |

---

## RECOMMENDATIONS (PRIORITY ORDER)

### Immediate Actions (Do Now)
1. Move all credentials to environment variables (.env file)
2. Set `DEBUG = False` for production
3. Configure proper `ALLOWED_HOSTS`
4. Enable all password validators

### Short-Term (This Week)
5. Add `@login_required` decorators to all secretary views
6. Add role-based authorization checks in all views
7. Add file upload validation (size, type)
8. Fix inconsistent registration error handling

### Medium-Term (This Month)
9. Implement proper error handling and logging
10. Add input validation for all forms
11. Implement IDOR protection
12. Add rate limiting on login

### Long-Term (Future)
13. Implement Content Security Policy headers
14. Enable HTTPS only (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`)
15. Add security headers middleware
16. Implement audit logging for security events

---

## COMPLIANCE NOTES

This application handles **Protected Health Information (PHI)** and should comply with:
- Data Privacy Act of 2012 (Philippines)
- HIPAA guidelines (if applicable)
- OWASP Top 10 security standards

---

*Report generated by Claude Code Security Scanner*
*End of Report*
