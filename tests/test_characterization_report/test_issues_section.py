from __future__ import annotations

import unittest

from characterization_report.helpers.data_holders import IssueEntry
from characterization_report.slides_sections.issues_section import _flatten_issues, _scope_group


class TestIssuesSectionHelpers(unittest.TestCase):
    def test_scope_group_mapping(self):
        self.assertEqual(_scope_group("charact"), "charact")
        self.assertEqual(_scope_group("PD_0.0"), "photodiode")
        self.assertEqual(_scope_group("PD_0.0_1064_FW5"), "fileset")
        self.assertEqual(_scope_group("PD_0.0_1064_FW5_run1"), "run")
        self.assertEqual(_scope_group("unexpected_scope"), "other")

    def test_flatten_issues_sorted_by_severity_then_scope(self):
        issues = {
            "PD_0.0_1064_FW5": [IssueEntry(description="fileset warn", level="warning", meta={})],
            "charact": [IssueEntry(description="char error", level="error", meta={})],
            "PD_0.0": [IssueEntry(description="pd warn", level="warning", meta={})],
        }
        items = _flatten_issues(issues)
        self.assertEqual(items[0].severity, "error")
        self.assertEqual(items[0].scope_group, "charact")
        self.assertEqual(items[1].severity, "warning")
        self.assertEqual(items[1].scope_group, "photodiode")
        self.assertEqual(items[2].scope_group, "fileset")


if __name__ == "__main__":
    unittest.main()

