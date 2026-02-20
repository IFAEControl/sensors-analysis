from __future__ import annotations

import unittest
from unittest.mock import patch

from characterization.config import config
from characterization.elements.characterization import Characterization


class TestCalibrationPedestalMismatch(unittest.TestCase):
    def test_extract_calibration_subtract_from_meta_config(self):
        cal_data = {"meta": {"config": {"subtract_pedestals": True}}}
        self.assertTrue(Characterization._extract_calibration_subtract_pedestals(cal_data))

    def test_extract_calibration_subtract_from_call_args_inverse(self):
        cal_data = {"meta": {"calling_arguments": {"do_not_sub_pedestals": True}}}
        self.assertFalse(Characterization._extract_calibration_subtract_pedestals(cal_data))

    def test_adds_warning_issue_on_mismatch(self):
        c = Characterization.__new__(Characterization)
        c.issues = []
        with patch.object(config, "subtract_pedestals", True):
            c._add_pedestal_setting_mismatch_issue(
                calibration_subtract_pedestals=False,
                calibration_summary_path="/tmp/calib.json",
            )
        self.assertEqual(len(c.issues), 1)
        self.assertEqual(c.issues[0]["level"], "warning")
        self.assertIn("calibration_subtract_pedestals", c.issues[0]["meta"])
        self.assertIn("characterization_subtract_pedestals", c.issues[0]["meta"])

    def test_no_warning_issue_when_settings_match(self):
        c = Characterization.__new__(Characterization)
        c.issues = []
        with patch.object(config, "subtract_pedestals", False):
            c._add_pedestal_setting_mismatch_issue(
                calibration_subtract_pedestals=False,
                calibration_summary_path="/tmp/calib.json",
            )
        self.assertEqual(c.issues, [])


if __name__ == "__main__":
    unittest.main()
