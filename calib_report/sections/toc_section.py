"""
Docstring for calib_report.sections.toc_section
"""
from base_report.base_report import BaseReport
from ..helpers.data_holders import ReportData
from .base_section import BaseSection



class ToCSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReport) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2  # FileSet section is at depth 2

    def _build(self, depth):
        """Build the fileset section of the report"""
        self.report.add_page()
        self.report.add_section('Table of Contents', 'table_of_contents')
        self.report.add_table_of_contents(page_break=False)
