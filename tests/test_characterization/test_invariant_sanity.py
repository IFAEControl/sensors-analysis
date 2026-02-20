from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from characterization.config import config
from characterization.elements.sanity.characterization import CharacterizationSanityChecker
from characterization.elements.sanity_checks import SanityChecks


def _mk_char(photodiodes: dict, strict_contract: bool = False):
    return SimpleNamespace(photodiodes=photodiodes, level_header="char_run", strict_contract=strict_contract)


def _mk_pd(fileset_keys: list[str]):
    return SimpleNamespace(filesets={k: object() for k in fileset_keys})


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

    def test_strict_mode_raises_on_failed_invariant_checks(self):
        san = SanityChecks.__new__(SanityChecks)
        san.char = _mk_char({}, strict_contract=True)
        san.results = {
            "char_run": {
                "checks": {
                    "error.pd_single_1064_fw5": {"check_name": "pd_single_1064_fw5", "passed": False},
                    "error.max_temperature_change": {"check_name": "max_temperature_change", "passed": False},
                }
            }
        }
        with self.assertRaises(ValueError):
            san._raise_if_strict_invariant_failures()


if __name__ == "__main__":
    unittest.main()
