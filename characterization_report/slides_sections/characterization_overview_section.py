from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides

from ..report_elements import add_characterization_overview
from .base_section import BaseSection


class CharacterizationOverviewSection(BaseSection):
    def __init__(self, report_data: dict, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 1

    def _build(self, depth: int) -> None:
        self.report.add_slide()
        frame = self.report.get_active_area()
        add_characterization_overview(self.report, self.report_data, frame)
