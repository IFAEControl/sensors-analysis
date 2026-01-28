
from .data_holders import ReportData
from base_report.base_report import BaseReport


class SummarySection:
    def __init__(self, report_data: ReportData, report: BaseReport, depth: int = 0) -> None:
        self.report_data = report_data
        self.report = report
        self.depth = depth

    def build(self):
        """Build the summary section of the report"""
        self.report.add_section('Calibration Summary', 'summary')
        # Further summary section building logic goes here
        
    def add_failed_sanity_checks(self):
        """Add a subsection for failed sanity checks"""
        failed_checks = {}
        for section, checks in self.report_data.sanity_checks:
        self.report.add_subsection('Failed Sanity Checks', 'failed_sanity_checks')
        for check in failed_checks:
            self.report.add_paragraph(check)
