from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides, Frame
from ..helpers.data_holders import Fileset, ReportData


def add_fileset_detail(
    report: BaseReportSlides,
    report_data: ReportData,
    sensor_id: str,
    fileset_key: str,
    fileset_data: Fileset,
    frame: Frame,
) -> None:
    report.add_section(
        f"Fileset {fileset_key}",
        x=frame.x,
        y=frame.y,
        width=frame.width,
        anchor=f"photodiode_{sensor_id}_fileset_{fileset_key}",
        toc=True,
    )
    report.add_badge(
        title="Pending implementation",
        description=(
            "This slide is intentionally left as a placeholder. "
            f"Add detailed content for PD {sensor_id}, fileset {fileset_key}."
        ),
        level="Info",
        x=frame.x,
        y=report.last_frame.y - report.last_frame.height - 20,
        width=560,
    )
