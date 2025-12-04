"""Lung cancer screening logic."""

from datetime import date
from typing import Optional

from .base import BaseScreening, get_most_recent_date, add_years


class LungScreening(BaseScreening):
    """Lung cancer screening for adults 50-80 with smoking history."""

    # LDCT CPT codes
    LDCT_CPT_CODES = {
        "71271",  # Low-dose CT chest
        "G0296",  # Lung cancer screening with LDCT (Medicare)
    }

    def get_screening_name(self) -> str:
        return "Lung Cancer Screening"

    def get_uspstf_grade(self) -> str:
        return "B"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to adults 50-80 with 20+ pack-year smoking history."""
        age = patient_data.get("age", 0)
        if not (50 <= age <= 80):
            return False

        # Check smoking history
        pack_years = patient_data.get("pack_years", 0)
        return pack_years >= 20

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent LDCT date."""
        dates = []

        # Check procedures for LDCT
        procedures = data.get("procedures", [])
        for proc in procedures:
            if proc.get("code") in self.LDCT_CPT_CODES:
                dates.append(proc.get("date"))

        # Check imaging reports for LDCT
        imaging_reports = data.get("imaging_reports", [])
        for report in imaging_reports:
            report_type = report.get("type", "").lower()
            description = report.get("description", "").lower()
            if ("ldct" in report_type or "low dose ct" in report_type or
                "ldct" in description or "low dose ct" in description):
                dates.append(report.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "lung" in manual_entries:
            dates.append(manual_entries["lung"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """LDCT recommended annually for eligible patients."""
        if last_date is None:
            return None
        return add_years(last_date, 1)
