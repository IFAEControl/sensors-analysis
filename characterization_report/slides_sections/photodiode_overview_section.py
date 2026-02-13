from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides

from ..helpers.data_holders import ReportData
from ..report_elements import add_photodiode_fileset_overview
from .base_section import BaseSection


class PhotodiodeOverviewSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2

    def _build(self, depth: int) -> None:
        photodiodes = self.report_data.analysis.photodiodes
        if not photodiodes:
            self.report.add_slide("Photodiode Overview", "No photodiodes found")
            active_area = self.report.get_active_area()
            self.report.add_section(
                "Photodiode Overview",
                x=active_area.x,
                y=active_area.y,
                width=active_area.width,
                anchor="photodiode_overview",
                toc=True,
            )
            self.report.add_badge(
                title="No photodiodes available",
                description="No photodiode analysis entries were found in the input summary.",
                level="Warning",
                x=active_area.x,
                y=self.report.last_frame.y - self.report.last_frame.height - 20,
                width=520,
            )
            return

        active_area = self.report.get_active_area()
        for sensor_id in sorted(photodiodes.keys()):
            sensor_data = photodiodes[sensor_id]
            filesets_keys = sensor_data.filesets.keys() if sensor_data.filesets else []
            fs_1064 = list(filter(lambda k: k.startswith("1064_"), filesets_keys))[0] if any(k.startswith("1064_") for k in filesets_keys) else None
            fs_532 = list(filter(lambda k: k.startswith("532_"), filesets_keys))[0] if any(k.startswith("532_") for k in filesets_keys) else None
            first_slide = True
            if fs_1064:
                fs = sensor_data.filesets.get(fs_1064)
                
                self.report.add_slide(f"Photodiode {sensor_id}", f"{fs.meta.wavelength}nm - {fs.meta.filter_wheel}")
                add_photodiode_fileset_overview(
                    section=self,
                    sensor_id=sensor_id,
                    fileset_data=fs,
                    fileset_plots=fs.plots,
                    frame=active_area,
                    add_section=first_slide,
                )
                first_slide = False

            if fs_532:
                fs = sensor_data.filesets.get(fs_532)
                self.report.add_slide(f"Photodiode {sensor_id}", f"{fs.meta.wavelength}nm - {fs.meta.filter_wheel}")
                add_photodiode_fileset_overview(
                    section=self,
                    sensor_id=sensor_id,
                    fileset_data=fs,
                    fileset_plots=fs.plots,
                    frame=active_area,
                    add_section=first_slide,
                )
                first_slide = False
