"""Depression screening logic."""

from datetime import date
from typing import Optional

from .base import BaseScreening, get_most_recent_date, add_years


class DepressionScreening(BaseScreening):
    """Depression screening for all adults."""

    # Depression screening LOINC codes
    DEPRESSION_LOINC_CODES = {
        "55758-7",  # PHQ-2 (Patient Health Questionnaire-2)
        "44249-1",  # PHQ-9 (Patient Health Questionnaire-9)
        "73831-0",  # PHQ-9 panel
    }

    def get_screening_name(self) -> str:
        return "Depression Screening"

    def get_uspstf_grade(self) -> str:
        return "B"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to all adults (including pregnant/postpartum)."""
        age = patient_data.get("age", 0)
        return age >= 18

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent PHQ-2 or PHQ-9 screening date."""
        dates = []

        # Check observations for depression screening
        observations = data.get("observations", [])
        for obs in observations:
            if obs.get("code") in self.DEPRESSION_LOINC_CODES:
                dates.append(obs.get("date"))

        # Check questionnaires
        questionnaires = data.get("questionnaires", [])
        for q in questionnaires:
            q_name = q.get("name", "").lower()
            if "phq" in q_name or "depression" in q_name:
                dates.append(q.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "depression" in manual_entries:
            dates.append(manual_entries["depression"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Depression screening recommended annually."""
        if last_date is None:
            return None
        return add_years(last_date, 1)
