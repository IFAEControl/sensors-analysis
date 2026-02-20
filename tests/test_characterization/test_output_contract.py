from __future__ import annotations

import unittest

from characterization.helpers.output_contract import (
    validate_characterization_extended_contract,
    validate_characterization_reduced_contract,
)
from tests.contract_fixtures import make_valid_extended_payload, make_valid_reduced_payload


class TestOutputContract(unittest.TestCase):
    def test_valid_extended_contract_passes(self):
        payload = make_valid_extended_payload(generate_plots=True)
        violations = validate_characterization_extended_contract(payload)
        self.assertEqual(violations, [])

    def test_extended_contract_reports_missing_photodiode_filesets(self):
        payload = make_valid_extended_payload(generate_plots=True)
        del payload["analysis"]["photodiodes"]["0.0"]["filesets"]
        violations = validate_characterization_extended_contract(payload)
        self.assertTrue(any("analysis.photodiodes.0.0.filesets" in v for v in violations))

    def test_extended_contract_skips_plot_pd_checks_when_plots_disabled(self):
        payload = make_valid_extended_payload(generate_plots=False)
        payload["plots"] = {}
        violations = validate_characterization_extended_contract(payload)
        self.assertEqual(violations, [])

    def test_extended_contract_reports_missing_sanity_sweepfiles(self):
        payload = make_valid_extended_payload(generate_plots=False)
        del payload["sanity_checks"]["run_1"]["photodiodes"]["0.0"]["filesets"]["1064_FW5"]["sweepfiles"]
        violations = validate_characterization_extended_contract(payload)
        self.assertTrue(any("sweepfiles" in v for v in violations))

    def test_valid_reduced_contract_passes(self):
        payload = make_valid_reduced_payload()
        violations = validate_characterization_reduced_contract(payload)
        self.assertEqual(violations, [])

    def test_reduced_contract_reports_missing_required_key(self):
        payload = make_valid_reduced_payload()
        del payload["photodiodes"]
        violations = validate_characterization_reduced_contract(payload)
        self.assertTrue(any("photodiodes" in v for v in violations))


if __name__ == "__main__":
    unittest.main()
