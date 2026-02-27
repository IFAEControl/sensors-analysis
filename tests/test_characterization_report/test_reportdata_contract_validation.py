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
        payload["issues"]["PD_0.0"] = [{"description": "pd issue", "level": "warning", "meta": {"k": "v"}}]
        report_data = ReportData.from_dict(payload)
        self.assertEqual(report_data.meta.charact_id, "test_char")
        self.assertIn("0.0", report_data.analysis.photodiodes)
        self.assertIn("PD_0.0", report_data.issues)
        self.assertEqual(report_data.issues["PD_0.0"][0].level, "warning")

    def test_report_data_parses_new_characterization_level_group_fields(self):
        payload = make_valid_extended_payload(generate_plots=True)
        payload["analysis"]["linreg_by_wavelength_filter"] = {
            "1064_FW5": {
                "summary": {
                    "num_photodiodes": 1,
                    "slope_mean": 1.0,
                    "slope_median": 1.0,
                    "slope_std": 0.0,
                    "intercept_mean": 0.1,
                    "intercept_median": 0.1,
                    "intercept_std": 0.0,
                    "r_value_median": 0.99,
                },
                "relative_deviation_by_pd": [
                    {"sensor_id": "0.0", "slope_rel_dev_pct": 0.0}
                ],
            }
        }
        payload["plots"]["relative_slope_deviation_by_gain_1064"] = "plots/relative_slope_deviation_by_gain_1064.pdf"
        payload["plots"]["linreg_voltage_slope_vs_intercept_1064"] = "plots/linreg_voltage_slope_vs_intercept_1064.pdf"
        payload["plots"]["linreg_power_slope_vs_intercept_1064"] = "plots/linreg_power_slope_vs_intercept_1064.pdf"

        report_data = ReportData.from_dict(payload)
        self.assertIn("1064_FW5", report_data.analysis.linreg_by_wavelength_filter)
        grp = report_data.analysis.linreg_by_wavelength_filter["1064_FW5"]
        self.assertIsNotNone(grp.summary)
        self.assertEqual(grp.summary.num_photodiodes, 1)
        self.assertEqual(report_data.plots.relative_slope_deviation_by_gain_1064, "plots/relative_slope_deviation_by_gain_1064.pdf")
        self.assertEqual(report_data.plots.linreg_voltage_slope_vs_intercept_1064, "plots/linreg_voltage_slope_vs_intercept_1064.pdf")
        self.assertEqual(report_data.plots.linreg_power_slope_vs_intercept_1064, "plots/linreg_power_slope_vs_intercept_1064.pdf")


if __name__ == "__main__":
    unittest.main()
