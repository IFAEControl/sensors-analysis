from __future__ import annotations

from ..helpers import load_excluded_board_rows
from .base_section import BaseSection


def _format_value(value: str | None) -> str:
    if value is None or value == "":
        return "-"
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


class ExcludedBoardsSection(BaseSection):
    def __init__(self, summary_data: dict, report, root_path: str) -> None:
        super().__init__(summary_data, report)
        self.section_depth = 2
        self.root_path = root_path

    def _build(self, depth: int) -> None:
        rows = load_excluded_board_rows(self.summary_data, self.root_path)
        if not rows:
            return

        threshold = rows[0].get("exclusion_threshold_abs_dev_pct", "10")
        self.report.add_slide("Crossboard Report", "Excluded boards")
        self.report.add_section(
            "Excluded Boards",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="excluded_boards",
            toc=True,
        )
        intro = self.report.add_paragraph(
            f"Boards with any A2P percentage difference above {threshold}% are excluded from the final rank and assignment summary.",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 10,
            width=self.end_x - self.init_x,
            font_size=10.5,
        )

        table_data = [["Board ID", "Status", "Max abs dev %", "Excluded combos"]]
        for row in rows:
            table_data.append(
                [
                    str(row.get("board_id", "")),
                    str(row.get("status", "")),
                    _format_value(row.get("max_abs_dev_pct")),
                    str(row.get("excluded_combos", "")),
                ]
            )

        self.report.add_table(
            table_data,
            x=self.init_x,
            y=intro.y - intro.height - 12,
            width=self.end_x - self.init_x,
            header_rows=1,
            zebra=True,
            col_widths=[1.2, 1.0, 1.3, 6.0],
            col_align=["center", "center", "right", "left"],
        )
