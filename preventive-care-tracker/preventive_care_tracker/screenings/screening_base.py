"""Base classes for preventive care screenings."""

from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional
from abc import ABC, abstractmethod


class ScreeningStatus(Enum):
    """Status of a preventive care screening."""
    UP_TO_DATE = "up-to-date"
    OVERDUE = "overdue"
    NOT_APPLICABLE = "not-applicable"


@dataclass
class ScreeningResult:
    """Result of a preventive care screening evaluation."""
    name: str
    status: ScreeningStatus
    last_date: Optional[date]
    due_date: Optional[date]
    grade: str
    applicable: bool
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_date": self.last_date.isoformat() if self.last_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "grade": self.grade,
            "applicable": self.applicable,
            "notes": self.notes,
        }


class BaseScreening(ABC):
    """Base class for preventive care screening logic."""

    def __init__(self, patient_id: str):
        """Initialize screening with patient ID.

        Args:
            patient_id: Canvas patient identifier
        """
        self.patient_id = patient_id

    @abstractmethod
    def is_applicable(self, patient_data: dict) -> bool:
        """Check if screening applies to this patient.

        Args:
            patient_data: Dictionary with patient demographics
                - age: int
                - sex: str ("male" or "female")
                - conditions: list of ICD-10 codes
                - smoking_history: dict with pack_years

        Returns:
            True if screening applies to this patient
        """
        pass

    @abstractmethod
    def get_last_screening_date(self, data: dict) -> Optional[date]:
        """Get the most recent screening date from all sources.

        Args:
            data: Dictionary containing:
                - observations: list of observation records
                - procedures: list of procedure records
                - imaging_reports: list of imaging report records
                - manual_entries: list of manual questionnaire entries
                - conditions: list of condition records
                - medications: list of medication records

        Returns:
            Most recent screening date or None if never screened
        """
        pass

    @abstractmethod
    def calculate_due_date(self, last_date: Optional[date]) -> Optional[date]:
        """Calculate next due date based on screening interval.

        Args:
            last_date: Date of last screening (None if never done)

        Returns:
            Next recommended screening date or None if not applicable
        """
        pass

    @abstractmethod
    def get_screening_name(self) -> str:
        """Get the display name of this screening."""
        pass

    @abstractmethod
    def get_uspstf_grade(self) -> str:
        """Get the USPSTF recommendation grade (A or B)."""
        pass

    def evaluate(self, patient_data: dict, screening_data: dict) -> ScreeningResult:
        """Evaluate screening status for a patient.

        Args:
            patient_data: Patient demographics and history
            screening_data: Screening records from various sources

        Returns:
            ScreeningResult with status, dates, and applicability
        """
        applicable = self.is_applicable(patient_data)

        if not applicable:
            return ScreeningResult(
                name=self.get_screening_name(),
                status=ScreeningStatus.NOT_APPLICABLE,
                last_date=None,
                due_date=None,
                grade=self.get_uspstf_grade(),
                applicable=False,
                notes="Not applicable to this patient"
            )

        last_date = self.get_last_screening_date(screening_data)
        due_date = self.calculate_due_date(last_date)

        # Determine status
        if last_date is None:
            status = ScreeningStatus.OVERDUE
            notes = "Never screened"
        elif due_date and datetime.now().date() > due_date:
            status = ScreeningStatus.OVERDUE
            notes = f"Last screened {last_date.isoformat()}"
        else:
            status = ScreeningStatus.UP_TO_DATE
            notes = f"Last screened {last_date.isoformat()}"

        return ScreeningResult(
            name=self.get_screening_name(),
            status=status,
            last_date=last_date,
            due_date=due_date,
            grade=self.get_uspstf_grade(),
            applicable=True,
            notes=notes
        )


def parse_date(date_value) -> Optional[date]:
    """Parse various date formats into a date object.

    Args:
        date_value: String, date, or datetime object

    Returns:
        date object or None if parsing fails
    """
    if date_value is None:
        return None

    if isinstance(date_value, date):
        return date_value

    if isinstance(date_value, datetime):
        return date_value.date()

    if isinstance(date_value, str):
        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_value, fmt).date()
            except ValueError:
                continue

    return None


def get_most_recent_date(dates: list) -> Optional[date]:
    """Get the most recent date from a list of dates.

    Args:
        dates: List of date objects or date strings

    Returns:
        Most recent date or None if list is empty
    """
    parsed_dates = [parse_date(d) for d in dates if d is not None]
    valid_dates = [d for d in parsed_dates if d is not None]

    if not valid_dates:
        return None

    return max(valid_dates)


def add_years(start_date: date, years: int) -> date:
    """Add years to a date, handling leap years.

    Args:
        start_date: Starting date
        years: Number of years to add

    Returns:
        New date with years added
    """
    try:
        return start_date.replace(year=start_date.year + years)
    except ValueError:
        # Handle Feb 29 in leap years
        return start_date.replace(year=start_date.year + years, day=28)
