"""Statin for CVD prevention screening logic."""

from datetime import date
from typing import Optional

from .screening_base import BaseScreening, get_most_recent_date, add_years


class StatinScreening(BaseScreening):
    """Statin therapy for CVD prevention in adults 40-75 with risk factors."""

    # Diabetes ICD-10 codes
    DIABETES_ICD10_CODES = {
        "E11",  # Type 2 diabetes (prefix match)
    }

    # Hypertension ICD-10 codes
    HYPERTENSION_ICD10_CODES = {
        "I10",  # Essential hypertension
    }

    # Dyslipidemia ICD-10 codes
    DYSLIPIDEMIA_ICD10_CODES = {
        "E78",  # Disorders of lipoprotein metabolism (prefix match)
    }

    # Lipid panel LOINC codes
    LIPID_LOINC_CODES = {
        "13457-7",  # LDL cholesterol
        "2093-3",   # Total cholesterol
        "80061",    # Lipid panel
    }

    # Common statin medication names (partial matches)
    STATIN_MEDICATIONS = {
        "atorvastatin",
        "simvastatin",
        "rosuvastatin",
        "pravastatin",
        "lovastatin",
        "fluvastatin",
        "pitavastatin",
    }

    def get_screening_name(self) -> str:
        return "Statin for CVD Prevention"

    def get_uspstf_grade(self) -> str:
        return "B"

    def is_applicable(self, patient_data: dict) -> bool:
        """Applicable to adults 40-75 with CVD risk factors."""
        age = patient_data.get("age", 0)
        if not (40 <= age <= 75):
            return False

        # Check for CVD risk factors
        conditions = patient_data.get("conditions", [])
        smoking = patient_data.get("is_smoker", False)

        has_risk_factors = False

        # Check for diabetes, hypertension, or dyslipidemia
        for condition in conditions:
            # Handle both string codes and dict objects with 'code' key
            if isinstance(condition, str):
                code = condition
            else:
                code = condition.get("code", "")

            if code.startswith("E11") or code == "I10" or code.startswith("E78"):
                has_risk_factors = True
                break

        # Current smoking is also a risk factor
        if smoking:
            has_risk_factors = True

        return has_risk_factors

    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get most recent lipid panel date or statin prescription date."""
        dates = []

        # Check observations for lipid panel
        observations = data.get("observations", [])
        for obs in observations:
            if obs.get("code") in self.LIPID_LOINC_CODES:
                dates.append(obs.get("date"))

        # Check medications for active statin prescriptions
        medications = data.get("medications", [])
        for med in medications:
            med_name = med.get("name", "").lower()
            if any(statin in med_name for statin in self.STATIN_MEDICATIONS):
                # If patient has active statin, they're up to date
                if med.get("status") == "active":
                    dates.append(date.today())
                else:
                    dates.append(med.get("date"))

        # Check manual entries
        manual_entries = data.get("manual_entries", {})
        if "statin" in manual_entries:
            dates.append(manual_entries["statin"])

        return get_most_recent_date(dates)

    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Lipid panel recommended every 5 years, or ongoing if on statin."""
        if last_date is None:
            return None
        return add_years(last_date, 5)
