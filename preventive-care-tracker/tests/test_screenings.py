"""Unit tests for preventive care screening logic."""

import pytest
from datetime import date, timedelta
from preventive_care_tracker.screenings import (
    ScreeningStatus,
    ColorectalScreening,
    BreastScreening,
    HypertensionScreening,
    DepressionScreening,
    DiabetesScreening,
    LungScreening,
    CervicalScreening,
    StatinScreening,
    AlcoholScreening,
)
from preventive_care_tracker.screenings.base import parse_date, get_most_recent_date, add_years


class TestBaseHelperFunctions:
    """Test base helper functions."""

    def test_parse_date_from_string(self):
        """Test parsing date from string formats."""
        assert parse_date("2025-12-04") == date(2025, 12, 4)
        assert parse_date("12/04/2025") == date(2025, 12, 4)
        assert parse_date("12/04/25") == date(2025, 12, 4)
        assert parse_date("invalid") is None

    def test_parse_date_from_date_object(self):
        """Test parsing date from date object."""
        test_date = date(2025, 12, 4)
        assert parse_date(test_date) == test_date

    def test_get_most_recent_date(self):
        """Test getting most recent date from list."""
        dates = [
            date(2020, 1, 1),
            date(2023, 6, 15),
            date(2022, 3, 10),
        ]
        assert get_most_recent_date(dates) == date(2023, 6, 15)

    def test_get_most_recent_date_empty_list(self):
        """Test getting most recent date from empty list."""
        assert get_most_recent_date([]) is None

    def test_add_years(self):
        """Test adding years to a date."""
        start = date(2020, 1, 1)
        assert add_years(start, 1) == date(2021, 1, 1)
        assert add_years(start, 5) == date(2025, 1, 1)


class TestColorectalScreening:
    """Test colorectal cancer screening logic."""

    def test_is_applicable_age_45_to_75(self):
        """Test applicability for ages 45-75."""
        screening = ColorectalScreening("patient_id")
        assert screening.is_applicable({"age": 45}) is True
        assert screening.is_applicable({"age": 60}) is True
        assert screening.is_applicable({"age": 75}) is True

    def test_is_not_applicable_outside_age_range(self):
        """Test not applicable outside age range."""
        screening = ColorectalScreening("patient_id")
        assert screening.is_applicable({"age": 44}) is False
        assert screening.is_applicable({"age": 76}) is False

    def test_get_last_screening_date_from_procedures(self):
        """Test getting last screening date from procedures."""
        screening = ColorectalScreening("patient_id")
        data = {
            "procedures": [
                {"code": "45378", "date": date(2020, 1, 1)},
                {"code": "45385", "date": date(2023, 6, 15)},
            ],
            "observations": [],
            "manual_entries": {},
        }
        assert screening.get_last_screening_date(data) == date(2023, 6, 15)

    def test_get_last_screening_date_from_fit_test(self):
        """Test getting last screening date from FIT test."""
        screening = ColorectalScreening("patient_id")
        data = {
            "procedures": [],
            "observations": [
                {"code": "29771-3", "date": date(2024, 11, 1)},
            ],
            "manual_entries": {},
        }
        assert screening.get_last_screening_date(data) == date(2024, 11, 1)

    def test_calculate_due_date_recent_screening(self):
        """Test due date calculation for recent screening (assumes FIT)."""
        screening = ColorectalScreening("patient_id")
        last_date = date.today() - timedelta(days=180)  # 6 months ago
        due_date = screening.calculate_due_date(last_date)
        # Should be 1 year from last date (FIT)
        expected = add_years(last_date, 1)
        assert due_date == expected

    def test_calculate_due_date_old_screening(self):
        """Test due date calculation for old screening (assumes colonoscopy)."""
        screening = ColorectalScreening("patient_id")
        last_date = date.today() - timedelta(days=1095)  # 3 years ago
        due_date = screening.calculate_due_date(last_date)
        # Should be 10 years from last date (colonoscopy)
        expected = add_years(last_date, 10)
        assert due_date == expected


class TestBreastScreening:
    """Test breast cancer screening logic."""

    def test_is_applicable_women_40_to_74(self):
        """Test applicability for women 40-74."""
        screening = BreastScreening("patient_id")
        assert screening.is_applicable({"age": 40, "sex": "female"}) is True
        assert screening.is_applicable({"age": 55, "sex": "female"}) is True
        assert screening.is_applicable({"age": 74, "sex": "female"}) is True

    def test_is_not_applicable_men(self):
        """Test not applicable for men."""
        screening = BreastScreening("patient_id")
        assert screening.is_applicable({"age": 50, "sex": "male"}) is False

    def test_is_not_applicable_outside_age_range(self):
        """Test not applicable outside age range."""
        screening = BreastScreening("patient_id")
        assert screening.is_applicable({"age": 39, "sex": "female"}) is False
        assert screening.is_applicable({"age": 75, "sex": "female"}) is False

    def test_calculate_due_date(self):
        """Test due date calculation (every 2 years)."""
        screening = BreastScreening("patient_id")
        last_date = date(2022, 3, 15)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2024, 3, 15)


