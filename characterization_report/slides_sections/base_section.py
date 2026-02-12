from __future__ import annotations

from abc import ABC, abstractmethod

from base_report.base_report_slides import BaseReportSlides, Frame


class BaseSection(ABC):
    def __init__(self, report_data: dict, report: BaseReportSlides) -> None:
        self.report_data = report_data
        self.report = report
        self.section_depth = 3

    @property
    def lf(self) -> Frame:
        if self.report.last_frame is None:
            raise ValueError("No frame available yet.")
        return self.report.last_frame

    def build(self, depth: int = 0) -> None:
        if depth == 0 or self.section_depth <= depth:
            self._build(depth)

    @abstractmethod
    def _build(self, depth: int) -> None:
        pass
