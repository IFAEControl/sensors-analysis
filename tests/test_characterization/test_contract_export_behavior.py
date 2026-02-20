from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch

from characterization.config import config
from characterization.elements.characterization import Characterization
from tests.contract_fixtures import make_valid_extended_payload


class _FakeCharacterization:
    def __init__(self, reports_path: str, strict_contract: bool, payload: dict):
        self.reports_path = reports_path
        self.strict_contract = strict_contract
        self._payload = payload

    def to_dict(self):
        return self._payload


class TestContractExportBehavior(unittest.TestCase):
    def test_export_data_summary_non_strict_warns_and_writes(self):
        invalid_payload = make_valid_extended_payload(generate_plots=True)
        invalid_payload["plots"] = {}
        with tempfile.TemporaryDirectory() as tmpdir:
            fake = _FakeCharacterization(
                reports_path=tmpdir,
                strict_contract=False,
                payload=invalid_payload,
            )
            with patch.object(config, "summary_file_name", "extended.json"):
                with patch("characterization.elements.characterization.logger.warning") as warn_mock:
                    Characterization.export_data_summary(fake)
                self.assertTrue(warn_mock.called)
                self.assertTrue(os.path.exists(os.path.join(tmpdir, "extended.json")))

    def test_export_data_summary_strict_raises(self):
        invalid_payload = make_valid_extended_payload(generate_plots=True)
        invalid_payload["plots"] = {}
        with tempfile.TemporaryDirectory() as tmpdir:
            fake = _FakeCharacterization(
                reports_path=tmpdir,
                strict_contract=True,
                payload=invalid_payload,
            )
            with patch.object(config, "summary_file_name", "extended.json"):
                with self.assertRaises(ValueError):
                    Characterization.export_data_summary(fake)


if __name__ == "__main__":
    unittest.main()
