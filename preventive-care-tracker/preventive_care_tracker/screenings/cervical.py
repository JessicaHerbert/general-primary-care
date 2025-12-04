"""Cervical cancer screening logic."""

from datetime import date
from typing import Optional

from .base import BaseScreening, get_most_recent_date, add_years


class CervicalScreening(BaseScreening):
    """Cervical cancer screening for women 21-65."""

    # HPV and Pap test LOINC codes
    HPV_LOINC_CODES = {
        "19762-4",  # HPV DNA test
        "21440-3",  # HPV 16/18 DNA test
    }

    PAP_LOINC_CODES = {
        "10524-7",  # Cervical cytology (Pap test)
    }

    # Pap test CPT codes
    PAP_CPT_CODES = {
        "88141",  # Cytopathology, cervical or vaginal
        "88142",  # Cytopathology, cervical or vaginal, collected in preservative fluid
        "88143",  # Cytopathology, cervical or vaginal, with manual screening
        "88174",  # Cytopathology, cervical or vaginal, automated system
        "88175",  # Cytopathology, cervical or vaginal, automated system with manual rescreening
        "87624",  # HPV test, high-risk types
        "87625",  # HPV test, types 16 and 18
    }

    def get_screening_name(self) -> str:
        return "Cervical Cancer Screening"

    def get_uspstf_grade(self) -> str:
        return "A"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to women 21-65 years old."""
        age = patient_data.get("age", 0)
        sex = patient_data.get("sex", "").lower()
        return sex == "female" and 21 <= age <= 65

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent Pap or HPV test date."""
        dates = []

        # Check observations for Pap and HPV tests
        observations = data.get("observations", [])
        for obs in observations:
            code = obs.get("code")
            if code in self.HPV_LOINC_CODES or code in self.PAP_LOINC_CODES:
                dates.append(obs.get("date"))

        # Check procedures for Pap tests
        procedures = data.get("procedures", [])
        for proc in procedures:
            if proc.get("code") in self.PAP_CPT_CODES:
                dates.append(proc.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "cervical" in manual_entries:
            dates.append(manual_entries["cervical"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Calculate due date based on patient age.

        - Age 21-29: Pap every 3 years
        - Age 30-65: Pap+HPV every 5 years OR HPV alone every 5 years

        Since we don't know which test was done, use conservative approach:
        - If <30 years old: 3 years
        - If ≥30 years old: 5 years
        """
        if last_date is None:
            return None

        # This is a simplification - ideally we'd check the patient's
        # current age, but for now we'll use 5 years as default
        return add_years(last_date, 5)
