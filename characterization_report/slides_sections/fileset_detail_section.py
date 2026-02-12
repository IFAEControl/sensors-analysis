from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides

from ..report_elements import add_fileset_detail
from .base_section import BaseSection


class FilesetDetailSection(BaseSection):
    def __init__(self, report_data: dict, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 3

    def _build(self, depth: int) -> None:
        photodiodes = self.report_data.get("analysis", {}).get("photodiodes", {})
        has_filesets = False

        for sensor_id in sorted(photodiodes.keys()):
            filesets = photodiodes[sensor_id].get("filesets", {})
            for fileset_key in sorted(filesets.keys()):
                has_filesets = True
                self.report.add_slide(f"PD {sensor_id} - {fileset_key}", "Fileset Detail")
                frame = self.report.get_active_area()
                add_fileset_detail(
                    report=self.report,
                    report_data=self.report_data,
                    sensor_id=sensor_id,
                    fileset_key=fileset_key,
                    fileset_data=filesets[fileset_key],
                    frame=frame,
                )

        if not has_filesets:
            self.report.add_slide("Fileset Detail", "No filesets found")
            frame = self.report.get_active_area()
            self.report.add_section(
                "Fileset Detail",
                x=frame.x,
                y=frame.y,
                width=frame.width,
                anchor="fileset_detail",
                toc=True,
            )
            self.report.add_badge(
                title="No filesets available",
                description="No fileset entries were found in the input summary.",
                level="Warning",
                x=frame.x,
                y=self.report.last_frame.y - self.report.last_frame.height - 20,
                width=520,
            )
