"""Unit tests for Preventive Care Tracker application."""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, MagicMock, patch
from preventive_care_tracker.applications.simple_preventive_care_app import PreventiveCareTrackerApp


class TestPreventiveCareTrackerApp:
    """Test the Preventive Care Tracker application."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock event with context
        mock_event = Mock()
        mock_event.target.id = "test-event-123"
        mock_event.context = {"patient": {"id": "test-patient-123"}}
        self.app = PreventiveCareTrackerApp(mock_event)

    def test_parse_date_string_valid_formats(self):
        """Test parsing valid date strings in different formats."""
        # Use self.app from setup
        # MM/DD/YYYY format
        assert self.app._parse_date_string("12/04/2025") == date(2025, 12, 4)

        # MM/DD/YY format
        assert self.app._parse_date_string("12/04/25") == date(2025, 12, 4)

        # YYYY-MM-DD format
        assert self.app._parse_date_string("2025-12-04") == date(2025, 12, 4)

        # MM-DD-YYYY format
        assert self.app._parse_date_string("12-04-2025") == date(2025, 12, 4)

        # MM/YYYY format (month/year only)
        result = self.app._parse_date_string("12/2025")
        assert result.year == 2025
        assert result.month == 12

    def test_parse_date_string_invalid(self):
        """Test parsing invalid date strings returns None."""
        assert self.app._parse_date_string("invalid-date") is None
        assert self.app._parse_date_string("") is None
        assert self.app._parse_date_string(None) is None

    def test_parse_date_string_strips_whitespace(self):
        """Test that date string is stripped of whitespace."""
        assert self.app._parse_date_string("  12/04/2025  ") == date(2025, 12, 4)

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Patient')
    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Command')
    def test_get_latest_screening_dates_no_questionnaires(self, mock_command, mock_patient):
        """Test when no questionnaires exist."""
        app = self.app

        # Mock patient
        mock_patient_obj = Mock()
        mock_patient_obj.id = "test-patient-123"

        # Mock empty command queryset
        mock_commands = Mock()
        mock_commands.count.return_value = 0
        mock_commands.__iter__ = Mock(return_value=iter([]))
        mock_command.objects.filter.return_value.order_by.return_value = mock_commands

        result = app._get_latest_screening_dates(mock_patient_obj)

        assert result is None

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Patient')
    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Command')
    def test_get_latest_screening_dates_single_questionnaire(self, mock_command, mock_patient):
        """Test with a single questionnaire submission."""
        app = self.app

        # Mock patient
        mock_patient_obj = Mock()
        mock_patient_obj.id = "test-patient-123"

        # Mock command with questionnaire data
        mock_cmd = Mock()
        mock_cmd.data = {
            'questionnaire': {
                'text': 'Preventive Care Screening Dates',
                'extra': {
                    'questions': [
                        {
                            'pk': 180,
                            'coding': {'code': 'HYPERTENSION_DATE'}
                        }
                    ]
                }
            },
            'question-180': '10/10/2024'
        }

        mock_commands = Mock()
        mock_commands.count.return_value = 1
        mock_commands.__iter__ = Mock(return_value=iter([mock_cmd]))
        mock_command.objects.filter.return_value.order_by.return_value = mock_commands

        result = app._get_latest_screening_dates(mock_patient_obj)

        assert result is not None
        assert 'HYPERTENSION_DATE' in result
        assert result['HYPERTENSION_DATE'] == '10/10/2024'

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Patient')
    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Command')
    def test_get_latest_screening_dates_multiple_questionnaires(self, mock_command, mock_patient):
        """Test with multiple questionnaires - should get most recent date for each screening."""
        app = self.app

        # Mock patient
        mock_patient_obj = Mock()
        mock_patient_obj.id = "test-patient-123"

        # Mock first command (older)
        mock_cmd1 = Mock()
        mock_cmd1.data = {
            'questionnaire': {
                'text': 'Preventive Care Screening Dates',
                'extra': {
                    'questions': [
                        {'pk': 180, 'coding': {'code': 'HYPERTENSION_DATE'}},
                        {'pk': 181, 'coding': {'code': 'DEPRESSION_DATE'}}
                    ]
                }
            },
            'question-180': '01/01/2024',  # Older date
            'question-181': '02/01/2024'
        }

        # Mock second command (newer)
        mock_cmd2 = Mock()
        mock_cmd2.data = {
            'questionnaire': {
                'text': 'Preventive Care Screening Dates',
                'extra': {
                    'questions': [
                        {'pk': 180, 'coding': {'code': 'HYPERTENSION_DATE'}},
                        {'pk': 182, 'coding': {'code': 'DIABETES_DATE'}}
                    ]
                }
            },
            'question-180': '10/10/2024',  # Newer date
            'question-182': '05/15/2024'
        }

        mock_commands = Mock()
        mock_commands.count.return_value = 2
        mock_commands.__iter__ = Mock(return_value=iter([mock_cmd2, mock_cmd1]))  # Ordered by -created
        mock_command.objects.filter.return_value.order_by.return_value = mock_commands

        result = app._get_latest_screening_dates(mock_patient_obj)

        assert result is not None
        # Should have most recent hypertension date from second questionnaire
        assert result['HYPERTENSION_DATE'] == '10/10/2024'
        # Should have depression date from first questionnaire (only one with it)
        assert result['DEPRESSION_DATE'] == '02/01/2024'
        # Should have diabetes date from second questionnaire (only one with it)
        assert result['DIABETES_DATE'] == '05/15/2024'

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Patient')
    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Command')
    def test_get_latest_screening_dates_skips_empty_responses(self, mock_command, mock_patient):
        """Test that empty/blank responses are skipped."""
        app = self.app

        # Mock patient
        mock_patient_obj = Mock()
        mock_patient_obj.id = "test-patient-123"

        # Mock command with empty responses
        mock_cmd = Mock()
        mock_cmd.data = {
            'questionnaire': {
                'text': 'Preventive Care Screening Dates',
                'extra': {
                    'questions': [
                        {'pk': 180, 'coding': {'code': 'HYPERTENSION_DATE'}},
                        {'pk': 181, 'coding': {'code': 'DEPRESSION_DATE'}}
                    ]
                }
            },
            'question-180': '10/10/2024',
            'question-181': ''  # Empty response
        }

        mock_commands = Mock()
        mock_commands.count.return_value = 1
        mock_commands.__iter__ = Mock(return_value=iter([mock_cmd]))
        mock_command.objects.filter.return_value.order_by.return_value = mock_commands

        result = app._get_latest_screening_dates(mock_patient_obj)

        assert result is not None
        assert 'HYPERTENSION_DATE' in result
        # Depression date should not be in result since it was empty
        assert 'DEPRESSION_DATE' not in result

    def test_render_html_basic_structure(self):
        """Test that HTML is rendered with correct structure."""
        app = self.app

        mock_patient = Mock()
        mock_patient.first_name = "John"
        mock_patient.last_name = "Doe"

        screenings = [
            {"name": "Hypertension Screening", "last_date": "10/10/2024"},
            {"name": "Depression Screening", "last_date": "Never"}
        ]

        html = app._render_html(mock_patient, age=45, screenings=screenings)

        # Check basic structure
        assert "Preventive Care Tracker" in html
        assert "John Doe" in html
        assert "Age: 45" in html
        assert "Hypertension Screening" in html
        assert "10/10/2024" in html
        assert "Depression Screening" in html
        assert "Never" in html

    def test_render_html_unknown_age(self):
        """Test HTML rendering with unknown age."""
        app = self.app

        mock_patient = Mock()
        mock_patient.first_name = "Jane"
        mock_patient.last_name = "Smith"

        screenings = []

        html = app._render_html(mock_patient, age=None, screenings=screenings)

        assert "Age: Unknown" in html

    def test_render_html_canvas_styling(self):
        """Test that Canvas branding styles are applied."""
        app = self.app

        mock_patient = Mock()
        mock_patient.first_name = "Test"
        mock_patient.last_name = "User"

        screenings = [{"name": "Test Screening", "last_date": "Never"}]

        html = app._render_html(mock_patient, age=50, screenings=screenings)

        # Check for teal gradient header
        assert "#1b9aaa" in html
        assert "#16808e" in html

        # Check for modern typography
        assert "BlinkMacSystemFont" in html or "Segoe UI" in html

        # Check for footer note
        assert "Showing most recent date" in html

    def test_render_error(self):
        """Test error message rendering."""
        app = self.app

        error_html = app._render_error("Test error message")

        assert "Error" in error_html
        assert "Test error message" in error_html
        # Check for error styling
        assert "#dc3545" in error_html

    def test_evaluate_screenings_creates_correct_structure(self):
        """Test that _evaluate_screenings returns correct data structure."""
        app = self.app

        with patch.object(app, '_get_latest_screening_dates') as mock_get_dates:
            mock_get_dates.return_value = {
                'HYPERTENSION_DATE': '10/10/2024',
                'DEPRESSION_DATE': '05/15/2024'
            }

            mock_patient = Mock()
            mock_patient.id = "test-123"

            result = app._evaluate_screenings(mock_patient, age=50, sex="male")

            # Should return list of screenings
            assert isinstance(result, list)
            assert len(result) == 9  # All 9 screening types

            # Check structure of each screening
            for screening in result:
                assert "name" in screening
                assert "last_date" in screening

            # Check specific screenings
            hypertension = next(s for s in result if s["name"] == "Hypertension Screening")
            assert hypertension["last_date"] == "10/10/2024"

            depression = next(s for s in result if s["name"] == "Depression Screening")
            assert depression["last_date"] == "05/15/2024"

            # Check screening without data shows "Never"
            alcohol = next(s for s in result if s["name"] == "Alcohol Use Screening")
            assert alcohol["last_date"] == "Never"

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Patient')
    def test_on_open_success(self, mock_patient_class):
        """Test successful on_open flow."""
        # Mock patient
        mock_patient = Mock()
        mock_patient.first_name = "John"
        mock_patient.last_name = "Doe"
        mock_patient.birth_date = date(1980, 5, 15)
        mock_patient.sex_at_birth = "male"
        mock_patient_class.objects.get.return_value = mock_patient

        # Mock the evaluation method
        with patch.object(self.app, '_evaluate_screenings') as mock_eval:
            mock_eval.return_value = [
                {"name": "Hypertension Screening", "last_date": "10/10/2024"}
            ]

            result = self.app.on_open()

            # Should return LaunchModalEffect
            assert result is not None
            mock_patient_class.objects.get.assert_called_once()
            mock_eval.assert_called_once()

    def test_on_open_no_patient_context(self):
        """Test on_open when no patient context is available."""
        # Create app without patient context
        mock_event = Mock()
        mock_event.context = {}
        app = PreventiveCareTrackerApp(mock_event)

        result = app.on_open()

        # Should return error effect
        assert result is not None

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Patient')
    def test_on_open_patient_not_found(self, mock_patient_class):
        """Test on_open when patient is not found."""
        mock_patient_class.objects.get.side_effect = Exception("Patient not found")

        result = self.app.on_open()

        # Should return error effect
        assert result is not None

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Patient')
    def test_on_open_patient_no_birthdate(self, mock_patient_class):
        """Test on_open with patient that has no birth date."""
        mock_patient = Mock()
        mock_patient.first_name = "Jane"
        mock_patient.last_name = "Smith"
        mock_patient.birth_date = None
        mock_patient.sex_at_birth = "female"
        mock_patient_class.objects.get.return_value = mock_patient

        with patch.object(self.app, '_evaluate_screenings') as mock_eval:
            mock_eval.return_value = []

            result = self.app.on_open()

            assert result is not None
            # Age should be None when birthdate is missing
            mock_eval.assert_called_once()
            # Check that age is None in the call arguments
            call_args = mock_eval.call_args
            # Get positional args: (patient, age, sex)
            assert call_args[0][1] is None  # age parameter (second positional arg)

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Command')
    def test_get_latest_screening_dates_exception_handling(self, mock_command):
        """Test exception handling in _get_latest_screening_dates."""
        mock_patient = Mock()
        mock_patient.id = "test-123"

        # Make the query raise an exception
        mock_command.objects.filter.side_effect = Exception("Database error")

        result = self.app._get_latest_screening_dates(mock_patient)

        # Should return None on error
        assert result is None

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Command')
    def test_get_latest_screening_dates_command_no_data(self, mock_command):
        """Test handling of command with no data."""
        mock_patient = Mock()
        mock_patient.id = "test-123"

        # Mock command without data
        mock_cmd = Mock()
        mock_cmd.data = None

        mock_commands = Mock()
        mock_commands.count.return_value = 1
        mock_commands.__iter__ = Mock(return_value=iter([mock_cmd]))
        mock_command.objects.filter.return_value.order_by.return_value = mock_commands

        result = self.app._get_latest_screening_dates(mock_patient)

        # Should return None when no valid data
        assert result is None

    @patch('preventive_care_tracker.applications.simple_preventive_care_app.Command')
    def test_get_latest_screening_dates_invalid_date_format(self, mock_command):
        """Test handling of invalid date formats in questionnaire."""
        mock_patient = Mock()
        mock_patient.id = "test-123"

        # Mock command with invalid date
        mock_cmd = Mock()
        mock_cmd.data = {
            'questionnaire': {
                'text': 'Preventive Care Screening Dates',
                'extra': {
                    'questions': [
                        {'pk': 180, 'coding': {'code': 'HYPERTENSION_DATE'}}
                    ]
                }
            },
            'question-180': 'invalid-date-format'
        }

        mock_commands = Mock()
        mock_commands.count.return_value = 1
        mock_commands.__iter__ = Mock(return_value=iter([mock_cmd]))
        mock_command.objects.filter.return_value.order_by.return_value = mock_commands

        result = self.app._get_latest_screening_dates(mock_patient)

        # Should return None or empty dict when date can't be parsed
        assert result is None or result == {}
