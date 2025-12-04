"""Unhealthy alcohol use screening logic."""

from datetime import date
from typing import Optional

from .base import BaseScreening, get_most_recent_date, add_years


class AlcoholScreening(BaseScreening):
    """Alcohol use screening for adults 18+."""

    # AUDIT screening LOINC codes
    ALCOHOL_LOINC_CODES = {
        "72109-2",  # AUDIT-C (Alcohol Use Disorders Identification Test - Consumption)
        "75626-2",  # AUDIT total score
    }

    def get_screening_name(self) -> str:
        return "Alcohol Use Screening"

    def get_uspstf_grade(self) -> str:
        return "B"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to all adults 18+."""
        age = patient_data.get("age", 0)
        return age >= 18

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent AUDIT-C screening date."""
        dates = []

        # Check observations for AUDIT screening
        observations = data.get("observations", [])
        for obs in observations:
            if obs.get("code") in self.ALCOHOL_LOINC_CODES:
                dates.append(obs.get("date"))

        # Check questionnaires for alcohol screening
        questionnaires = data.get("questionnaires", [])
        for q in questionnaires:
            q_name = q.get("name", "").lower()
            if "audit" in q_name or "alcohol" in q_name:
                dates.append(q.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "alcohol" in manual_entries:
            dates.append(manual_entries["alcohol"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Alcohol screening recommended annually."""
        if last_date is None:
            return None
        return add_years(last_date, 1)
