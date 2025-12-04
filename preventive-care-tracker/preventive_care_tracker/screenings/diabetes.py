"""Prediabetes and Type 2 Diabetes screening logic."""

from datetime import date
from typing import Optional

from .screening_base import BaseScreening, get_most_recent_date, add_years


class DiabetesScreening(BaseScreening):
    """Diabetes screening for adults 35-70 with BMI ≥25."""

    # Diabetes screening LOINC codes
    DIABETES_LOINC_CODES = {
        "4548-4",   # HbA1c
        "1558-6",   # Fasting glucose
        "2345-7",   # Glucose (random)
    }

    # BMI LOINC code
    BMI_LOINC_CODE = "39156-5"

    def get_screening_name(self) -> str:
        return "Diabetes Screening"

    def get_uspstf_grade(self) -> str:
        return "B"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to adults 35-70 with BMI ≥25."""
        age = patient_data.get("age", 0)
        if not (35 <= age <= 70):
            return False

        # Check BMI
        bmi = patient_data.get("bmi")
        if bmi is None:
            # If BMI not provided, assume applicable (will show in UI)
            return True

        return bmi >= 25

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent HbA1c or glucose test date."""
        dates = []

        # Check observations for diabetes screening tests
        observations = data.get("observations", [])
        for obs in observations:
            if obs.get("code") in self.DIABETES_LOINC_CODES:
                dates.append(obs.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "diabetes" in manual_entries:
            dates.append(manual_entries["diabetes"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Diabetes screening recommended every 3 years."""
        if last_date is None:
            return None
        return add_years(last_date, 3)
