import os
import tempfile
import unittest
from unittest.mock import patch
from spending_tracker.main import main, csv_reader, get_autopct_formatter, pie_chart_data_gathering


class TestSpendingTracker(unittest.TestCase):

    def test_csv_reader_invalid_path(self):
        invalid_path = 'non_existent_file.csv'
        result = csv_reader(invalid_path)
        self.assertEqual(False, result["status"])
        self.assertEqual("File not found.", result["message"])

    def test_csv_reader_permission_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_csv_path = os.path.join(temp_dir, 'mock_file.csv')
            print(mock_csv_path)
            csv_content = "category,amount\nFood,50\nEntertainment,30\n"
            with open(mock_csv_path, 'w') as file:
                file.write(csv_content)
            # Mock the open function to raise a PermissionError
            with patch('builtins.open', side_effect=PermissionError):
                result = csv_reader(mock_csv_path)
                self.assertEqual(False, result["status"])
                self.assertEqual("Input file cannot be read.", result["message"])

    def test_csv_reader_negative_amount(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_csv_path = os.path.join(temp_dir, 'mock_file.csv')
            csv_content = "category,amount\nFood,-50\nEntertainment,30\n"
            with open(mock_csv_path, 'w') as file:
                file.write(csv_content)
            with patch('builtins.print') as mock_print:
                result = csv_reader(mock_csv_path)
            self.assertEqual(result, {'Entertainment': 30.0})
            mock_print.assert_called_once_with("Amount must be positive!")

    def test_autopct_formatting_for_percentage_0(self):
        sizes = [100, 0]
        formatter = get_autopct_formatter(sizes)
        expected_result = '£0.00\n(0.00%)'
        self.assertEqual(formatter(0), expected_result)

    def test_autopct_formatting_for_percentage_1(self):
        sizes = [99, 1]
        formatter = get_autopct_formatter(sizes)
        expected_result = '£1.00\n(1.00%)'
        self.assertEqual(formatter(1), expected_result)

    def test_autopct_formatting_for_single_value(self):
        single_formatter = get_autopct_formatter([100])
        self.assertEqual(single_formatter(100), '£100.00\n(100.00%)')

    def test_pie_chart_data_gathering(self):
        empty_formatter = pie_chart_data_gathering({})
        expected_result = "Unable to generate pie chart."
        self.assertEqual(empty_formatter, expected_result)


if __name__ == '__main__':
    unittest.main()
