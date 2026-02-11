
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
        if not self._has_failed_checks(depth):
            return
        self.report.add_page()
        self.report.add_section('Sanity Checks', 'sanity_checks')
        # Further sanity checks section building logic goes here
        self.add_sanity_checks(depth)

    def _has_failed_checks(self, depth: int) -> bool:
        if any(check.passed is False for check in self.report_data.sanity_checks.calibration_checks.values()):
            return True
        if depth == 0 or depth >= 2:
            for fs_checks in self.report_data.sanity_checks.fileset_checks.values():
                if any(check.passed is False for check in fs_checks.values()):
                    return True
        if depth == 0 or depth >= 3:
            for file_checks in self.report_data.sanity_checks.file_checks.values():
                if any(check.passed is False for check in file_checks.values()):
                    return True
        return False
        
    def add_sanity_checks(self, depth: int):
        """Add a subsection for sanity checks"""
        calib_failed = [
            check for check in self.report_data.sanity_checks.calibration_checks.values()
            if check.passed is False
        ]
        if calib_failed:
            self.report.add_subsection("Calibration Level Failed Sanity Checks", 'calib_level_sanity_checks')
            for check in calib_failed:
                add_sanity_check_box(self.report, check)

        if depth == 0 or depth >=2:
            fileset_failed = {
                fs_name: [check for check in fs_checks.values() if check.passed is False]
                for fs_name, fs_checks in self.report_data.sanity_checks.fileset_checks.items()
            }
            fileset_failed = {fs_name: checks for fs_name, checks in fileset_failed.items() if checks}
            if fileset_failed:
                self.report.add_subsection("FileSet Level Failed Sanity Checks", 'fileset_level_sanity_checks')
                for fs_name, failed_checks in fileset_failed.items():
                    self.report.add_subsubsection(f"FileSet {fs_name}", include_in_toc=False)
                    for check in failed_checks:
                        add_sanity_check_box(self.report, check)
        
        if depth == 0 or depth >=3:
            file_failed = {
                file_name: [check for check in file_checks.values() if check.passed is False]
                for file_name, file_checks in self.report_data.sanity_checks.file_checks.items()
            }
            file_failed = {file_name: checks for file_name, checks in file_failed.items() if checks}
            if file_failed:
                self.report.add_subsection("File Level Failed Sanity Checks", 'file_level_sanity_checks')
                for file_name, failed_checks in file_failed.items():
                    self.report.add_subsubsection(f"File {file_name}", include_in_toc=False)
                    for check in failed_checks:
                        add_sanity_check_box(self.report, check)

