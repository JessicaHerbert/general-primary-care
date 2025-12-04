"""Protocol handler for preventive care screening questionnaire submissions."""

from datetime import datetime
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data.command import Command
from logger import log


class PreventiveCareQuestionnaireHandler(BaseProtocol):
    """Handle submissions of the Preventive Care Screening Dates questionnaire.

    This protocol processes manual date entries for preventive care screenings
    and stores them for use by the application handler.
    """

    RESPONDS_TO = EventType.Name(EventType.QUESTIONNAIRE_COMMAND__POST_COMMIT)

    # Mapping of screening types to questionnaire question identifiers
    SCREENING_QUESTION_MAP = {
        "colorectal": "colorectal_screening_date",
        "breast": "breast_screening_date",
        "cervical": "cervical_screening_date",
        "hypertension": "hypertension_screening_date",
        "depression": "depression_screening_date",
        "diabetes": "diabetes_screening_date",
        "lung": "lung_screening_date",
        "statin": "statin_screening_date",
        "alcohol": "alcohol_screening_date",
    }

    def compute(self) -> list[Effect]:
        """Process questionnaire submission and store manual screening dates.

        Returns:
            List of effects (empty for now - could add confirmation messages)
        """
        # Get the command that was committed
        command_id = self.event.target.id

        try:
            command = Command.objects.get(id=command_id)
        except Command.DoesNotExist:
            log.error(f"Command {command_id} not found")
            return []

        # Check if this is the preventive care questionnaire by checking command.data
        if not command.data:
            log.info(f"Command {command_id} has no data")
            return []

        log.info(f"Preventive Care questionnaire handler processing command {command_id}")
        log.info(f"Command data: {command.data}")

        # Parse the questionnaire responses from command.data
        # command.data structure is like: {"HYPERTENSION_DATE": "12/04/2025", ...}
        screening_dates = {}

        # Map of our question codes to screening names
        question_code_map = {
            "HYPERTENSION_DATE": "hypertension",
            "DEPRESSION_DATE": "depression",
            "ALCOHOL_DATE": "alcohol",
            "COLORECTAL_DATE": "colorectal",
            "BREAST_DATE": "breast",
            "CERVICAL_DATE": "cervical",
            "DIABETES_DATE": "diabetes",
            "LUNG_DATE": "lung",
            "STATIN_DATE": "statin"
        }

        # Extract dates from command.data
        for question_code, screening_name in question_code_map.items():
            if question_code in command.data:
                date_str = command.data[question_code]
                if date_str:
                    parsed_date = self._parse_date_string(date_str)
                    if parsed_date:
                        screening_dates[screening_name] = parsed_date
                        log.info(f"Parsed {screening_name} screening date: {parsed_date}")

        if screening_dates:
            log.info(f"Successfully parsed {len(screening_dates)} screening dates from questionnaire")
            # TODO: Store these dates as observations or in patient metadata
            # For now, they're logged and can be used for verification
        else:
            log.info("No valid screening dates found in questionnaire responses")

        return []

    def _parse_questionnaire_responses(self, interview_data: dict) -> dict:
        """Parse questionnaire responses to extract screening dates.

        Args:
            interview: Interview object containing questionnaire responses

        Returns:
            Dictionary mapping screening types to dates
        """
        parsed_dates = {}

        # The interview.data structure varies by questionnaire
        # This is a simplified parser
        if not interview.data:
            return parsed_dates

        questions = interview.data.get("questions", [])

        for question in questions:
            question_id = question.get("id", "")
            responses = question.get("responses", [])

            # Find which screening this question corresponds to
            screening_type = None
            for screening, q_id in self.SCREENING_QUESTION_MAP.items():
                if q_id in question_id.lower():
                    screening_type = screening
                    break

            if not screening_type:
                continue

            # Extract date from response
            # Responses are typically text for date entry questions
            for response in responses:
                date_text = response.get("text", "")
                if date_text:
                    parsed_date = self._parse_date_string(date_text)
                    if parsed_date:
                        parsed_dates[screening_type] = parsed_date
                        log.info(f"Parsed {screening_type} screening date: {parsed_date}")

        return parsed_dates

    def _parse_date_string(self, date_str: str) -> datetime.date:
        """Parse a date string in various formats.

        Args:
            date_str: Date string (MM/DD/YYYY, MM/YYYY, etc.)

        Returns:
            date object or None if parsing fails
        """
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
