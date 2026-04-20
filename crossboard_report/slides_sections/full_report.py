from __future__ import annotations

import os

from base_report.base_report_slides import BaseReportSlides

from ..helpers import ReportPaths, load_summary
from .final_calification_section import FinalCalificationSection
from .metadata_section import MetadataSection
from .plots_section import PlotsSection
from .position_assignment_section import PositionAssignmentSection


class FullReport:
    def __init__(self, report_paths: ReportPaths) -> None:
        self.report_paths = report_paths
        self.summary_data = load_summary(report_paths.input_file)
        self.sections = []

        serial_number = self._resolve_serial_number()
        self.report_paths.report_path = os.path.join(
            self.report_paths.output_path,
            f"{serial_number}_crossboard_report.pdf",
        )

        self.report = BaseReportSlides(
            output_path=self.report_paths.report_path,
            logo_path=self.report_paths.logo_path,
            title="Crossboard Report",
            subtitle="Generated board ranking summary",
            serial_number=serial_number,
        )

    def load_sections(self) -> None:
        self.sections.append(FinalCalificationSection(self.summary_data, self.report, self.report_paths.root_path))
        self.sections.append(PositionAssignmentSection(self.summary_data, self.report, self.report_paths.root_path))
        self.sections.append(PlotsSection(self.summary_data, self.report, self.report_paths.root_path))
        self.sections.append(MetadataSection(self.summary_data, self.report, self.report_paths))

    def build(self, depth: int = 0) -> None:
        self.load_sections()
        for section in self.sections:
            section.build(depth)
        self.report.build()

    def _resolve_serial_number(self) -> str:
        meta = self.summary_data.get("meta", {}) or {}
        output_path = meta.get("output_path")
        if isinstance(output_path, str) and output_path.strip():
            return os.path.basename(output_path.rstrip(os.sep)) or "crossboard"
        return "crossboard"
