from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides, Frame


def add_photodiode_overview(
    report: BaseReportSlides,
    report_data: dict,
    sensor_id: str,
    photodiode_data: dict,
    frame: Frame,
) -> None:
    report.add_section(
        f"Photodiode {sensor_id} Overview",
        x=frame.x,
        y=frame.y,
        width=frame.width,
        anchor=f"photodiode_{sensor_id}_overview",
        toc=True,
    )
    report.add_badge(
        title="Pending implementation",
        description=(
            "This slide is intentionally left as a placeholder. "
            f"Add overview metrics and plots for photodiode {sensor_id}."
        ),
        level="Info",
        x=frame.x,
        y=report.last_frame.y - report.last_frame.height - 20,
        width=520,
    )
