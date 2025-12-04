# Preventive Care Gap Identification Plugin

## Overview

A clinical decision support plugin that identifies gaps in preventive care screenings for patients based on USPSTF guidelines. The plugin evaluates 9 key preventive care measures and displays missing screenings in an easy-to-review modal interface.

---

## Problem Statement

Care teams need an efficient way to identify which preventive care screenings a patient is due for during clinical encounters. Currently, this requires manually reviewing each patient's history against multiple screening guidelines, which is time-consuming and prone to oversight.

---

## Solution

A Canvas plugin that:
1. Analyzes patient demographics, medical history, and screening records
2. Evaluates eligibility and compliance for 9 USPSTF preventive care measures
3. Displays all relevant screenings with their status in a patient-scoped application
4. Provides a questionnaire to manually document/override screening dates
5. Accessible via the Canvas app drawer

---

## Users

- **Primary**: Physicians and care team staff (nurses, medical assistants, care coordinators)
- **Secondary**: Administrative staff coordinating preventive care outreach

---

## Technical Implementation

### Handler Type
**Application** - Patient-scoped application in the Canvas app drawer

### Entry Point
Launched from the app drawer when viewing a patient chart

### Components
1. **Protocol Handler**: Responds to questionnaire submissions for manual date entry
2. **Application Handler**: Renders the preventive care tracking interface

---

## Preventive Care Measures

### 1. Colorectal Cancer Screening

**Population**: Adults 45-75 years old

**Screening Criteria**:
- No colonoscopy in past 10 years
- No FIT (Fecal Immunochemical Test) in past 1 year

**Data Queries**:
- **Procedures** (CPT): 45378, 45380-45385, G0121, G0105
- **Lab Results** (LOINC): 29771-3, 56490-6, 57905-2

**USPSTF Grade**: A

---

### 2. Breast Cancer Screening

**Population**: Women 40-74 years old

**Screening Criteria**:
- No mammogram in past 2 years

**Data Queries**:
- **Imaging Reports**: Query completed mammography reports with report dates
- **Procedures** (CPT): 77067, G0202

**USPSTF Grade**: B

---

### 3. Hypertension Screening

**Population**: Adults 18+ years old

**Screening Criteria**:
- No blood pressure reading in past 1 year

**Data Queries**:
- **Vitals/Observations** (LOINC): 8480-6 (systolic), 8462-4 (diastolic), 85354-9 (BP panel)

**USPSTF Grade**: A

---

### 4. Depression Screening

**Population**: All adults (including pregnant/postpartum)

**Screening Criteria**:
- No PHQ-2 or PHQ-9 in past 1 year

**Data Queries**:
- **Lab Results/Questionnaires** (LOINC): 55758-7 (PHQ-2), 44249-1 (PHQ-9), 73831-0 (PHQ-9 panel)

**USPSTF Grade**: B

---

### 5. Prediabetes/Type 2 Diabetes Screening

**Population**: Adults 35-70 years old with BMI ≥25

**Screening Criteria**:
- No HbA1c or fasting glucose in past 3 years

**Data Queries**:
- **BMI Calculation**: From height/weight observations
- **Lab Results** (LOINC): 4548-4 (HbA1c), 1558-6 (fasting glucose), 2345-7 (glucose)

**USPSTF Grade**: B

---

### 6. Lung Cancer Screening

**Population**: Adults 50-80 years old with 20+ pack-year smoking history

**Screening Criteria**:
- No low-dose CT chest in past 1 year

**Data Queries**:
- **Smoking History**: Pack-years calculation from social history
- **Imaging Reports**: Query completed LDCT reports with report dates
- **Procedures** (CPT): 71271, G0296

**USPSTF Grade**: B

---

### 7. Cervical Cancer Screening

**Population**: Women 21-65 years old

**Screening Criteria**:
- Age 21-29: No Pap test in past 3 years
- Age 30-65: No Pap + HPV co-testing in past 5 years OR no HPV testing alone in past 5 years

