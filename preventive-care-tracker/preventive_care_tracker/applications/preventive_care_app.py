"""Preventive Care Tracker Application."""

from datetime import datetime
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.medication import Medication
from logger import log

from preventive_care_tracker.screenings import (
    ColorectalScreening,
    BreastScreening,
    HypertensionScreening,
    DepressionScreening,
    DiabetesScreening,
    LungScreening,
    CervicalScreening,
    StatinScreening,
    AlcoholScreening,
    ScreeningStatus,
)


class PreventiveCareTrackerApp(Application):
    """Preventive Care Tracker application for patient-scoped screening gap identification."""

    def on_open(self) -> Effect | list[Effect]:
        """Handle application open - render the preventive care tracking interface.

        Returns:
            LaunchModalEffect with HTML content showing preventive care screening status
        """
        patient_id = self.context.get("patient", {}).get("id")

        if not patient_id:
            error_html = self._render_error("No patient context available.")
            return LaunchModalEffect(
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
                title="Preventive Care Tracker",
                content=error_html
            ).apply()

        # Gather patient data
        patient_data = self._gather_patient_data(patient_id)
        screening_data = self._gather_screening_data(patient_id)

        # Evaluate all screenings
        results = self._evaluate_screenings(patient_data, screening_data)

        # Render HTML
        html_content = self._render_html(patient_data, results)

        return LaunchModalEffect(
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE,
            title="Preventive Care Tracker",
            content=html_content
        ).apply()

    def _gather_patient_data(self, patient_id: str) -> dict:
        """Gather patient demographics and relevant history.

        Args:
            patient_id: Canvas patient identifier

        Returns:
            Dictionary with patient data needed for screening evaluation
        """
        try:
            patient = Patient.objects.get(id=patient_id)

            # Calculate age
            if patient.birth_date:
                today = datetime.now().date()
                age = today.year - patient.birth_date.year
                if today.month < patient.birth_date.month or (
                    today.month == patient.birth_date.month and today.day < patient.birth_date.day
                ):
                    age -= 1
            else:
                age = 0

            # Get BMI from most recent observation
            bmi = None
            bmi_obs = Observation.objects.filter(
                patient=patient_id,
                code="39156-5"  # BMI LOINC code
            ).order_by("-effective_datetime").first()
            if bmi_obs and bmi_obs.value_quantity:
                bmi = float(bmi_obs.value_quantity.get("value", 0))

            # Get conditions
            conditions = list(Condition.objects.filter(
                patient=patient_id,
                clinicalStatus="active"
            ).values_list("code__code", flat=True))

            # Get smoking history (simplified - would need more logic in production)
            pack_years = 0  # Would calculate from social history

            # Determine if current smoker
            is_smoker = False  # Would check social history

            return {
                "age": age,
                "sex": patient.sex.lower() if patient.sex else "unknown",
                "bmi": bmi,
                "conditions": conditions,
                "pack_years": pack_years,
                "is_smoker": is_smoker,
            }
        except Patient.DoesNotExist:
            log.error(f"Patient {patient_id} not found")
            return {"age": 0, "sex": "unknown", "conditions": [], "bmi": None, "pack_years": 0, "is_smoker": False}

    def _gather_screening_data(self, patient_id: str) -> dict:
        """Gather screening records from various sources.

        Args:
            patient_id: Canvas patient identifier

        Returns:
            Dictionary with screening data from observations, procedures, imaging, etc.
        """
        data = {
            "observations": [],
            "procedures": [],
            "imaging_reports": [],
            "vitals": [],
            "conditions": [],
            "medications": [],
            "questionnaires": [],
            "manual_entries": {},
        }

        # Get observations (labs, vitals)
        observations = Observation.objects.filter(patient=patient_id)
        for obs in observations:
            if obs.code and obs.effective_datetime:
                data["observations"].append({
                    "code": obs.code,
                    "date": obs.effective_datetime.date() if hasattr(obs.effective_datetime, 'date') else obs.effective_datetime,
                    "value": obs.value_quantity or obs.value_string,
                })

        # Get procedures
        # NOTE: Procedure model not available in current Canvas SDK
        # Procedure-based screenings will rely on imaging reports and observations
        # procedures = Procedure.objects.filter(patient=patient_id)
        # for proc in procedures:
        #     if proc.code and proc.performed_datetime:
        #         data["procedures"].append({
        #             "code": proc.code.code if hasattr(proc.code, 'code') else str(proc.code),
        #             "date": proc.performed_datetime.date() if hasattr(proc.performed_datetime, 'date') else proc.performed_datetime,
        #         })

        # Get imaging reports
        imaging_reports = ImagingReport.objects.filter(patient=patient_id)
        for report in imaging_reports:
            if report.report_date:
                data["imaging_reports"].append({
                    "type": report.name or "",
                    "description": report.description or "",
                    "date": report.report_date.date() if hasattr(report.report_date, 'date') else report.report_date,
                })

        # Get conditions
        conditions = Condition.objects.filter(patient=patient_id, clinicalStatus="active")
        for condition in conditions:
            data["conditions"].append({
                "code": condition.code.code if hasattr(condition.code, 'code') else str(condition.code),
                "onset_date": condition.onset_datetime.date() if condition.onset_datetime and hasattr(condition.onset_datetime, 'date') else None,
            })

        # Get medications
        medications = Medication.objects.filter(patient=patient_id)
        for med in medications:
            data["medications"].append({
                "name": med.fdb_medication_name or "",
                "code": med.fdb_code or "",
                "date": med.created.date() if med.created and hasattr(med.created, 'date') else None,
            })

        # Manual entries would come from questionnaire responses
        # For now, this is a placeholder
        data["manual_entries"] = {}

        return data

    def _evaluate_screenings(self, patient_data: dict, screening_data: dict) -> list:
        """Evaluate all preventive care screenings.

        Args:
            patient_data: Patient demographics and history
            screening_data: Screening records

        Returns:
            List of ScreeningResult objects
        """
        # Initialize all screening types
        screenings = [
            ColorectalScreening(patient_data.get("age", 0)),
            BreastScreening(patient_data.get("age", 0)),
            HypertensionScreening(patient_data.get("age", 0)),
            DepressionScreening(patient_data.get("age", 0)),
            DiabetesScreening(patient_data.get("age", 0)),
            LungScreening(patient_data.get("age", 0)),
            CervicalScreening(patient_data.get("age", 0)),
            StatinScreening(patient_data.get("age", 0)),
            AlcoholScreening(patient_data.get("age", 0)),
        ]

        results = []
        for screening in screenings:
            result = screening.evaluate(patient_data, screening_data)
            results.append(result)

        # Sort by status (overdue first, then N/A, then up-to-date)
        status_priority = {
            ScreeningStatus.OVERDUE: 0,
            ScreeningStatus.NOT_APPLICABLE: 1,
            ScreeningStatus.UP_TO_DATE: 2,
        }
        results.sort(key=lambda r: (status_priority.get(r.status, 3), r.name))

        return results

    def _render_html(self, patient_data: dict, results: list) -> str:
        """Render HTML for the preventive care tracker interface.

        Args:
            patient_data: Patient demographics
            results: List of ScreeningResult objects

        Returns:
            HTML string
        """
        # Count statistics
        up_to_date_count = sum(1 for r in results if r.status == ScreeningStatus.UP_TO_DATE and r.applicable)
        overdue_count = sum(1 for r in results if r.status == ScreeningStatus.OVERDUE and r.applicable)
        not_applicable_count = sum(1 for r in results if not r.applicable)

        # Build table rows
        rows_html = ""
        for result in results:
            if result.applicable:
                status_icon, status_color = self._get_status_display(result.status)
                last_date_str = result.last_date.strftime("%m/%d/%Y") if result.last_date else "None"
                due_date_str = result.due_date.strftime("%m/%d/%Y") if result.due_date else "—"

                rows_html += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{result.name}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">
                        <span style="color: {status_color}; font-size: 18px;">{status_icon}</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">{last_date_str}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">{due_date_str}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-weight: bold;">{result.grade}</td>
                </tr>
                """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 24px;
                }}
                .header {{
                    margin-bottom: 24px;
                    padding-bottom: 16px;
                    border-bottom: 2px solid #e0e0e0;
                }}
                .header h1 {{
                    margin: 0 0 8px 0;
                    font-size: 24px;
                    color: #333;
                }}
                .header .subtitle {{
                    color: #666;
                    font-size: 14px;
                }}
                .summary {{
                    display: flex;
                    gap: 16px;
                    margin-bottom: 24px;
                    flex-wrap: wrap;
                }}
                .summary-card {{
                    flex: 1;
                    min-width: 150px;
                    padding: 16px;
                    border-radius: 6px;
                    text-align: center;
                }}
                .summary-card.up-to-date {{
                    background-color: #e8f5e9;
                    border-left: 4px solid #4caf50;
                }}
                .summary-card.overdue {{
                    background-color: #fff3e0;
                    border-left: 4px solid #ff9800;
                }}
                .summary-card.not-applicable {{
                    background-color: #f5f5f5;
                    border-left: 4px solid #9e9e9e;
                }}
                .summary-card .number {{
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 4px;
                }}
                .summary-card .label {{
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 24px;
                }}
                th {{
                    background-color: #f5f5f5;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 14px;
                    color: #333;
                    border-bottom: 2px solid #e0e0e0;
                }}
                th.center {{
                    text-align: center;
                }}
                .footer {{
                    padding-top: 16px;
                    border-top: 1px solid #e0e0e0;
                    color: #666;
                    font-size: 12px;
                }}
                .legend {{
                    margin-top: 16px;
                    padding: 12px;
                    background-color: #f9f9f9;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                .legend-item {{
                    display: inline-block;
                    margin-right: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Preventive Care Tracker</h1>
                    <div class="subtitle">
                        Age: {patient_data.get('age', 'Unknown')} |
                        Sex: {patient_data.get('sex', 'Unknown').capitalize()} |
                        Last Updated: {datetime.now().strftime("%m/%d/%Y %I:%M %p")}
                    </div>
                </div>

                <div class="summary">
                    <div class="summary-card up-to-date">
                        <div class="number">{up_to_date_count}</div>
                        <div class="label">Up-to-Date</div>
                    </div>
                    <div class="summary-card overdue">
                        <div class="number">{overdue_count}</div>
                        <div class="label">Overdue</div>
                    </div>
                    <div class="summary-card not-applicable">
                        <div class="number">{not_applicable_count}</div>
                        <div class="label">Not Applicable</div>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Screening</th>
                            <th class="center">Status</th>
                            <th class="center">Last Date</th>
                            <th class="center">Due Date</th>
                            <th class="center">USPSTF Grade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>

                <div class="legend">
                    <div class="legend-item"><strong>Status:</strong></div>
                    <div class="legend-item" style="color: #4caf50;">✓ Up-to-Date</div>
                    <div class="legend-item" style="color: #ff9800;">⚠ Overdue</div>
                    <div class="legend-item" style="color: #9e9e9e;">— Not Applicable</div>
                </div>

                <div class="footer">
                    Based on USPSTF guidelines. For manual date entry or to override screening dates,
                    use the "Preventive Care Screening Dates" questionnaire.
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _get_status_display(self, status: ScreeningStatus) -> tuple[str, str]:
        """Get display icon and color for a screening status.

        Args:
            status: ScreeningStatus enum value

        Returns:
            Tuple of (icon, color)
        """
        if status == ScreeningStatus.UP_TO_DATE:
            return ("✓", "#4caf50")
        elif status == ScreeningStatus.OVERDUE:
            return ("⚠", "#ff9800")
        else:
            return ("—", "#9e9e9e")

    def _render_error(self, message: str) -> str:
        """Render an error message.

        Args:
            message: Error message to display

        Returns:
            HTML string
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 40px;
                    background-color: #f5f5f5;
                }}
                .error {{
                    background-color: #fff;
                    padding: 24px;
                    border-radius: 8px;
                    border-left: 4px solid #f44336;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .error h2 {{
                    margin: 0 0 8px 0;
                    color: #f44336;
                }}
                .error p {{
                    margin: 0;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>Error</h2>
                <p>{message}</p>
            </div>
        </body>
        </html>
        """
