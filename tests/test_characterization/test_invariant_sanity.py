from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from characterization.config import config
from characterization.elements.sanity.characterization import CharacterizationSanityChecker
from characterization.elements.sanity_checks import SanityChecks


def _mk_char(photodiodes: dict, strict_contract: bool = False):
    return SimpleNamespace(photodiodes=photodiodes, level_header="char_run", strict_contract=strict_contract)


def _mk_fs(has_lr: bool = True, has_power: bool = True):
    lr = SimpleNamespace(
        linreg=object() if has_lr else None,
        slope=1.0 if has_lr else None,
        intercept=0.1 if has_lr else None,
    )
    adc_to_power = {"slope": 2.0, "intercept": 0.2} if has_power else {}
    return SimpleNamespace(anal=SimpleNamespace(lr_refpd_vs_adc=lr, adc_to_power=adc_to_power))


def _mk_pd(fileset_keys: list[str], incomplete_by_key: dict[str, tuple[bool, bool]] | None = None):
    incomplete_by_key = incomplete_by_key or {}
    filesets = {}
    for key in fileset_keys:
        has_lr, has_power = incomplete_by_key.get(key, (True, True))
        filesets[key] = _mk_fs(has_lr=has_lr, has_power=has_power)
    return SimpleNamespace(filesets=filesets)


class TestInvariantSanityChecks(unittest.TestCase):
    def test_invariant_checks_pass_for_expected_layout(self):
        char = _mk_char(
            {
                "0.0": _mk_pd(["1064_FW5", "532_FW4"]),
                "3.0": _mk_pd(["1064_FW5", "532_FW5"]),
            }
        )
        with patch.object(
            config,
            "sensor_config",
            {
                "0.0": {"valid_setups": ["1064_FW5", "532_FW4"]},
                "3.0": {"valid_setups": ["1064_FW5", "532_FW5"]},
            },
        ):
            checker = CharacterizationSanityChecker(char)
            self.assertTrue(checker.san_check_pd_single_1064_fw5().passed)
            self.assertTrue(checker.san_check_pd_single_532_fileset().passed)
            self.assertTrue(checker.san_check_pd_532_matches_expected_mapping().passed)
            self.assertTrue(checker.san_check_pd_has_slope_intercept_for_all_wavelengths().passed)

    def test_invariant_checks_fail_for_invalid_layout(self):
        char = _mk_char(
            {
                "0.0": _mk_pd(["1064_FW4", "532_FW4", "532_FW5"]),
            }
        )
        with patch.object(
            config,
            "sensor_config",
            {
                "0.0": {"valid_setups": ["1064_FW5", "532_FW4"]},
            },
        ):
            checker = CharacterizationSanityChecker(char)
            r1 = checker.san_check_pd_single_1064_fw5()
            r2 = checker.san_check_pd_single_532_fileset()
            r3 = checker.san_check_pd_532_matches_expected_mapping()
            self.assertFalse(r1.passed)
            self.assertFalse(r2.passed)
            self.assertFalse(r3.passed)
            self.assertIn("0.0", r1.check_args)
            self.assertIn("0.0", r2.check_args)
            self.assertIn("0.0", r3.check_args)

    def test_invariant_check_fails_when_fit_params_missing_for_expected_wavelength(self):
        char = _mk_char(
            {
                "0.0": _mk_pd(
                    ["1064_FW5", "532_FW4"],
                    incomplete_by_key={"532_FW4": (True, False)},
                ),
            }
        )
        with patch.object(
            config,
            "sensor_config",
            {
                "0.0": {"valid_setups": ["1064_FW5", "532_FW4"]},
            },
        ):
            checker = CharacterizationSanityChecker(char)
            result = checker.san_check_pd_has_slope_intercept_for_all_wavelengths()
            self.assertFalse(result.passed)
            self.assertIn("0.0", result.check_args)
            self.assertIn("532", result.check_args["0.0"])

    def test_strict_mode_raises_on_failed_invariant_checks(self):
        san = SanityChecks.__new__(SanityChecks)
        san.char = _mk_char({}, strict_contract=True)
        san.results = {
            "char_run": {
                "checks": {
                    "error.pd_single_1064_fw5": {"check_name": "pd_single_1064_fw5", "passed": False},
                    "error.pd_has_slope_intercept_for_all_wavelengths": {
                        "check_name": "pd_has_slope_intercept_for_all_wavelengths",
                        "passed": False,
                    },
                    "error.max_temperature_change": {"check_name": "max_temperature_change", "passed": False},
                }
            }
        }
        with self.assertRaises(ValueError):
            san._raise_if_strict_invariant_failures()

    def test_slope_deviation_threshold_check_warns_or_errors_by_threshold(self):
        char = _mk_char(
            {
                "0.0": SimpleNamespace(filesets={"1064_FW5": _mk_fs(has_lr=True, has_power=True)}),
                "0.1": SimpleNamespace(filesets={"1064_FW5": _mk_fs(has_lr=True, has_power=True)}),
                "0.2": SimpleNamespace(filesets={"1064_FW5": _mk_fs(has_lr=True, has_power=True)}),
            }
        )
        char.photodiodes["0.0"].filesets["1064_FW5"].anal.lr_refpd_vs_adc.slope = 1.00
        char.photodiodes["0.1"].filesets["1064_FW5"].anal.lr_refpd_vs_adc.slope = 1.00
        char.photodiodes["0.2"].filesets["1064_FW5"].anal.lr_refpd_vs_adc.slope = 1.03

        with patch.object(
            config,
            "sensor_config",
            {
                "0.0": {"gain": "G1"},
                "0.1": {"gain": "G1"},
                "0.2": {"gain": "G1"},
            },
        ):
            checker = CharacterizationSanityChecker(char)
            warn_result = checker.san_check_pd_slope_deviation_from_group_median_pct(2.0, severity="warning")
            err_result = checker.san_check_pd_slope_deviation_from_group_median_pct(5.0, severity="error")
            self.assertFalse(warn_result.passed)
            self.assertTrue(err_result.passed)


if __name__ == "__main__":
    unittest.main()
