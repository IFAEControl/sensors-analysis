from __future__ import annotations

import json
import os

from base_report.base_report_slides import BaseReportSlides

from ..helpers.paths import ReportPaths
from .characterization_overview_section import CharacterizationOverviewSection
from .fileset_detail_section import FilesetDetailSection
from .photodiode_overview_section import PhotodiodeOverviewSection
from .toc_section import ToCSection


class FullReport:
    def __init__(self, report_paths: ReportPaths) -> None:
        self.report_paths = report_paths
        self._data: dict | None = None
        self.sections = []

        self.load_data()
        charact_id = self.data.get("meta", {}).get("charact_id", "characterization")
        self.report_paths.report_path = os.path.join(
            self.report_paths.output_path,
            f"{charact_id}_report.pdf",
        )

        self.report = BaseReportSlides(
            output_path=self.report_paths.report_path,
            logo_path=self.report_paths.logo_path,
            title="Characterization Report",
            subtitle="Generated Characterization Analysis Report",
            serial_number=charact_id,
        )

    @property
    def data(self) -> dict:
        if self._data is None:
            raise ValueError("Report data not loaded yet.")
        return self._data

    def load_data(self) -> None:
        with open(self.report_paths.input_file, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    def load_sections(self) -> None:
        self.sections.append(CharacterizationOverviewSection(self.data, self.report))
        self.sections.append(ToCSection(self.data, self.report))
        self.sections.append(PhotodiodeOverviewSection(self.data, self.report))
        self.sections.append(FilesetDetailSection(self.data, self.report))

    def build(self, depth: int = 0) -> None:
        self.load_sections()
        for section in self.sections:
            section.build(depth)
        self.report.build()
