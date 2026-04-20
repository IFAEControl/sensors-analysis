from __future__ import annotations

from .base_section import BaseSection


class MetadataSection(BaseSection):
    def __init__(self, summary_data: dict, report, report_paths) -> None:
        super().__init__(summary_data, report)
        self.section_depth = 2
        self.report_paths = report_paths

    def _build(self, depth: int) -> None:
        meta = self.summary_data.get("meta", {}) or {}
        dataframe = self.summary_data.get("dataframe", {}) or {}
        analysis = self.summary_data.get("analysis", {}) or {}
        final_cal = analysis.get("a2p_board_final_calification", {}) or {}

        lines = [
            f"Report generation date: {meta.get('execution_date', 'N/A')}",
            f"Crossboard input path: {meta.get('input_path', 'N/A')}",
            f"Crossboard source type: {meta.get('source', 'N/A')}",
            f"Crossboard output path: {meta.get('output_path', 'N/A')}",
            f"Report input summary: {self.report_paths.input_file}",
            f"Report output PDF: {self.report_paths.report_path}",
            f"Report output directory: {self.report_paths.output_path}",
            f"Boards loaded: {dataframe.get('boards_loaded', 'N/A')}",
            f"Crossboard dataframe rows: {dataframe.get('rows', 'N/A')}",
            f"Crossboard dataframe CSV: {dataframe.get('csv_path', 'N/A')}",
            f"Final calification CSV: {final_cal.get('ranking_csv', 'N/A')}",
            f"Final calification JSON: {final_cal.get('ranking_json', 'N/A')}",
        ]

        self.report.add_slide("Crossboard Report", "Metadata")
        self.report.add_section(
            "Metadata",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="metadata",
            toc=False,
        )

        current_y = self.lf.y - self.lf.height - 10
        for line in lines:
            frame = self.report.add_paragraph(
                line,
                x=self.init_x,
                y=current_y,
                width=self.end_x - self.init_x,
                font_size=10.5,
            )
            current_y = frame.y - frame.height - 5
