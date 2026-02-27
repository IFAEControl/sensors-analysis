from __future__ import annotations

import unittest
from unittest.mock import patch

from characterization.config import config
from characterization.elements.plots.characterization_plots import CharacterizationPlots


class TestCharacterizationPlotSelection(unittest.TestCase):
    def test_plot_selection_uses_expected_run(self):
        plotter = CharacterizationPlots.__new__(CharacterizationPlots)
        filesets = {"532_FW4": object(), "532_FW5": object()}
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5", "532_FW5"]}}):
            key, _ = plotter._select_fileset_for_wavelength(
                sensor_id="3.0",
                filesets=filesets,
                wavelength="532",
            )
        self.assertEqual(key, "532_FW5")

    def test_plot_selection_is_deterministic_without_expected_run(self):
        plotter = CharacterizationPlots.__new__(CharacterizationPlots)
        filesets = {"532_FW5": object(), "532_FW4": object()}
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5"]}}), patch(
            "characterization.elements.plots.characterization_plots.logger.warning"
        ) as mock_warning:
            key, _ = plotter._select_fileset_for_wavelength(
                sensor_id="3.0",
                filesets=filesets,
                wavelength="532",
            )
        self.assertEqual(key, "532_FW4")
        self.assertTrue(mock_warning.called)


if __name__ == "__main__":
    unittest.main()
