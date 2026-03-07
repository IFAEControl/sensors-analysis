from __future__ import annotations

import os

from base_report.base_report_slides import BaseReportSlides

from ..helpers.data_holders import ReportData
from .base_section import BaseSection


class MiscelaniaSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2

    def _build(self, depth: int) -> None:
        self.report.add_slide("Miscelania")
        self.report.add_section(
            "Miscelania",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="miscelania",
            toc=True,
        )

        pd_positions_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "media",
                "PD positions and Naming and Indexes.pdf",
            )
        )
        boards_scheme_candidates = [
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "media",
                    "BoardsNaming_boards_scheme.pdf",
                )
            ),
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "media",
                    "BoardsNaming_boardsScheme.pdf",
                )
            ),
        ]
        boards_scheme_path = next((p for p in boards_scheme_candidates if os.path.isfile(p)), None)

        if not os.path.isfile(pd_positions_path):
            self.report.add_paragraph(
                f"Missing media file: {pd_positions_path}",
                x=self.init_x,
                y=self.lf.y - self.lf.height - 12,
                width=self.end_x - self.init_x,
                font_size=10,
            )
            return

        total_width = self.end_x - self.init_x
        plot_width = total_width * 0.5
        x = self.init_x  # Left aligned for future content on the right side.
        y = self.lf.y - self.lf.height - 12
        self.report.add_plot(
            pd_positions_path,
            x=x,
            y=y,
            width=plot_width,
        )

        if boards_scheme_path is None:
            self.report.add_paragraph(
                "Missing media file: characterization_report/media/BoardsNaming_boards_scheme.pdf",
                x=self.init_x,
                y=self.lf.y - self.lf.height - 8,
                width=self.end_x - self.init_x,
                font_size=10,
            )
            return

        second_y = self.lf.y - self.lf.height - 10
        remaining_height = second_y - self.end_y
        if remaining_height <= 10:
            return
        self.report.add_plot(
            boards_scheme_path,
            x=x,
            y=second_y,
            width=plot_width,
            height=remaining_height,
        )
