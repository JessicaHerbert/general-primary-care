"""Hypertension screening logic."""

from datetime import date
from typing import Optional

from .screening_base import BaseScreening, get_most_recent_date, add_years


class HypertensionScreening(BaseScreening):
    """Hypertension screening for adults 18+."""

    # Blood pressure LOINC codes
    BP_LOINC_CODES = {
        "8480-6",   # Systolic blood pressure
        "8462-4",   # Diastolic blood pressure
        "85354-9",  # Blood pressure panel
    }

    def get_screening_name(self) -> str:
        return "Hypertension Screening"

    def get_uspstf_grade(self) -> str:
        return "A"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to all adults 18+."""
        age = patient_data.get("age", 0)
        return age >= 18

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent blood pressure reading date."""
        dates = []

        # Check observations for blood pressure readings
        observations = data.get("observations", [])
        for obs in observations:
            if obs.get("code") in self.BP_LOINC_CODES:
                dates.append(obs.get("date"))

        # Check vitals for blood pressure
        vitals = data.get("vitals", [])
        for vital in vitals:
            if "blood_pressure" in vital or "bp" in vital:
                dates.append(vital.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "hypertension" in manual_entries:
            dates.append(manual_entries["hypertension"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Blood pressure screening recommended annually."""
        if last_date is None:
            return None
        return add_years(last_date, 1)
