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
        payload["analysis"]["lr_refpd_vs_adc_by_wavelength_gain"] = {
            "1064_G1": {
                "lr_refpd_vs_adc_summary": {
                    "num_photodiodes": 1,
                    "slope_mean": 1.0,
                    "slope_median": 1.0,
                    "slope_std": 0.0,
                    "intercept_mean": 0.1,
                    "intercept_median": 0.1,
                    "intercept_std": 0.0,
                    "r_value_median": 0.99,
                },
                "lr_refpd_vs_adc_relative_deviation_by_pd": [
                    {"sensor_id": "0.0", "slope_rel_dev_pct": 0.0}
                ],
            }
        }
        payload["analysis"]["adc_to_power_by_wavelength_gain"] = {
            "1064_G1": {
                "adc_to_power_summary": {
                    "num_photodiodes": 1,
                    "slope_mean": 2.0,
                    "slope_median": 2.0,
                    "slope_std": 0.0,
                    "intercept_mean": 0.2,
                    "intercept_median": 0.2,
                    "intercept_std": 0.0,
                }
            }
        }
        payload["plots"]["relative_slope_deviation_by_gain_1064"] = "plots/relative_slope_deviation_by_gain_1064.pdf"
        payload["plots"]["linreg_voltage_slope_vs_intercept_1064"] = "plots/linreg_voltage_slope_vs_intercept_1064.pdf"
        payload["plots"]["linreg_power_slope_vs_intercept_1064"] = "plots/linreg_power_slope_vs_intercept_1064.pdf"

        report_data = ReportData.from_dict(payload)
        self.assertIn("1064_G1", report_data.analysis.lr_refpd_vs_adc_by_wavelength_gain)
        grp = report_data.analysis.lr_refpd_vs_adc_by_wavelength_gain["1064_G1"]
        self.assertIsNotNone(grp.lr_refpd_vs_adc_summary)
        self.assertEqual(grp.lr_refpd_vs_adc_summary.num_photodiodes, 1)
        self.assertIn("1064_G1", report_data.analysis.adc_to_power_by_wavelength_gain)
        power_grp = report_data.analysis.adc_to_power_by_wavelength_gain["1064_G1"]
        self.assertIsNotNone(power_grp.adc_to_power_summary)
        self.assertEqual(power_grp.adc_to_power_summary.slope_mean, 2.0)
        self.assertEqual(report_data.plots.relative_slope_deviation_by_gain_1064, "plots/relative_slope_deviation_by_gain_1064.pdf")
        self.assertEqual(report_data.plots.linreg_voltage_slope_vs_intercept_1064, "plots/linreg_voltage_slope_vs_intercept_1064.pdf")
        self.assertEqual(report_data.plots.linreg_power_slope_vs_intercept_1064, "plots/linreg_power_slope_vs_intercept_1064.pdf")


if __name__ == "__main__":
    unittest.main()
