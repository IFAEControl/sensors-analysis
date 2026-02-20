from __future__ import annotations

import unittest

from characterization.elements.sanity_checks import SanityChecks


class _FakeChar:
    def __init__(self):
        self.error_issues = []
        self.warning_issues = []

    def add_issue_error(self, description: str, meta: dict | None = None):
        self.error_issues.append((description, meta or {}))

    def add_issue_warning(self, description: str, meta: dict | None = None):
        self.warning_issues.append((description, meta or {}))


class TestSanityIssueSummary(unittest.TestCase):
    def test_adds_one_error_and_one_warning_issue_when_present(self):
        san = SanityChecks.__new__(SanityChecks)
        san.char = _FakeChar()
        summary = {
            "total_failed": 3,
            "total_checks": 10,
            "details": {
                "error_failed": 2,
                "warning_failed": 1,
            },
        }

        san._add_summary_issues(summary)

        self.assertEqual(len(san.char.error_issues), 1)
        self.assertEqual(len(san.char.warning_issues), 1)
        self.assertEqual(san.char.error_issues[0][1]["error_failed"], 2)
        self.assertEqual(san.char.warning_issues[0][1]["warning_failed"], 1)

    def test_adds_no_issue_when_no_failures(self):
        san = SanityChecks.__new__(SanityChecks)
        san.char = _FakeChar()
        summary = {
            "total_failed": 0,
            "total_checks": 10,
            "details": {
                "error_failed": 0,
                "warning_failed": 0,
            },
        }

        san._add_summary_issues(summary)

        self.assertEqual(len(san.char.error_issues), 0)
        self.assertEqual(len(san.char.warning_issues), 0)


if __name__ == "__main__":
    unittest.main()
