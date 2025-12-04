"""Colorectal cancer screening logic."""

from datetime import date
from typing import Optional

from .screening_base import BaseScreening, get_most_recent_date, add_years


class ColorectalScreening(BaseScreening):
    """Colorectal cancer screening for adults 45-75."""

    # Colonoscopy CPT codes
    COLONOSCOPY_CPT_CODES = {
        "45378",  # Colonoscopy, flexible
        "45380",  # Colonoscopy with biopsy
        "45381",  # Colonoscopy with submucosal injection
        "45382",  # Colonoscopy with control of bleeding
        "45384",  # Colonoscopy with removal of tumor(s)
        "45385",  # Colonoscopy with removal of polyp(s)
        "G0121",  # Colorectal cancer screening; colonoscopy on individual not meeting criteria
        "G0105",  # Colorectal cancer screening; colonoscopy on individual at high risk
    }

    # FIT test LOINC codes
    FIT_LOINC_CODES = {
        "29771-3",  # Fecal occult blood [Presence] in Stool
        "56490-6",  # Fecal occult blood panel [Presence] in Stool
        "57905-2",  # Fecal immunochemical test (FIT)
    }

    def get_screening_name(self) -> str:
        return "Colorectal Cancer Screening"

    def get_uspstf_grade(self) -> str:
        return "A"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to adults 45-75 years old."""
        age = patient_data.get("age", 0)
        return 45 <= age <= 75

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent colonoscopy or FIT test date."""
        dates = []

        # Check procedures for colonoscopy
        procedures = data.get("procedures", [])
        for proc in procedures:
            if proc.get("code") in self.COLONOSCOPY_CPT_CODES:
                dates.append(proc.get("date"))

        # Check lab results for FIT
        observations = data.get("observations", [])
        for obs in observations:
            if obs.get("code") in self.FIT_LOINC_CODES:
                dates.append(obs.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "colorectal" in manual_entries:
            dates.append(manual_entries["colorectal"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Calculate next due date.

        - Colonoscopy: every 10 years
        - FIT: every 1 year

        Since we don't know which test was done, we use the conservative
        approach of assuming FIT (1 year) unless the date is >2 years ago,
        then assume colonoscopy (10 years).
        """
        if last_date is None:
            return None

        # Simple heuristic: if last screening was >2 years ago,
        # assume it was a colonoscopy (due in 10 years)
        # Otherwise assume FIT (due in 1 year)
        years_since = (date.today() - last_date).days / 365.25

        if years_since > 2:
            # Likely was a colonoscopy
            return add_years(last_date, 10)
        else:
            # Likely was a FIT test
            return add_years(last_date, 1)
