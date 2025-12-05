# Preventive Care Tracker

## Purpose

Providers need a simple way to track when USPSTF-recommended preventive care screenings were last completed for their patients. This plugin provides a lightweight, questionnaire-based solution for recording and viewing screening dates in a centralized location.

## Why This Approach?

This plugin uses a **questionnaire-only approach** rather than attempting to automatically extract screening dates from the medical record. Here's why:

**Benefits:**
- ✅ **Simple and reliable**: Providers explicitly record screening dates - no complex data mining required
- ✅ **Flexible**: Works regardless of where/how the screening was originally documented
- ✅ **Low maintenance**: No protocol logic that needs updating as guidelines change
- ✅ **Transparent**: Shows exactly what providers have recorded, no hidden logic

**Trade-offs:**
- Requires manual data entry via questionnaire
- Doesn't automatically detect screenings from labs, vitals, or imaging reports
- Best suited for practices that want explicit tracking rather than automatic inference

## How It Works

### For Providers

1. **Recording Screening Dates**: Submit the "Preventive Care Screening Dates" questionnaire for a patient
   - Enter the date each screening was last completed
   - Leave blank any screenings not yet done
   - Can submit multiple times - the app will show the most recent date for each screening

2. **Viewing Screening History**: Open the "Preventive Care Tracker" application from the patient chart
   - See all 9 USPSTF screening types in one table
   - Shows "Never" for screenings not yet recorded
   - Displays patient name and age for context

### Data Aggregation Logic

**Key Feature**: The app intelligently aggregates data across ALL questionnaire submissions:

- If a provider submits the questionnaire on 10/1/2024 with just hypertension and depression dates
- Then submits again on 11/1/2024 with just diabetes and an updated hypertension date
- The app will show the 11/1 hypertension date (most recent) PLUS the 10/1 depression date (only submission) PLUS the 11/1 diabetes date

This means providers can fill out the questionnaire incrementally without losing previous data.

## Supported Screenings

Based on USPSTF Grade A and B recommendations:

1. **Hypertension Screening** - Blood pressure monitoring
2. **Depression Screening** - PHQ-2/PHQ-9 or similar tools
3. **Alcohol Use Screening** - AUDIT-C or similar
4. **Colorectal Cancer Screening** - Colonoscopy, FIT, Cologuard, etc.
5. **Breast Cancer Screening** - Mammography
6. **Cervical Cancer Screening** - Pap smear, HPV testing
7. **Diabetes Screening** - HbA1c, fasting glucose
8. **Lung Cancer Screening** - Low-dose CT for high-risk patients
9. **Statin/CVD Prevention** - Lipid panel, ASCVD risk assessment

## Technical Implementation

### Architecture
- **Application Handler**: `PreventiveCareTrackerApp` - Displays screening dashboard in right chart pane
- **Questionnaire**: `preventive_care_dates.yml` - Date input form with 9 fields mapped to screening codes
- **Data Source**: Canvas `Command` objects (questionnaire submissions)

### Key Design Decisions

**1. Questionnaire Storage**
- Screening dates are stored in questionnaire `Command` objects with coded questions
- Each question has a unique code (e.g., `HYPERTENSION_DATE`, `DEPRESSION_DATE`)
- Makes it easy to query and aggregate data

**2. Smart Date Aggregation**
- App queries ALL questionnaire submissions for the patient
- Parses dates and keeps the most recent date for each screening type
- Handles multiple date formats: MM/DD/YYYY, MM/DD/YY, YYYY-MM-DD, MM-DD-YYYY, MM/YYYY

**3. Canvas-Branded UI**
- Teal gradient header (#1b9aaa → #16808e) matching Canvas brand
- Clean table with alternating row colors for readability
- Responsive typography using system font stack

### Test Coverage

- **96% code coverage** with 19 comprehensive tests
- Tests cover date parsing, data aggregation, error handling, and UI rendering
- All edge cases tested (empty data, invalid dates, missing patients, etc.)

## Development

### Running Tests
```bash
uv run pytest tests/ --cov=preventive_care_tracker
```

### Deployment
```bash
# Install to a Canvas instance
uv run canvas install preventive_care_tracker --host <instance-name>

# View logs
uv run canvas logs --host <instance-name>
```

### File Structure
```
preventive_care_tracker/
├── CANVAS_MANIFEST.json                    # Plugin configuration
├── applications/
│   ├── __init__.py
│   └── simple_preventive_care_app.py      # Main application handler
├── templates/
│   └── preventive_care_dates.yml          # Questionnaire definition
└── tests/
    └── test_application.py                # Unit tests (96% coverage)
```

## Limitations & Future Enhancements

### Current Limitations
- Manual data entry required (no automatic extraction from EHR data)
- No date validation against patient age/sex appropriateness
- No reminders or alerts for overdue screenings
- No integration with quality measures or reporting

### Potential Future Enhancements
- Add protocol logic to suggest overdue screenings based on age/sex
- Integrate with existing screening documentation (labs, imaging, procedures)
- Add visual indicators for overdue vs. up-to-date screenings
- Generate quality measure reports for practice-wide screening compliance

## Version History

**v1.1.0** (Current)
- Simplified to questionnaire-only approach
- Smart aggregation across multiple questionnaire submissions
- Canvas-branded UI redesign
- Production-ready logging
- 96% test coverage

## Support

For issues or questions about this plugin, contact the General Primary Care plugin development team.
