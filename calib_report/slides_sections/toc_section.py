"""
Docstring for calib_report.sections.toc_section
"""
from base_report.base_report_slides import BaseReportSlides
from ..helpers.data_holders import ReportData
from .base_section import BaseSection



class ToCSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2  # FileSet section is at depth 2

    def _build(self, depth):
        """Build the fileset section of the report"""
        self.report.create_table_of_contents_slide(
            title="Table of Contents",
            subtitle="Overview of the report sections",
            num_columns=2)
