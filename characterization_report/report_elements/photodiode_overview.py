from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides, Frame
from ..helpers.data_holders import Photodiode, ReportData, Fileset, FilesetPlots
from ..helpers.paths import calc_plot_path

def add_photodiode_fileset_overview(
    report: BaseReportSlides,
    sensor_id: str,
    fileset_data: Fileset,
    fileset_plots: FilesetPlots,
    frame: Frame,
    add_section: bool = True,
) -> None:
    if add_section:
        report.add_section(
            f"Photodiode {sensor_id}",
            x=frame.x,
            y=frame.y,
            width=frame.width,
            anchor=f"photodiode_{sensor_id}",
            toc=True,
        )
        subsection_y = report.last_frame.y - report.last_frame.height - 8
    else:
        subsection_y = frame.y

    report.add_subsection(
        f"{fileset_data.meta.wavelength}nm - {fileset_data.meta.filter_wheel}",
        x=frame.x,
        y=subsection_y,
        width=frame.width,
        anchor=f"photodiode_{sensor_id}_{fileset_data.meta.wavelength}",
        toc=True,
    )

    report.add_plot(
        path=calc_plot_path(fileset_plots.refpd_vs_dut),
        x=frame.x,
        y=report.last_frame.y - report.last_frame.height - 12,
        width=510
    )
    top_y = report.last_frame.y - report.last_frame.height - 12
    report.add_plot(
        path=calc_plot_path(fileset_plots.saturation_points_vs_run),
        x=frame.x,
        y=top_y,
        width=510,
        height=top_y-10
    )

