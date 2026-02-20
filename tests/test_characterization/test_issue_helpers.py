from __future__ import annotations

import unittest

from characterization.elements.characterization import Characterization
from characterization.elements.fileset import Fileset
from characterization.elements.photodiode import Photodiode
from characterization.elements.sweep_file import SweepFile


class TestIssueHelpers(unittest.TestCase):
    def test_collect_issues_builds_expected_keys(self):
        c = Characterization.__new__(Characterization)
        c.issues = []
        c.photodiodes = {}

        pdh = Photodiode.__new__(Photodiode)
        pdh.sensor_id = "0.0"
        pdh.issues = []
        pdh.filesets = {}

        fs = Fileset.__new__(Fileset)
        fs.label = "1064_FW5"
        fs.issues = []
        fs.files = []

        sweep = SweepFile.__new__(SweepFile)
        sweep.file_info = {"run": "1"}
        sweep.issues = []

        c.photodiodes["0.0"] = pdh
        pdh.filesets["1064_FW5"] = fs
        fs.files.append(sweep)

        c.add_issue("c-level", "warning", {"a": 1})
        pdh.add_issue("pd-level", "warning", {})
        fs.add_issue("fs-level", "error", {})
        sweep.add_issue("run-level", "error", {})

        out = c._collect_issues()
        self.assertIn("charact", out)
        self.assertIn("PD_0.0", out)
        self.assertIn("PD_0.0_1064_FW5", out)
        self.assertIn("PD_0.0_1064_FW5_1", out)
        self.assertEqual(out["charact"][0]["level"], "warning")

    def test_add_issue_rejects_invalid_level(self):
        c = Characterization.__new__(Characterization)
        c.issues = []
        with self.assertRaises(ValueError):
            c.add_issue("bad", "fatal", {})

    def test_add_issue_warning_and_error_helpers(self):
        c = Characterization.__new__(Characterization)
        c.issues = []
        c.add_issue_warning("warn")
        c.add_issue_error("err")
        self.assertEqual(c.issues[0]["level"], "warning")
        self.assertEqual(c.issues[1]["level"], "error")


if __name__ == "__main__":
    unittest.main()
