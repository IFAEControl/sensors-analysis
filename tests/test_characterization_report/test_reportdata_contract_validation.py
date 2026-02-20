from __future__ import annotations

import unittest

from characterization_report.helpers.data_holders import ReportData
from tests.contract_fixtures import make_valid_extended_payload


class TestReportDataContractValidation(unittest.TestCase):
    def test_report_data_rejects_invalid_contract(self):
        payload = make_valid_extended_payload(generate_plots=True)
        del payload["analysis"]["photodiodes"]
        with self.assertRaises(ValueError):
            ReportData.from_dict(payload)

    def test_report_data_accepts_valid_contract(self):
        payload = make_valid_extended_payload(generate_plots=True)
        report_data = ReportData.from_dict(payload)
        self.assertEqual(report_data.meta.charact_id, "test_char")
        self.assertIn("0.0", report_data.analysis.photodiodes)


if __name__ == "__main__":
    unittest.main()
