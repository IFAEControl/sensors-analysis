from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from characterization.config import config
from characterization_report.report_elements.characterization_overview import (
    _extract_power_for_sensor,
    _extract_refpd_for_sensor,
)


class TestFilesetSelectionConsistency(unittest.TestCase):
    def _mk_photodiode(self, expected_532: str):
        fw4 = SimpleNamespace(
            analysis=SimpleNamespace(
                linreg_refpd_vs_adc=SimpleNamespace(slope=1.0),
                adc_to_power=SimpleNamespace(slope=10.0),
            )
        )
        fw5 = SimpleNamespace(
            analysis=SimpleNamespace(
                linreg_refpd_vs_adc=SimpleNamespace(slope=2.0),
                adc_to_power=SimpleNamespace(slope=20.0),
            )
        )
        return SimpleNamespace(
            meta=SimpleNamespace(sensor_id="3.0", valid_setups=["1064_FW5", expected_532]),
            filesets={
                "1064_FW5": SimpleNamespace(
                    analysis=SimpleNamespace(
                        linreg_refpd_vs_adc=SimpleNamespace(slope=100.0),
                        adc_to_power=SimpleNamespace(slope=200.0),
                    )
                ),
                "532_FW4": fw4,
                "532_FW5": fw5,
            },
        )

    def test_overview_extractors_use_same_expected_selected_fileset_fw5(self):
        pd = self._mk_photodiode(expected_532="532_FW5")
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5", "532_FW5"]}}):
            ref_fit = _extract_refpd_for_sensor(pd, wavelength="532")
            power_fit = _extract_power_for_sensor(pd, wavelength="532")
        self.assertEqual(ref_fit.slope, 2.0)
        self.assertEqual(power_fit.slope, 20.0)

    def test_overview_extractors_use_same_expected_selected_fileset_fw4(self):
        pd = self._mk_photodiode(expected_532="532_FW4")
        with patch.object(config, "sensor_config", {"3.0": {"valid_setups": ["1064_FW5", "532_FW4"]}}):
            ref_fit = _extract_refpd_for_sensor(pd, wavelength="532")
            power_fit = _extract_power_for_sensor(pd, wavelength="532")
        self.assertEqual(ref_fit.slope, 1.0)
        self.assertEqual(power_fit.slope, 10.0)


if __name__ == "__main__":
    unittest.main()
