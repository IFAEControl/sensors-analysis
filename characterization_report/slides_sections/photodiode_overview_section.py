from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides

from ..report_elements import add_photodiode_overview
from .base_section import BaseSection


class PhotodiodeOverviewSection(BaseSection):
    def __init__(self, report_data: dict, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2

    def _build(self, depth: int) -> None:
        photodiodes = self.report_data.get("analysis", {}).get("photodiodes", {})
        if not photodiodes:
            self.report.add_slide("Photodiode Overview", "No photodiodes found")
            frame = self.report.get_active_area()
            self.report.add_section(
                "Photodiode Overview",
                x=frame.x,
                y=frame.y,
                width=frame.width,
                anchor="photodiode_overview",
                toc=True,
            )
            self.report.add_badge(
                title="No photodiodes available",
                description="No photodiode analysis entries were found in the input summary.",
                level="Warning",
                x=frame.x,
                y=self.report.last_frame.y - self.report.last_frame.height - 20,
                width=520,
            )
            return

        for sensor_id in sorted(photodiodes.keys()):
            self.report.add_slide(f"Photodiode {sensor_id}", "Overview")
            frame = self.report.get_active_area()
            add_photodiode_overview(
                report=self.report,
                report_data=self.report_data,
                sensor_id=sensor_id,
                photodiode_data=photodiodes[sensor_id],
                frame=frame,
            )
