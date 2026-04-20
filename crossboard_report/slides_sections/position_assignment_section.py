from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit

from base_report.base_report_slides import TextStyle

from ..helpers import load_final_calification_rows
from .base_section import BaseSection


MISSING_COLOR = colors.HexColor("#B02A37")
INFO_COLOR = colors.HexColor("#5B151A")
SLOT_ORDER = ("R0", "R1", "R2", "L0", "L1", "L2")


def _format_avg_abs_dev(value: str | None) -> str:
    if value is None or value == "":
        return "-"
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


class PositionAssignmentSection(BaseSection):
    def __init__(self, summary_data: dict, report, root_path: str) -> None:
        super().__init__(summary_data, report)
        self.section_depth = 2
        self.root_path = root_path

    def _build(self, depth: int) -> None:
        rows = load_final_calification_rows(self.summary_data, self.root_path)
        if not rows:
            return

        ranked_rows = sorted(rows, key=lambda row: int(row.get("rank", "999999")))
        self.report.add_slide("Crossboard Report", "Board assignment summary")
        self.report.add_section(
            "Board Assignment Summary",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="board_assignment_summary",
            toc=True,
        )
        intro = self.report.add_paragraph(
            "Boards are grouped by suffix and assigned by final calification rank. Lower rank is better. "
            "The first two boards become Best and Second; any additional boards are listed as Spares.",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 10,
            width=self.end_x - self.init_x,
            font_size=10.5,
        )
        table_y = intro.y - intro.height - 12

        self.report.set_table_style(
            header_style=TextStyle("Helvetica-Bold", 10, 12, colors.HexColor("#F2F5F3")),
            body_style=TextStyle("Helvetica", 9.2, 11, self.report.body_text),
        )

        table_data = [["Slot", "Best", "Second", "Spares"]]
        missing_cells: set[tuple[int, int]] = set()
        for row_idx, slot in enumerate(SLOT_ORDER, start=1):
            matches = [row for row in ranked_rows if str(row.get("board_id", "")).endswith(slot)]
            best = self._describe_row(matches[0]) if len(matches) >= 1 else "Missing"
            second = self._describe_row(matches[1]) if len(matches) >= 2 else "Missing"
            spares = self._describe_spares(matches[2:])
            table_data.append([slot, best, second, spares])
            if len(matches) < 1:
                missing_cells.add((row_idx, 1))
            if len(matches) < 2:
                missing_cells.add((row_idx, 2))

        col_widths = [0.75, 2.15, 2.15, 4.2]
        col_align = ["center", "left", "left", "left"]
        table_frame = self.report.add_table(
            table_data,
            x=self.init_x,
            y=table_y,
            width=self.end_x - self.init_x,
            header_rows=1,
            zebra=True,
            col_widths=col_widths,
            col_align=col_align,
        )

        self._overlay_missing_cells(
            data=table_data,
            x=self.init_x,
            y=table_y,
            width=self.end_x - self.init_x,
            col_widths=col_widths,
            missing_cells=missing_cells,
        )
        self.report.reset_table_style()

        footnote_y = table_frame.y - table_frame.height - 10
        self.report.add_paragraph(
            "Missing Best/Second entries are highlighted in red. Spare boards are any remaining boards of the same slot after the first two.",
            x=self.init_x,
            y=footnote_y,
            width=self.end_x - self.init_x,
            font_size=9.5,
            font_color=INFO_COLOR,
        )

    @staticmethod
    def _describe_row(row: dict[str, str]) -> str:
        return (
            f"{row.get('board_id', '')} "
            f"(rank {row.get('rank', '-')}, weighted avg abs dev {_format_avg_abs_dev(row.get('average_abs_dev_pct'))}%)"
        )

    @staticmethod
    def _describe_spares(rows: list[dict[str, str]]) -> str:
        if not rows:
            return "None"
        return "; ".join(PositionAssignmentSection._describe_row(row) for row in rows)

    def _overlay_missing_cells(
        self,
        data: list[list[str]],
        x: float,
        y: float,
        width: float,
        col_widths: list[float],
        missing_cells: set[tuple[int, int]],
    ) -> None:
        total = sum(col_widths)
        scaled_col_widths = [col_w * width / total for col_w in col_widths]
        row_heights = self._compute_row_heights(data=data, scaled_col_widths=scaled_col_widths, header_rows=1)
        for row_idx, col_idx in sorted(missing_cells):
            cell_x = x + sum(scaled_col_widths[:col_idx])
            row_top = y - sum(row_heights[:row_idx])
            row_height = row_heights[row_idx]
            self.report.add_paragraph(
                "Missing",
                x=cell_x + 4,
                y=row_top - 6,
                width=scaled_col_widths[col_idx] - 8,
                font_size=9.2,
                font_color=MISSING_COLOR,
                bold=True,
            )

    def _compute_row_heights(self, data: list[list[str]], scaled_col_widths: list[float], header_rows: int) -> list[float]:
        row_heights: list[float] = []
        for row_idx, row in enumerate(data):
            style = self.report.table_header_style if row_idx < header_rows else self.report.table_style
            max_lines = 1
            for col_idx, cell in enumerate(row):
                lines = simpleSplit(str(cell), style.font_name, style.font_size, scaled_col_widths[col_idx] - 8)
                max_lines = max(max_lines, len(lines))
            row_heights.append(max_lines * style.leading + 6)
        return row_heights
