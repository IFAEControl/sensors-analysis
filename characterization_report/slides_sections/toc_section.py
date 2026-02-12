from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides

from .base_section import BaseSection


class ToCSection(BaseSection):
    def __init__(self, report_data: dict, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2

    def _build(self, depth: int) -> None:
        self.report.create_table_of_contents_slide(
            title="Table of Contents",
            subtitle="Overview of report sections",
            num_columns=2,
        )
