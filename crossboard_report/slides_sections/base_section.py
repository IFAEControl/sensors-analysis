from __future__ import annotations

from abc import ABC, abstractmethod

from base_report.base_report_slides import BaseReportSlides, Frame
from ..helpers import resolve_plot_path


class BaseSection(ABC):
    def __init__(self, summary_data: dict, report: BaseReportSlides) -> None:
        self.summary_data = summary_data
        self.report = report
        self.section_depth = 3
        self.init_x = 18
        self.end_x = 942
        self.init_y = 478
        self.end_y = 18

    @property
    def lf(self) -> Frame:
        if self.report.last_frame is None:
            raise ValueError("No frame available yet.")
        return self.report.last_frame

    def build(self, depth: int = 0) -> None:
        if depth == 0 or self.section_depth <= depth:
            self._build(depth)

    def add_plot_from_summary(
        self,
        plot_key: str,
        root_path: str,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
    ) -> Frame:
        plot_path = resolve_plot_path(self.summary_data, root_path, plot_key)
        return self.report.add_plot(
            plot_path,
            x=x,
            y=y,
            width=width,
            height=height,
        )

    @abstractmethod
    def _build(self, depth: int) -> None:
        pass
