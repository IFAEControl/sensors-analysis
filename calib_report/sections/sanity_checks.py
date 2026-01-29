
from ..helpers.data_holders import ReportData
from base_report.base_report import BaseReport
from ..report_elements.sanity_checks import add_sanity_check_box
from .base_section import BaseSection


class SanityChecksSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReport) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2

    def _build(self, depth: int):
        """Build the sanity checks section of the report"""
        self.report.add_page()
        self.report.add_section('Sanity Checks', 'sanity_checks')
        # Further sanity checks section building logic goes here
        self.add_sanity_checks(depth)
        
    def add_sanity_checks(self, depth: int):
        """Add a subsection for sanity checks"""
        self.report.add_subsection("Calibration Level Sanity Checks")
        for name, check in self.report_data.sanity_checks.calibration_checks.items():
            add_sanity_check_box(self.report, check)
        if depth == 0 or depth >=2:
            self.report.add_subsection(f"FileSet Level Sanity Checks")
            for fs_name, fs_checks in self.report_data.sanity_checks.fileset_checks.items():
                self.report.add_subsubsection(f"FileSet {fs_name}")
                for name, check in fs_checks.items():
                    add_sanity_check_box(self.report, check)
        
        if depth == 0 or depth >=3:
            self.report.add_subsection(f"File Level Sanity Checks")
            for file_name, file_checks in self.report_data.sanity_checks.file_checks.items():
                self.report.add_subsubsection(f"File {file_name}")
                for name, check in file_checks.items():
                    add_sanity_check_box(self.report, check)