**Data Queries**:
- **Lab Results** (LOINC): 19762-4 (HPV), 10524-7 (Pap), 21440-3 (HPV 16/18)
- **Procedures** (CPT): 88141-88143, 88174-88175, 87624-87625

**USPSTF Grade**: A

---

### 8. Statin for CVD Prevention

**Population**: Adults 40-75 years old with CVD risk factors and 10-year risk ≥10%

**Risk Factors**:
- Diabetes (ICD-10: E11.x)
- Hypertension (ICD-10: I10)
- Dyslipidemia (ICD-10: E78.x)
- Current smoking

**Screening Criteria**:
- Has qualifying risk factors
- No lipid panel in past 5 years OR
- No active statin prescription

**Data Queries**:
- **Conditions**: ICD-10 codes for diabetes, HTN, dyslipidemia
- **Medications**: Active statin prescriptions (RxNorm)
- **Lab Results** (LOINC): 13457-7 (LDL), 2093-3 (total cholesterol), 80061 (lipid panel)

**USPSTF Grade**: B

---

### 9. Unhealthy Alcohol Use Screening

**Population**: Adults 18+ years old

**Screening Criteria**:
- No AUDIT-C screening in past 1 year

**Data Queries**:
- **Lab Results/Questionnaires** (LOINC): 72109-2 (AUDIT-C), 75626-2 (AUDIT total)

**USPSTF Grade**: B

---

## Application Interface Design

### Title
"Preventive Care Tracker"

### Layout

The application displays a table/list view with all preventive care measures relevant to the patient:

**Table Columns:**
1. **Screening Name** - Name of the preventive care measure
2. **Status** - Visual indicator (✓ Up-to-date, ⚠️ Overdue, — Not Applicable)
3. **Last Date** - Date of most recent screening (from structured data or manual entry)
4. **Due Date** - Next recommended screening date
5. **Grade** - USPSTF recommendation grade

**Filtering:**
- Show only applicable screenings (default)
- Show all screenings including N/A (toggle option)

### Manual Date Entry Section

Below the screening table, provide access to a questionnaire for manual date documentation:

**Questionnaire Button**: "Update Screening Dates"

When clicked, launches a questionnaire with:
- One question per applicable screening
- Free text field to enter date (format: MM/DD/YYYY or MM/YYYY)
- Optional notes field for each screening
- Saves entries as structured data linked to the patient

### Example Display

```
PREVENTIVE CARE TRACKER
Patient: Jane Doe | Age: 52 | Sex: Female
Last Updated: 2025-12-04 10:30 AM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Screening                        Status    Last Date    Due Date     Grade
────────────────────────────────────────────────────────────────────────
Colorectal Cancer Screening      ⚠️        None         Overdue      A
Breast Cancer Screening          ⚠️        03/15/2022   03/15/2024   B
Cervical Cancer Screening        —         N/A          N/A          A
Depression Screening             ⚠️        None         Overdue      B
Diabetes Screening               —         N/A          N/A          B
Hypertension Screening           ✓         11/20/2025   11/20/2026   A
Lung Cancer Screening            —         N/A          N/A          B
Statin for CVD Prevention        —         N/A          N/A          B
Alcohol Use Screening            ✓         06/10/2025   06/10/2026   B

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Update Screening Dates] [Export Report] [Refresh Data]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY
• 2 screenings up-to-date
• 3 screenings overdue
• 4 not applicable to this patient
```

---

## Data Models Used

### Canvas SDK Models
- `Patient`: Demographics (age, sex, birth date)
- `Observation`: Vitals, labs (LOINC codes), BMI
- `Procedure`: Screening procedures (CPT codes)
- `Condition`: Diagnoses (ICD-10 codes)
- `MedicationStatement`: Active prescriptions
- `ImagingReport`: Completed imaging results with dates
- `SocialHistory`: Smoking status and pack-years

