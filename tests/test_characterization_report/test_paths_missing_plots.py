from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from characterization_report.helpers.paths import calc_paths
from tests.contract_fixtures import make_valid_extended_payload


class TestPathsMissingPlots(unittest.TestCase):
    def test_calc_paths_allows_missing_plots_in_non_strict_mode(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payload = make_valid_extended_payload(generate_plots=False)
            payload["meta"]["plots_path"] = str(root / "missing_plots")
            fpath = root / "sample_extended.json"
            with fpath.open("w", encoding="utf-8") as f:
                json.dump(payload, f)

            report_paths = calc_paths(str(fpath), output_path=None, strict_plots=False)
            self.assertEqual(report_paths.input_file, str(fpath))
            self.assertEqual(report_paths.char_plots_path, str(root / "missing_plots"))

    def test_calc_paths_raises_when_plots_missing_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payload = make_valid_extended_payload(generate_plots=False)
            payload["meta"]["plots_path"] = str(root / "missing_plots")
            fpath = root / "sample_extended.json"
            with fpath.open("w", encoding="utf-8") as f:
                json.dump(payload, f)

            with self.assertRaises(FileNotFoundError):
                calc_paths(str(fpath), output_path=None, strict_plots=True)


if __name__ == "__main__":
    unittest.main()
