from __future__ import annotations

import unittest
from unittest.mock import patch

from characterization.config import config
from characterization.helpers.fileset_selector import select_fileset_for_wavelength


class TestFilesetSelector(unittest.TestCase):
    def test_prefers_expected_run_when_available(self):
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5", "532_FW5"]}}):
            selection = select_fileset_for_wavelength(
                fileset_keys=["1064_FW5", "532_FW4", "532_FW5"],
                wavelength="532",
                sensor_id="3.0",
            )
        self.assertEqual(selection.selected_key, "532_FW5")
        self.assertEqual(selection.reason, "expected_match")

    def test_falls_back_to_single_candidate_when_expected_missing(self):
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5", "532_FW5"]}}):
            selection = select_fileset_for_wavelength(
                fileset_keys=["1064_FW5", "532_FW4"],
                wavelength="532",
                sensor_id="3.0",
            )
        self.assertEqual(selection.selected_key, "532_FW4")
        self.assertEqual(selection.reason, "single_candidate")

    def test_lexicographic_fallback_when_ambiguous_and_no_expected(self):
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5"]}}):
            selection = select_fileset_for_wavelength(
                fileset_keys=["532_FW5", "532_FW4"],
                wavelength="532",
                sensor_id="3.0",
            )
        self.assertEqual(selection.selected_key, "532_FW4")
        self.assertEqual(selection.reason, "lexicographic_fallback")

    def test_missing_wavelength_returns_none(self):
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5", "532_FW4"]}}):
            selection = select_fileset_for_wavelength(
                fileset_keys=["1064_FW5"],
                wavelength="532",
                sensor_id="3.0",
            )
        self.assertIsNone(selection.selected_key)
        self.assertEqual(selection.reason, "missing")


if __name__ == "__main__":
    unittest.main()
