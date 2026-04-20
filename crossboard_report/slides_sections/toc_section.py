from __future__ import annotations

from .base_section import BaseSection


class ToCSection(BaseSection):
    def __init__(self, summary_data: dict, report) -> None:
        super().__init__(summary_data, report)
        self.section_depth = 2

    def _build(self, depth: int) -> None:
        self.report.create_table_of_contents_slide(
            title="Table of Contents",
            subtitle="Crossboard report sections",
            num_columns=2,
        )
