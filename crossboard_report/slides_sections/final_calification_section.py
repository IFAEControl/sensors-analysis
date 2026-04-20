from __future__ import annotations

from reportlab.lib import colors

from base_report.base_report_slides import TextStyle

from ..helpers import load_final_calification_rows
from .base_section import BaseSection


def _format_value(value: str | None) -> str:
    if value is None or value == "":
        return "-"
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


class FinalCalificationSection(BaseSection):
    def __init__(self, summary_data: dict, report, root_path: str) -> None:
        super().__init__(summary_data, report)
        self.section_depth = 2
        self.root_path = root_path

    def _build(self, depth: int) -> None:
        rows = load_final_calification_rows(self.summary_data, self.root_path)
        if not rows:
            return

        combo_columns = [key for key in rows[0].keys() if key.startswith("abs_dev_pct_")]
        combo_columns = sorted(combo_columns, key=self._combo_column_sort_key)

        intro_lines = [
            "Final board calification ranks boards by a weighted mean absolute deviation percentage across all wavelength and gain combinations.",
            "The weighting is 70% for 1064 and 30% for 532, split evenly across gains within each wavelength.",
            "Lower average absolute deviation means the board is closer to the crossboard median behavior.",
        ]

        self.report.add_slide("Crossboard Report", "Board final calification")
        self.report.add_section(
            "Board Final Calification",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="board_final_calification",
            toc=True,
        )
        text_y = self.lf.y - self.lf.height - 10
        for line in intro_lines:
            frame = self.report.add_paragraph(
                line,
                x=self.init_x,
                y=text_y,
                width=self.end_x - self.init_x,
                font_size=10.5,
            )
            text_y = frame.y - frame.height - 4

        table_data = [[
            "Rank",
            "Board ID",
            "Avg abs dev %",
            *[self._display_combo_name(col) for col in combo_columns],
        ]]
        for row in rows:
            table_data.append(
                [
                    str(row.get("rank", "")),
                    str(row.get("board_id", "")),
                    _format_value(row.get("average_abs_dev_pct")),
                    *[_format_value(row.get(col)) for col in combo_columns],
                ]
            )

        col_widths = [0.7, 1.0, 1.35] + [1.12] * len(combo_columns)
        col_align = ["center", "center", "right"] + ["right"] * len(combo_columns)
        title_gap = 8
        available_y = text_y - title_gap
        table_width = self.end_x - self.init_x

        self.report.set_table_style(
            header_style=TextStyle("Helvetica-Bold", 8.2, 10, colors.HexColor("#F2F5F3")),
            body_style=TextStyle("Helvetica", 8.0, 9.6, self.report.body_text),
        )

        start_idx = 1
        chunk_idx = 0
        while start_idx < len(table_data):
            if chunk_idx > 0:
                self.report.add_slide("Crossboard Report", f"Board final calification (cont. {chunk_idx})")
                cont_title = self.report.add_section(
                    "Board Final Calification",
                    x=self.init_x,
                    y=self.init_y,
                    width=self.end_x - self.init_x,
                    toc=False,
                )
                available_y = cont_title.y - cont_title.height - 10

            chunk_rows = [table_data[0]]
            cursor = start_idx
            while cursor < len(table_data):
                candidate = chunk_rows + [table_data[cursor]]
                frame = self.report.get_table_frame(
                    candidate,
                    x=self.init_x,
                    y=available_y,
                    width=table_width,
                    header_rows=1,
                    zebra=True,
                    col_widths=col_widths,
                    col_align=col_align,
                )
                if frame.height > (available_y - self.end_y) and len(chunk_rows) > 1:
                    break
                if frame.height > (available_y - self.end_y) and len(chunk_rows) == 1:
                    chunk_rows.append(table_data[cursor])
                    cursor += 1
                    break
                chunk_rows.append(table_data[cursor])
                cursor += 1

            self.report.add_table(
                chunk_rows,
                x=self.init_x,
                y=available_y,
                width=table_width,
                header_rows=1,
                zebra=True,
                col_widths=col_widths,
                col_align=col_align,
            )
            start_idx = cursor
            chunk_idx += 1

        self.report.reset_table_style()

    @staticmethod
    def _display_combo_name(column_name: str) -> str:
        return column_name.replace("abs_dev_pct_", "").replace("_", " ")

    @staticmethod
    def _combo_column_sort_key(column_name: str):
        combo = column_name.replace("abs_dev_pct_", "", 1)
        wavelength, _, gain = combo.partition("_")
        try:
            return (0, float(wavelength), gain)
        except ValueError:
            return (1, wavelength, gain)
