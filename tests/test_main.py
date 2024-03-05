import csv
import unittest
from spending_tracker.main import autopct_format, overall_usage


class TestCSVData(unittest.TestCase):
    def setUp(self):
        self.csv_data = "Amount,Category\n" \
                        "13,Food\n" \
                        "150,Food\n" \
                        "25,Entertainment\n" \
                        "50,Entertainment\n" \
                        "70,Necessities\n" \
                        "40,Cash\n" \
                        "40,Cash\n" \
                        "14,Cash\n" \
                        "15.14,Bills\n"

    def test_autopct_format(self):
        self.assertEqual(autopct_format(25), '£104.28\n(25.00%)')
        self.assertEqual(autopct_format(50), '£208.57\n(50.00%)')
        self.assertEqual(autopct_format(75), '£312.86\n(75.00%)')

    def test_valid_category_totals(self):
        self.assertEqual(overall_usage.get('Food', 0), 163.0)
        self.assertEqual(overall_usage.get('Entertainment', 0), 75.0)

    def test_calculate_totals(self):
        totals = {}
        csv_reader = csv.DictReader(self.csv_data.splitlines())
        for row in csv_reader:
            category = row['Category']
            amount = float(row['Amount'])
            if category in totals:
                totals[category] += amount
            else:
                totals[category] = amount

        self.assertEqual(totals['Food'], 163)
        self.assertEqual(totals['Entertainment'], 75)
        self.assertEqual(totals['Necessities'], 70)
        self.assertEqual(totals['Cash'], 94)
        self.assertEqual(totals['Bills'], 15.14)


if __name__ == '__main__':
    unittest.main()
