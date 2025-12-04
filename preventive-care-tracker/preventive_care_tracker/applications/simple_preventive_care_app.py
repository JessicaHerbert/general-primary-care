"""Simplified Preventive Care Tracker Application - All logic inline."""

from datetime import datetime, date, timedelta
from typing import Optional
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.medication import Medication
from logger import log


class PreventiveCareTrackerApp(Application):
    """Preventive Care Tracker application - simplified inline version."""

    def on_open(self) -> Effect | list[Effect]:
        """Handle application open - render preventive care tracking interface."""
        patient_id = self.context.get("patient", {}).get("id")

        if not patient_id:
            error_html = self._render_error("No patient context available.")
            return LaunchModalEffect(
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
                title="Preventive Care Tracker",
                content=error_html
            ).apply()

        try:
            # Get patient
            patient = Patient.objects.get(id=patient_id)

            # Calculate age
            if patient.birth_date:
                today = date.today()
                age = today.year - patient.birth_date.year
                if (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day):
                    age -= 1
            else:
                age = None

            # Get sex
            sex = patient.sex_at_birth if hasattr(patient, 'sex_at_birth') else None

            # Evaluate screenings
            screenings = self._evaluate_screenings(patient, age, sex)

            # Render HTML
            html_content = self._render_html(patient, age, screenings)

            return LaunchModalEffect(
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
                title="Preventive Care Tracker",
                content=html_content
            ).apply()

        except Exception as e:
            log.error(f"Error in PreventiveCareTrackerApp: {str(e)}")
            error_html = self._render_error(f"Error loading patient data: {str(e)}")
            return LaunchModalEffect(
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
                title="Preventive Care Tracker",
                content=error_html
            ).apply()

    def _evaluate_screenings(self, patient: Patient, age: Optional[int], sex: Optional[str]) -> list:
        """Evaluate all preventive care screenings for this patient."""
        screenings = []

        # 1. Hypertension Screening (adults 18+)
        if age and age >= 18:
            last_bp = self._get_last_observation(patient, ["8480-6", "8462-4", "85354-9"])
            screenings.append({
                "name": "Hypertension Screening",
                "status": "up-to-date" if last_bp and self._within_days(last_bp, 365) else "overdue",
                "last_date": last_bp.strftime("%m/%d/%Y") if last_bp else "Never",
                "grade": "A",
                "applicable": True
            })
        else:
            screenings.append({
                "name": "Hypertension Screening",
                "status": "not-applicable",
                "last_date": "N/A",
                "grade": "A",
                "applicable": False
            })

        # 2. Depression Screening (adults 18+)
        if age and age >= 18:
            last_phq = self._get_last_observation(patient, ["55758-7", "44249-1", "73831-0"])
            screenings.append({
                "name": "Depression Screening",
                "status": "up-to-date" if last_phq and self._within_days(last_phq, 365) else "overdue",
                "last_date": last_phq.strftime("%m/%d/%Y") if last_phq else "Never",
                "grade": "B",
                "applicable": True
            })
        else:
            screenings.append({
                "name": "Depression Screening",
                "status": "not-applicable",
                "last_date": "N/A",
                "grade": "B",
                "applicable": False
            })

        # 3. Alcohol Use Screening (adults 18+)
        if age and age >= 18:
            last_audit = self._get_last_observation(patient, ["72109-2", "75626-2"])
            screenings.append({
                "name": "Alcohol Use Screening",
                "status": "up-to-date" if last_audit and self._within_days(last_audit, 365) else "overdue",
                "last_date": last_audit.strftime("%m/%d/%Y") if last_audit else "Never",
                "grade": "B",
                "applicable": True
            })
        else:
            screenings.append({
                "name": "Alcohol Use Screening",
                "status": "not-applicable",
                "last_date": "N/A",
                "grade": "B",
                "applicable": False
            })

        # 4. Colorectal Cancer Screening (ages 45-75)
        if age and 45 <= age <= 75:
            last_colo = self._get_last_observation(patient, ["29771-3", "56490-6", "57905-2"])
            screenings.append({
                "name": "Colorectal Cancer Screening",
                "status": "up-to-date" if last_colo and self._within_days(last_colo, 365) else "overdue",
                "last_date": last_colo.strftime("%m/%d/%Y") if last_colo else "Never",
                "grade": "A",
                "applicable": True
            })
        else:
            screenings.append({
                "name": "Colorectal Cancer Screening",
                "status": "not-applicable",
                "last_date": "N/A",
                "grade": "A",
                "applicable": False
            })

        # 5. Breast Cancer Screening (women 40-74)
        if age and 40 <= age <= 74 and sex and sex.lower() == "female":
            last_mammo = self._get_last_imaging(patient, "mammogr")
            screenings.append({
                "name": "Breast Cancer Screening",
                "status": "up-to-date" if last_mammo and self._within_days(last_mammo, 730) else "overdue",
                "last_date": last_mammo.strftime("%m/%d/%Y") if last_mammo else "Never",
                "grade": "B",
                "applicable": True
            })
        else:
            screenings.append({
                "name": "Breast Cancer Screening",
                "status": "not-applicable",
                "last_date": "N/A",
                "grade": "B",
                "applicable": False
            })

        # 6. Cervical Cancer Screening (women 21-65)
        if age and 21 <= age <= 65 and sex and sex.lower() == "female":
            last_pap = self._get_last_observation(patient, ["19762-4", "10524-7", "21440-3"])
            screenings.append({
                "name": "Cervical Cancer Screening",
                "status": "up-to-date" if last_pap and self._within_days(last_pap, 1095) else "overdue",
                "last_date": last_pap.strftime("%m/%d/%Y") if last_pap else "Never",
                "grade": "A",
                "applicable": True
            })
        else:
            screenings.append({
                "name": "Cervical Cancer Screening",
                "status": "not-applicable",
                "last_date": "N/A",
                "grade": "A",
                "applicable": False
            })

        # 7. Diabetes Screening (ages 35-70) - simplified without BMI check
        if age and 35 <= age <= 70:
            last_a1c = self._get_last_observation(patient, ["4548-4", "1558-6", "2345-7"])
            screenings.append({
                "name": "Diabetes Screening",
                "status": "up-to-date" if last_a1c and self._within_days(last_a1c, 1095) else "overdue",
                "last_date": last_a1c.strftime("%m/%d/%Y") if last_a1c else "Never",
                "grade": "B",
                "applicable": True
            })
        else:
            screenings.append({
                "name": "Diabetes Screening",
                "status": "not-applicable",
                "last_date": "N/A",
                "grade": "B",
                "applicable": False
            })

        # 8. Lung Cancer Screening (ages 50-80) - simplified without smoking check
        screenings.append({
            "name": "Lung Cancer Screening",
            "status": "not-applicable",
            "last_date": "N/A",
            "grade": "B",
            "applicable": False,
            "notes": "Requires smoking history"
        })

        # 9. Statin for CVD Prevention (ages 40-75) - simplified
        screenings.append({
            "name": "Statin for CVD Prevention",
            "status": "not-applicable",
            "last_date": "N/A",
            "grade": "B",
            "applicable": False,
            "notes": "Requires risk assessment"
        })

        return screenings

    def _get_last_observation(self, patient: Patient, loinc_codes: list) -> Optional[date]:
        """Get the most recent observation date for any of the given LOINC codes."""
        try:
            observations = Observation.objects.filter(patient=patient).order_by('-effective_datetime')
            for obs in observations:
                if hasattr(obs, 'codings'):
                    for coding in obs.codings.all():
                        if coding.code in loinc_codes:
                            if obs.effective_datetime:
                                return obs.effective_datetime.date() if hasattr(obs.effective_datetime, 'date') else obs.effective_datetime
            return None
        except Exception as e:
            log.error(f"Error getting observations: {str(e)}")
            return None

    def _get_last_imaging(self, patient: Patient, imaging_type: str) -> Optional[date]:
        """Get the most recent imaging report date."""
        try:
            reports = ImagingReport.objects.filter(patient=patient).order_by('-result_date')
            for report in reports:
                if report.name and imaging_type.lower() in report.name.lower():
                    if report.result_date:
                        return report.result_date.date() if hasattr(report.result_date, 'date') else report.result_date
            return None
        except Exception as e:
            log.error(f"Error getting imaging reports: {str(e)}")
            return None

    def _within_days(self, check_date: date, days: int) -> bool:
        """Check if a date is within the specified number of days from today."""
        if not check_date:
            return False
        today = date.today()
        delta = today - check_date
        return delta.days <= days

    def _render_html(self, patient: Patient, age: Optional[int], screenings: list) -> str:
        """Render the HTML interface."""
        # Filter out not-applicable screenings
        applicable_screenings = [s for s in screenings if s["applicable"]]

        # Count status - manual counting since sum() is not allowed in sandbox
        up_to_date = 0
        overdue = 0
        for s in applicable_screenings:
            if s["status"] == "up-to-date":
                up_to_date += 1
            elif s["status"] == "overdue":
                overdue += 1

        # Generate table rows
        rows = ""
        for screening in applicable_screenings:
            status_icon = {
                "up-to-date": "✓",
                "overdue": "⚠️",
                "not-applicable": "—"
            }.get(screening["status"], "?")

            rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{screening["name"]}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{status_icon}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{screening["last_date"]}</td>
            </tr>
            """

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Preventive Care Tracker</h2>
            <p><strong>Patient:</strong> {patient.first_name} {patient.last_name} | <strong>Age:</strong> {age if age else "Unknown"}</p>

            <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px;">
                <h3>Summary</h3>
                <p>✓ Up-to-date: {up_to_date} | ⚠️ Overdue: {overdue}</p>
            </div>

            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background-color: #f0f0f0;">
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Screening</th>
                        <th style="padding: 12px; text-align: center; border-bottom: 2px solid #ddd;">Status</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Last Date</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <p style="margin-top: 20px; font-size: 12px; color: #666;">
                <em>Note: This is a simplified version - full risk assessment and smoking history checks coming soon.</em>
            </p>
        </div>
        """
        return html

    def _render_error(self, message: str) -> str:
        """Render an error message."""
        return f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #d32f2f;">Error</h2>
            <p>{message}</p>
        </div>
        """