class TestHypertensionScreening:
    """Test hypertension screening logic."""

    def test_is_applicable_adults_18_plus(self):
        """Test applicability for adults 18+."""
        screening = HypertensionScreening("patient_id")
        assert screening.is_applicable({"age": 18}) is True
        assert screening.is_applicable({"age": 50}) is True
        assert screening.is_applicable({"age": 90}) is True

    def test_is_not_applicable_under_18(self):
        """Test not applicable under 18."""
        screening = HypertensionScreening("patient_id")
        assert screening.is_applicable({"age": 17}) is False

    def test_calculate_due_date(self):
        """Test due date calculation (annually)."""
        screening = HypertensionScreening("patient_id")
        last_date = date(2024, 1, 1)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2025, 1, 1)


class TestDepressionScreening:
    """Test depression screening logic."""

    def test_is_applicable_all_adults(self):
        """Test applicability for all adults."""
        screening = DepressionScreening("patient_id")
        assert screening.is_applicable({"age": 18}) is True
        assert screening.is_applicable({"age": 65}) is True

    def test_calculate_due_date(self):
        """Test due date calculation (annually)."""
        screening = DepressionScreening("patient_id")
        last_date = date(2024, 6, 10)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2025, 6, 10)


class TestDiabetesScreening:
    """Test diabetes screening logic."""

    def test_is_applicable_with_bmi_25_plus(self):
        """Test applicability for age 35-70 with BMI ≥25."""
        screening = DiabetesScreening("patient_id")
        assert screening.is_applicable({"age": 35, "bmi": 25}) is True
        assert screening.is_applicable({"age": 50, "bmi": 30}) is True
        assert screening.is_applicable({"age": 70, "bmi": 26}) is True

    def test_is_not_applicable_low_bmi(self):
        """Test not applicable with low BMI."""
        screening = DiabetesScreening("patient_id")
        assert screening.is_applicable({"age": 50, "bmi": 24}) is False

    def test_is_not_applicable_outside_age_range(self):
        """Test not applicable outside age range."""
        screening = DiabetesScreening("patient_id")
        assert screening.is_applicable({"age": 34, "bmi": 30}) is False
        assert screening.is_applicable({"age": 71, "bmi": 30}) is False

    def test_is_applicable_no_bmi_provided(self):
        """Test applicability when BMI not provided (assume applicable)."""
        screening = DiabetesScreening("patient_id")
        assert screening.is_applicable({"age": 50, "bmi": None}) is True

    def test_calculate_due_date(self):
        """Test due date calculation (every 3 years)."""
        screening = DiabetesScreening("patient_id")
        last_date = date(2021, 1, 1)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2024, 1, 1)


class TestLungScreening:
    """Test lung cancer screening logic."""

    def test_is_applicable_with_smoking_history(self):
        """Test applicability for age 50-80 with 20+ pack-years."""
        screening = LungScreening("patient_id")
        assert screening.is_applicable({"age": 50, "pack_years": 20}) is True
        assert screening.is_applicable({"age": 65, "pack_years": 30}) is True
        assert screening.is_applicable({"age": 80, "pack_years": 25}) is True

    def test_is_not_applicable_insufficient_smoking_history(self):
        """Test not applicable with insufficient smoking history."""
        screening = LungScreening("patient_id")
        assert screening.is_applicable({"age": 60, "pack_years": 19}) is False
        assert screening.is_applicable({"age": 60, "pack_years": 0}) is False

    def test_is_not_applicable_outside_age_range(self):
        """Test not applicable outside age range."""
        screening = LungScreening("patient_id")
        assert screening.is_applicable({"age": 49, "pack_years": 30}) is False
        assert screening.is_applicable({"age": 81, "pack_years": 30}) is False

    def test_calculate_due_date(self):
        """Test due date calculation (annually)."""
        screening = LungScreening("patient_id")
        last_date = date(2024, 5, 1)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2025, 5, 1)


class TestCervicalScreening:
    """Test cervical cancer screening logic."""

    def test_is_applicable_women_21_to_65(self):
        """Test applicability for women 21-65."""
        screening = CervicalScreening("patient_id")
        assert screening.is_applicable({"age": 21, "sex": "female"}) is True
        assert screening.is_applicable({"age": 40, "sex": "female"}) is True
        assert screening.is_applicable({"age": 65, "sex": "female"}) is True

    def test_is_not_applicable_men(self):
        """Test not applicable for men."""
        screening = CervicalScreening("patient_id")
        assert screening.is_applicable({"age": 30, "sex": "male"}) is False

    def test_is_not_applicable_outside_age_range(self):
        """Test not applicable outside age range."""
        screening = CervicalScreening("patient_id")
        assert screening.is_applicable({"age": 20, "sex": "female"}) is False
        assert screening.is_applicable({"age": 66, "sex": "female"}) is False

    def test_calculate_due_date(self):
        """Test due date calculation (every 5 years default)."""
        screening = CervicalScreening("patient_id")
        last_date = date(2020, 1, 1)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2025, 1, 1)