---

## Logic Flow

### Application Load Flow

```
1. User opens "Preventive Care Tracker" from app drawer
2. Application handler receives patient_id from context
3. Query patient demographics (age, sex)
4. For each preventive care measure:
   a. Check if patient meets population criteria
   b. If yes, query for relevant screening records (structured data)
   c. Query for manual override dates (from questionnaire responses)
   d. Use most recent date (structured vs. manual)
   e. Calculate next due date based on screening interval
   f. Determine status (up-to-date/overdue/not-applicable)
5. Format results as HTML table
6. Render application interface
```

### Manual Date Entry Flow

```
1. User clicks "Update Screening Dates" button
2. Application launches questionnaire with one question per applicable screening
3. User enters dates in free text fields (MM/DD/YYYY format)
4. User submits questionnaire
5. Protocol handler receives questionnaire submission event
6. Parse and validate date entries
7. Store dates as structured observations or custom data
8. Application refreshes to show updated dates
```

---

## Configuration

### Plugin Settings
- **plugin_name**: `preventive-care-tracker`
- **version**: `1.0.0`
- **handler_types**:
  - `Application` - Main tracking interface
  - `BaseProtocol` - Questionnaire submission handler
- **app_name**: "Preventive Care Tracker"
- **app_description**: "Track and manage preventive care screenings"
- **app_icon**: `care.png` (red hand holding heart logo)

### Questionnaire Configuration
- **questionnaire_name**: "Preventive Care Screening Dates"
- **questions**: One per screening measure (9 total)
- **question_type**: Free text (date entry)
- **validation**: Date format (MM/DD/YYYY or MM/YYYY)

---

## Testing Strategy

### Unit Tests
1. Population criteria evaluation for each measure
2. Date range calculations (1 year, 2 years, 3 years, 5 years, 10 years)
3. LOINC/CPT code matching logic
4. BMI calculation from height/weight observations
5. Pack-year calculation from smoking history
6. Modal content formatting

### Integration Tests
1. Patient with no screenings (all gaps)
2. Patient with all screenings up-to-date
3. Patient with mixed compliance
4. Patients at age boundaries (turning 45, 50, 65, etc.)
5. Male vs. female screening differences
6. Edge cases (missing data, incomplete records)

### Test Data Requirements
- Mock patients across different age ranges
- Mock observation/procedure/condition data with various LOINC/CPT/ICD-10 codes
- Date ranges spanning 0-10+ years

---

## Future Enhancements

### Phase 2 (Post-MVP)
1. **Direct ordering**: Add buttons to order missing screenings from the modal
2. **Care team notifications**: Automatically create tasks for care coordinators
3. **Bulk analysis**: Run gap analysis across patient panels
4. **Custom reminder intervals**: Allow practices to configure screening intervals
5. **Export functionality**: Generate preventive care reports for quality metrics
6. **Historical tracking**: Show trends in gap closure over time

---

## Dependencies

- Canvas SDK (handlers, effects, data models)
- Python 3.11+
- Access to patient demographics, observations, procedures, conditions, medications

---

## Deployment Notes

- Deploy to `general-primary-care-trial` instance
- Target users: Primary care team at General Primary Care
- Enable for all staff roles initially
- Monitor usage and feedback for 2-week UAT period
- Iterate based on clinical workflow feedback

---

## Success Metrics

1. **Adoption**: % of encounters where preventive care is checked
2. **Gap identification**: Average number of gaps identified per patient
3. **Gap closure**: % of identified gaps that result in completed screenings
4. **User satisfaction**: Feedback from care team on usability and accuracy
5. **Performance**: Modal load time < 2 seconds

---

## References

- USPSTF Preventive Care Guidelines: https://www.uspreventiveservicestaskforce.org/
- Canvas SDK Documentation: https://docs.canvasmedical.com/sdk/
- ICD-10, CPT, LOINC code references provided by user
