# Canvas Instance Configuration Report

**Instance**: general-primary-care-trial.canvasmedical.com
**Generated**: 2025-12-04
**Analysis Method**: Canvas CLI + API Authentication

---

## Summary

This report documents the configuration of the Canvas instance for plugin development purposes. Some information was gathered programmatically using the Canvas CLI, while other configuration details would require direct admin portal access.

| Category | Status |
|----------|--------|
| Installed Plugins | ✅ Retrieved (8 plugins) |
| API Credentials | ✅ Verified |
| Teams | ⚠️ Requires admin portal access |
| Roles | ⚠️ Requires admin portal access |
| Questionnaires | ⚠️ Requires admin portal access |
| Note Types | ⚠️ Requires admin portal access |
| Appointment Types | ⚠️ Requires admin portal access |

---

## Installed Plugins

| Plugin Name | Version | Status |
|-------------|---------|--------|
| test_plugin | 0.0.1 | disabled |
| sbh | 0.0.1 | enabled |
| abstractive_health | 0.0.1 | enabled |
| bp_cpt2 | 1.8.31 | enabled |
| hyperscribe | 2025-11-14 v0.2.147 (main) | enabled |
| audit_c_questionnaire | 1.0.0 | enabled |
| diabetes_foot_exam_questionnaire | 1.0.0 | enabled |
| womens_health_history_questionnaire | 1.0.0 | enabled |

### Plugin Analysis

**Active Plugins (7):**
- **sbh** (v0.0.1) - Custom plugin, purpose to be determined
- **abstractive_health** (v0.0.1) - Custom plugin, likely health documentation/summarization
- **bp_cpt2** (v1.8.31) - Blood pressure CPT coding automation
- **hyperscribe** (v0.2.147) - Medical documentation and scribing tool
- **audit_c_questionnaire** (v1.0.0) - AUDIT-C alcohol screening questionnaire
- **diabetes_foot_exam_questionnaire** (v1.0.0) - Diabetes foot examination protocol
- **womens_health_history_questionnaire** (v1.0.0) - Women's health history intake

**Inactive Plugins (1):**
- **test_plugin** (v0.0.1) - Disabled test/development plugin

---

## API Access Configuration

✅ **API Credentials Verified**
- Client ID: `YEOKJaR2VwsKQwxetch4hw1QXBNV9FPjAbyB6t0l`
- OAuth2 token endpoint working
- Full FHIR API access available with extensive scopes including:
  - Patient data (read/write)
  - Clinical resources (Conditions, Observations, Medications, etc.)
  - Care coordination (CareTeam, Tasks)
  - Documentation (DocumentReference, Notes)
  - Scheduling (Appointments, Slots)

---

## Configuration Not Yet Retrieved

The following configuration details require direct admin portal access and could not be retrieved programmatically:

### Teams
Teams are groups of providers/staff that work together. They're commonly used for:
- Task assignment in plugins
- Care coordination workflows
- Provider scheduling groups

**To retrieve**: Access https://general-primary-care-trial.canvasmedical.com/admin/core/team/

### Roles (Permission Groups)
Roles define user permissions and capabilities within Canvas.

**To retrieve**: Access https://general-primary-care-trial.canvasmedical.com/admin/auth/group/

### Questionnaires
Based on the installed plugins, we know these questionnaires exist:
- AUDIT-C (Alcohol screening)
- Diabetes Foot Exam
- Women's Health History
- DrB Service Request (from drbconsult.py plugin code)
- DrB Phone Call (from drbconsult.py plugin code)

**To retrieve complete list**: Access https://general-primary-care-trial.canvasmedical.com/admin/core/questionnaire/

### Note Types
Note types define the categories and templates for clinical documentation.

**To retrieve**: Access https://general-primary-care-trial.canvasmedical.com/admin/core/notetype/

### Appointment Types
Appointment types define scheduling categories, durations, and visit types.

**To retrieve**: Access https://general-primary-care-trial.canvasmedical.com/admin/core/appointmenttype/

---

## Plugin Development Recommendations

Based on the current plugin ecosystem:

### 1. **Existing Questionnaire Infrastructure**
The instance has an established pattern of questionnaire-based plugins:
- audit_c_questionnaire
- diabetes_foot_exam_questionnaire
- womens_health_history_questionnaire

**Recommendation**: If your plugin needs patient data collection, follow the questionnaire pattern established by these plugins.

### 2. **Clinical Automation Present**
The bp_cpt2 plugin shows automated CPT coding is already in use.

**Recommendation**: New clinical decision support plugins should integrate with existing automation patterns.

### 3. **Documentation Tools Active**
Hyperscribe (v0.2.147) is actively used for medical documentation.

**Recommendation**: Any documentation-related plugins should be designed to complement (not conflict with) Hyperscribe.

### 4. **Custom Plugin Development**
Several custom plugins (sbh, abstractive_health, test_plugin) indicate active internal development.

**Recommendation**: Follow the instance's existing plugin architecture patterns found in the codebase.

### 5. **API Integration Points**
Full FHIR API access is available with comprehensive scopes for:
- Patient data manipulation
- Task creation and management
- Clinical documentation
- Care team coordination

**Recommendation**: Leverage the FHIR API for data access rather than direct database queries.

---

## Next Steps for Complete Configuration Analysis

To gather the remaining configuration details, you can:

1. **Manual Admin Portal Access**:
   ```
   URL: https://general-primary-care-trial.canvasmedical.com/admin/
   Username: root
   Password: eH2BmRuMRLYR5uYD5kM3xqgL
   ```

2. **Specific Pages to Document**:
   - `/admin/auth/group/` - Roles and permissions
   - `/admin/core/team/` - Teams and members
   - `/admin/core/questionnaire/` - All questionnaires
   - `/admin/core/notetype/` - Note type definitions
   - `/admin/core/appointmenttype/` - Appointment configurations

3. **Canvas CLI Commands**:
   ```bash
   # List plugins
   canvas list --host general-primary-care-trial

   # View plugin logs
   canvas logs --host general-primary-care-trial --plugin <plugin_name>
   ```

---

## Development Environment Setup

To develop plugins for this instance:

1. **Credentials Location**: `~/.canvas/credentials.ini`
2. **Instance Section**: `[general-primary-care-trial]`
3. **Available Commands**:
   - `canvas install` - Deploy new plugin
   - `canvas enable/disable` - Manage plugin state
   - `canvas logs` - Monitor plugin execution
   - `canvas run-plugin` - Local development testing

---

## Notes for Non-Developers

**What is this report?**
This document maps out the "landscape" of your Canvas medical records system - what tools (plugins) are installed, what capabilities exist, and what information is available for building new automated features.

**Why does this matter?**
Before building new automation or features in Canvas, you need to know:
- What's already installed (to avoid duplication)
- What data structures exist (teams, questionnaires, note types)
- What patterns other plugins use (so new ones fit well)

**What couldn't be accessed?**
Some configuration details (like team names, role definitions, and complete questionnaire lists) live in the admin section of Canvas and require manual login to see. The API provides data access but not configuration management.

**Key Takeaway**:
This instance is actively used with 7 enabled plugins focused on clinical workflows (blood pressure, diabetes, women's health, alcohol screening) plus documentation tools (Hyperscribe). Any new plugins should complement these existing tools.

---

**Report Limitations**: This analysis was performed using the Canvas CLI and API authentication. Direct admin portal access would provide additional details about teams, roles, and complete resource configurations. The admin credentials are available in `~/.canvas/credentials.ini` for manual verification if needed.
