"""Screening modules for preventive care measures."""

from .base import ScreeningResult, ScreeningStatus
from .colorectal import ColorectalScreening
from .breast import BreastScreening
from .hypertension import HypertensionScreening
from .depression import DepressionScreening
from .diabetes import DiabetesScreening
from .lung import LungScreening
from .cervical import CervicalScreening
from .statin import StatinScreening
from .alcohol import AlcoholScreening

__all__ = [
    "ScreeningResult",
    "ScreeningStatus",
    "ColorectalScreening",
    "BreastScreening",
    "HypertensionScreening",
    "DepressionScreening",
    "DiabetesScreening",
    "LungScreening",
    "CervicalScreening",
    "StatinScreening",
    "AlcoholScreening",
]
