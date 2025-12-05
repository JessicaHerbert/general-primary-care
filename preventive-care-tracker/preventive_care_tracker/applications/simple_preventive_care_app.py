"""Preventive Care Tracker Application - Questionnaire-based screening tracker."""

from datetime import datetime, date
from typing import Optional
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.command import Command
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
        """Get most recent screening dates from all questionnaire submissions."""
        # Get the most recent date for each screening across ALL questionnaires
        screening_dates = self._get_latest_screening_dates(patient)

        # Mapping of question codes to display names
        screening_config = [
            ("HYPERTENSION_DATE", "Hypertension Screening"),
            ("DEPRESSION_DATE", "Depression Screening"),
            ("ALCOHOL_DATE", "Alcohol Use Screening"),
            ("COLORECTAL_DATE", "Colorectal Cancer Screening"),
            ("BREAST_DATE", "Breast Cancer Screening"),
            ("CERVICAL_DATE", "Cervical Cancer Screening"),
            ("DIABETES_DATE", "Diabetes Screening"),
            ("LUNG_DATE", "Lung Cancer Screening"),
            ("STATIN_DATE", "Statin/CVD Prevention"),
        ]

        screenings = []
        for question_code, display_name in screening_config:
            date_value = screening_dates.get(question_code) if screening_dates else None
            screenings.append({
                "name": display_name,
                "last_date": date_value if date_value else "Never"
            })

        return screenings

    def _get_latest_screening_dates(self, patient: Patient) -> Optional[dict]:
        """Get the most recent date for each screening type across all questionnaire submissions.

        Returns:
            Dictionary mapping question codes to the most recent date string for each screening
        """
        try:
            # Query for all commands for this patient, then filter by questionnaire name
            commands = Command.objects.filter(
                patient=patient
            ).order_by('-created')

            # Filter to only preventive care questionnaires
            preventive_care_commands = []
            for cmd in commands:
                if cmd.data and 'questionnaire' in cmd.data:
                    quest_name = cmd.data.get('questionnaire', {}).get('text', '')
                    if quest_name == 'Preventive Care Screening Dates':
                        preventive_care_commands.append(cmd)

            if not preventive_care_commands:
                return None

            # Dictionary to track the most recent date for each screening type
            # Key: question_code, Value: (date object, formatted_date string)
            most_recent_dates = {}

            # Iterate through ALL questionnaires to find the most recent date for each screening
            for cmd in preventive_care_commands:
                if not cmd.data:
                    continue

                # Get questionnaire metadata to map question IDs to codes
                if 'questionnaire' in cmd.data and 'extra' in cmd.data['questionnaire']:
                    questions = cmd.data['questionnaire']['extra'].get('questions', [])

                    for question in questions:
                        question_pk = question.get('pk')
                        question_code = question.get('coding', {}).get('code')
                        question_key = f"question-{question_pk}"

                        if question_key in cmd.data:
                            date_str = cmd.data[question_key]
                            if date_str:  # Only process non-empty dates
                                # Parse the date
                                parsed_date = self._parse_date_string(date_str)
                                if parsed_date:
                                    formatted_date = parsed_date.strftime("%m/%d/%Y")

                                    # Check if this is the most recent date for this screening type
                                    if question_code not in most_recent_dates:
                                        most_recent_dates[question_code] = (parsed_date, formatted_date)
                                    else:
                                        existing_date, existing_formatted = most_recent_dates[question_code]
                                        if parsed_date > existing_date:
                                            most_recent_dates[question_code] = (parsed_date, formatted_date)

            # Convert to result dictionary with just the formatted dates
            result = {code: formatted_date for code, (_, formatted_date) in most_recent_dates.items()}
            return result if result else None

        except Exception as e:
            log.error(f"Error getting latest screening dates: {str(e)}")
            log.error(f"Exception type: {type(e).__name__}")
            return None

    def _parse_date_string(self, date_str: str) -> Optional[date]:
        """Parse a date string in various formats."""
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try common formats
        formats = [
            "%m/%d/%Y",     # 12/04/2025
            "%m/%d/%y",     # 12/04/25
            "%Y-%m-%d",     # 2025-12-04
            "%m-%d-%Y",     # 12-04-2025
            "%m/%Y",        # 12/2025 (month/year only)
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.date()
            except ValueError:
                continue

        log.warning(f"Could not parse date string: {date_str}")
        return None

    def _render_html(self, patient: Patient, age: Optional[int], screenings: list) -> str:
        """Render the HTML interface with Canvas branding."""
        # Generate table rows with alternating background
        rows = ""
        for idx, screening in enumerate(screenings):
            bg_color = "#f8f9fa" if idx % 2 == 0 else "#ffffff"
            date_display = screening["last_date"]
            date_color = "#6c757d" if date_display == "Never" else "#212529"

            rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 14px 16px; color: #212529; font-size: 14px; font-weight: 500;">{screening["name"]}</td>
                <td style="padding: 14px 16px; color: {date_color}; font-size: 14px;">{date_display}</td>
            </tr>
            """

        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    padding: 24px; background-color: #f8f9fa; min-height: 100vh;">

            <!-- Header Section -->
            <div style="background: linear-gradient(135deg, #1b9aaa 0%, #16808e 100%);
                        padding: 24px 28px;
                        border-radius: 8px;
                        margin-bottom: 24px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 8px 0;
                           color: #ffffff;
                           font-size: 24px;
                           font-weight: 600;
                           letter-spacing: -0.5px;">
                    Preventive Care Tracker
                </h2>
                <p style="margin: 0;
                          color: rgba(255,255,255,0.9);
                          font-size: 14px;
                          font-weight: 400;">
                    <strong style="font-weight: 600;">{patient.first_name} {patient.last_name}</strong>
                    <span style="margin: 0 8px; opacity: 0.7;">•</span>
                    <span>Age: {age if age else "Unknown"}</span>
                </p>
            </div>

            <!-- Screenings Table -->
            <div style="background-color: #ffffff;
                        border-radius: 8px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                        overflow: hidden;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #e9ecef; border-bottom: 2px solid #dee2e6;">
                            <th style="padding: 14px 16px;
                                       text-align: left;
                                       color: #495057;
                                       font-size: 13px;
                                       font-weight: 600;
                                       text-transform: uppercase;
                                       letter-spacing: 0.5px;">
                                Screening Type
                            </th>
                            <th style="padding: 14px 16px;
                                       text-align: left;
                                       color: #495057;
                                       font-size: 13px;
                                       font-weight: 600;
                                       text-transform: uppercase;
                                       letter-spacing: 0.5px;">
                                Last Completed
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>

            <!-- Footer Note -->
            <div style="margin-top: 20px; padding: 12px; color: #6c757d; font-size: 13px; text-align: center;">
                Showing most recent date for each screening type
            </div>
        </div>
        """
        return html

    def _render_error(self, message: str) -> str:
        """Render an error message with Canvas branding."""
        return f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    padding: 24px; background-color: #f8f9fa; min-height: 100vh;">
            <div style="background-color: #ffffff;
                        border-left: 4px solid #dc3545;
                        border-radius: 8px;
                        padding: 24px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                <h2 style="margin: 0 0 12px 0;
                           color: #dc3545;
                           font-size: 20px;
                           font-weight: 600;">
                    Error
                </h2>
                <p style="margin: 0;
                          color: #495057;
                          font-size: 14px;
                          line-height: 1.5;">
                    {message}
                </p>
            </div>
        </div>
        """
