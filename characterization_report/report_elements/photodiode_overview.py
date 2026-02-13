from __future__ import annotations
from typing import TYPE_CHECKING
from base_report.base_report_slides import Frame
from ..helpers.data_holders import Fileset, FilesetPlots
from ..helpers.paths import calc_plot_path
if TYPE_CHECKING:
    from characterization_report.slides_sections.base_section import BaseSection

def _fmt_linreg_value(value: object, precision: int = 3) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{precision}e}"
    return str(value)


def _fmt_r_value(value: object) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.6f}"
    return str(value)

def add_photodiode_fileset_overview(
    section: BaseSection,
    sensor_id: str,
    fileset_data: Fileset,
    fileset_plots: FilesetPlots,
    frame: Frame,
    add_section: bool = True,
) -> None:
    if add_section:
        section.report.add_section(
            f"Photodiode {sensor_id}",
            x=frame.x,
            y=frame.y,
            width=frame.width,
            anchor=f"photodiode_{sensor_id}",
            toc=True,
        )
        subsection_y = section.lf.y - section.lf.height - 8
    else:
        subsection_y = frame.y

    col_1_x = frame.x
    col_1_width = 480
    gap = 10

    section.report.add_subsection(
        f"{fileset_data.meta.wavelength}nm - {fileset_data.meta.filter_wheel}",
        x=frame.x,
        y=subsection_y,
        width=frame.width,
        anchor=f"photodiode_{sensor_id}_{fileset_data.meta.wavelength}",
        toc=False,
    )

    section.report.add_plot(
        path=calc_plot_path(fileset_plots.refpd_vs_dut),
        x=col_1_x,
        y=section.lf.y - section.lf.height - 12,
        width=col_1_width
    )
    top_y = section.lf.y - section.lf.height - 12
    section.report.add_plot(
        path=calc_plot_path(fileset_plots.fit_slopes_intercepts_vs_run_horiz),
        x=col_1_x,
        y=top_y,
        width=col_1_width,
        height=top_y-10
    )


    linreg = fileset_data.analysis.linreg_refpd_vs_adc if fileset_data.analysis else None
    table_rows = [[
        "Slope (V/#adc)",
        "Slope_err (V/#adc)",
        "Intercept (V)",
        "Intercept_err (V)",
        "R",
        "P",
    ], [
        _fmt_linreg_value(getattr(linreg, "slope", None)),
        _fmt_linreg_value(getattr(linreg, "stderr", None)),
        _fmt_linreg_value(getattr(linreg, "intercept", None)),
        _fmt_linreg_value(getattr(linreg, "intercept_stderr", None)),
        _fmt_r_value(getattr(linreg, "r_value", None)),
        _fmt_linreg_value(getattr(linreg, "p_value", None)),
    ]]

    col_2_x = col_1_x + col_1_width + gap
    col_2_width = section.end_x - col_2_x - gap
    
    section.report.add_table(
        data=table_rows,
        x=col_2_x,
        y=section.init_y,
        width=col_2_width,
        zebra=True,
        col_align=["center", "center", "center", "center", "center", "center"],
    )

    section.report.add_plot(
        path=calc_plot_path(fileset_plots.timeseries),
        x=col_2_x,
        y=section.lf.y - section.lf.height - 12,
        width=col_2_width,
    )