class TestStatinScreening:
    """Test statin for CVD prevention logic."""

    def test_is_applicable_with_diabetes(self):
        """Test applicability with diabetes diagnosis."""
        screening = StatinScreening("patient_id")
        assert screening.is_applicable({
            "age": 50,
            "conditions": ["E11.9"],  # Type 2 diabetes
            "is_smoker": False
        }) is True

    def test_is_applicable_with_hypertension(self):
        """Test applicability with hypertension."""
        screening = StatinScreening("patient_id")
        assert screening.is_applicable({
            "age": 60,
            "conditions": ["I10"],  # Hypertension
            "is_smoker": False
        }) is True

    def test_is_applicable_with_dyslipidemia(self):
        """Test applicability with dyslipidemia."""
        screening = StatinScreening("patient_id")
        assert screening.is_applicable({
            "age": 55,
            "conditions": ["E78.5"],  # Hyperlipidemia
            "is_smoker": False
        }) is True

    def test_is_applicable_with_smoking(self):
        """Test applicability with smoking."""
        screening = StatinScreening("patient_id")
        assert screening.is_applicable({
            "age": 50,
            "conditions": [],
            "is_smoker": True
        }) is True

    def test_is_not_applicable_no_risk_factors(self):
        """Test not applicable without risk factors."""
        screening = StatinScreening("patient_id")
        assert screening.is_applicable({
            "age": 50,
            "conditions": [],
            "is_smoker": False
        }) is False

    def test_is_not_applicable_outside_age_range(self):
        """Test not applicable outside age range."""
        screening = StatinScreening("patient_id")
        assert screening.is_applicable({
            "age": 39,
            "conditions": ["I10"],
            "is_smoker": False
        }) is False

    def test_calculate_due_date(self):
        """Test due date calculation (every 5 years)."""
        screening = StatinScreening("patient_id")
        last_date = date(2020, 1, 1)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2025, 1, 1)


class TestAlcoholScreening:
    """Test alcohol use screening logic."""

    def test_is_applicable_all_adults(self):
        """Test applicability for all adults 18+."""
        screening = AlcoholScreening("patient_id")
        assert screening.is_applicable({"age": 18}) is True
        assert screening.is_applicable({"age": 50}) is True
        assert screening.is_applicable({"age": 85}) is True

    def test_is_not_applicable_under_18(self):
        """Test not applicable under 18."""
        screening = AlcoholScreening("patient_id")
        assert screening.is_applicable({"age": 17}) is False

    def test_calculate_due_date(self):
        """Test due date calculation (annually)."""
        screening = AlcoholScreening("patient_id")
        last_date = date(2024, 6, 10)
        due_date = screening.calculate_due_date(last_date)
        assert due_date == date(2025, 6, 10)


class TestScreeningEvaluation:
    """Test full screening evaluation."""

    def test_screening_up_to_date(self):
        """Test screening marked as up-to-date."""
        screening = HypertensionScreening("patient_id")
        patient_data = {"age": 50, "sex": "male"}
        screening_data = {
            "observations": [
                {"code": "8480-6", "date": date.today() - timedelta(days=30)},
            ],
            "procedures": [],
            "manual_entries": {},
        }

        result = screening.evaluate(patient_data, screening_data)
        assert result.status == ScreeningStatus.UP_TO_DATE
        assert result.applicable is True
        assert result.last_date is not None

    def test_screening_overdue(self):
        """Test screening marked as overdue."""
        screening = HypertensionScreening("patient_id")
        patient_data = {"age": 50, "sex": "male"}
        screening_data = {
            "observations": [
                {"code": "8480-6", "date": date.today() - timedelta(days=400)},
            ],
            "procedures": [],
            "manual_entries": {},
        }

        result = screening.evaluate(patient_data, screening_data)
        assert result.status == ScreeningStatus.OVERDUE
        assert result.applicable is True

    def test_screening_never_done(self):
        """Test screening never done (marked as overdue)."""
        screening = HypertensionScreening("patient_id")
        patient_data = {"age": 50, "sex": "male"}
        screening_data = {
            "observations": [],
            "procedures": [],
            "manual_entries": {},
        }

        result = screening.evaluate(patient_data, screening_data)
        assert result.status == ScreeningStatus.OVERDUE
        assert result.applicable is True
        assert result.last_date is None

    def test_screening_not_applicable(self):
        """Test screening not applicable."""
        screening = BreastScreening("patient_id")
        patient_data = {"age": 50, "sex": "male"}
        screening_data = {
            "observations": [],
            "procedures": [],
            "manual_entries": {},
        }

        result = screening.evaluate(patient_data, screening_data)
        assert result.status == ScreeningStatus.NOT_APPLICABLE
        assert result.applicable is False
