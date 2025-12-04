"""Breast cancer screening logic."""

from datetime import date
from typing import Optional

from .screening_base import BaseScreening, get_most_recent_date, add_years


class BreastScreening(BaseScreening):
    """Breast cancer screening for women 40-74."""

    # Mammography CPT codes
    MAMMOGRAPHY_CPT_CODES = {
        "77067",  # Screening mammography, bilateral
        "G0202",  # Screening mammography, bilateral (Medicare)
    }

    def get_screening_name(self) -> str:
        return "Breast Cancer Screening"

    def get_uspstf_grade(self) -> str:
        return "B"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to women 40-74 years old."""
        age = patient_data.get("age", 0)
        sex = patient_data.get("sex", "").lower()
        return sex == "female" and 40 <= age <= 74

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent mammography date from procedures or imaging reports."""
        dates = []

        # Check procedures
        procedures = data.get("procedures", [])
        for proc in procedures:
            if proc.get("code") in self.MAMMOGRAPHY_CPT_CODES:
                dates.append(proc.get("date"))

        # Check imaging reports
        imaging_reports = data.get("imaging_reports", [])
        for report in imaging_reports:
            report_type = report.get("type", "").lower()
            if "mammogram" in report_type or "mammography" in report_type:
                dates.append(report.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "breast" in manual_entries:
            dates.append(manual_entries["breast"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Mammography recommended every 2 years."""
        if last_date is None:
            return None
        return add_years(last_date, 2)
