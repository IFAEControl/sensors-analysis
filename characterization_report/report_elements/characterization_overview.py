from __future__ import annotations

from typing import Dict

from base_report.base_report_slides import BaseReportSlides, Frame
from ..helpers.data_holders import Photodiode, ReportData
from ..helpers.paths import calc_plot_path


RINGS = ["0", "1", "2", "3", "4"]
COLUMNS = ["0", "1", "2", "3"]


def _extract_refpd_for_sensor(photodiode_data: Photodiode, wavelength: str):
    pd_linreg = None
    if photodiode_data and photodiode_data.analysis:
        pd_linreg = getattr(photodiode_data.analysis, "linreg_refpd_vs_adc", None)
    # Prefer fileset-level linreg by wavelength for overview tables.

    filesets = photodiode_data.filesets if photodiode_data else {}
    preferred_order = (f"{wavelength}_FW5", f"{wavelength}_FW4")
    for key in preferred_order:
        fs = filesets.get(key)
        if fs is None:
            continue
        lr = fs.analysis.linreg_refpd_vs_adc if fs.analysis else None
        if lr is not None:
            return lr

    for key, fs in filesets.items():
        if not key.startswith(f"{wavelength}_"):
            continue
        lr = fs.analysis.linreg_refpd_vs_adc if fs.analysis else None
        if lr is not None:
            return lr
    if pd_linreg is not None:
        return pd_linreg
    return None


def _extract_power_for_sensor(photodiode_data: Photodiode, wavelength: str):
    filesets = photodiode_data.filesets if photodiode_data else {}
    preferred_order = (f"{wavelength}_FW5", f"{wavelength}_FW4")
    for key in preferred_order:
        fs = filesets.get(key)
        if fs is None:
            continue
        cf = fs.analysis.adc_to_power if fs.analysis else None
        if cf is not None:
            return cf

    for key, fs in filesets.items():
        if not key.startswith(f"{wavelength}_"):
            continue
        cf = fs.analysis.adc_to_power if fs.analysis else None
        if cf is not None:
            return cf
    return None


def _fmt(value: object, precision: int = 3) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{precision}e}"
    return str(value)


def _build_table_rows(
    photodiodes: Dict[str, Photodiode],
    sensors: list[str],
    wavelength: str,
    mode: str,
    power_unit: str,
) -> list[list[str]]:
    if mode == "power":
        rows = [[
            "Sensor",
            f"Slope ({power_unit}/#adc)",
            f"Slope err ({power_unit}/#adc)",
            f"Intercept ({power_unit})",
            f"Intercept err ({power_unit})",
        ]]
    else:
        rows = [[
            "Sensor",
            "Slope (V/#adc)",
            "Slope err (V/#adc)",
            "Intercept (V)",
            "Intercept err (V)",
        ]]
    for sensor_id in sensors:
        pd_data = photodiodes.get(sensor_id)
        if mode == "power":
            fit = _extract_power_for_sensor(pd_data, wavelength=wavelength)
            slope = getattr(fit, "slope", None)
            slope_err = getattr(fit, "slope_err", None)
            intercept = getattr(fit, "intercept", None)
            intercept_err = getattr(fit, "intercept_err", None)
        else:
            fit = _extract_refpd_for_sensor(pd_data, wavelength=wavelength)
            slope = getattr(fit, "slope", None)
            slope_err = getattr(fit, "stderr", None)
            intercept = getattr(fit, "intercept", None)
            intercept_err = getattr(fit, "intercept_stderr", None)
        rows.append(
            [
                sensor_id,
                _fmt(slope),
                _fmt(slope_err),
                _fmt(intercept),
                _fmt(intercept_err),
            ]
        )
    return rows


def _add_ring_tables(
    report: BaseReportSlides,
    frame: Frame,
    photodiodes: Dict[str, Photodiode],
    wavelength: str,
    mode: str,
    power_unit: str,
) -> Frame:
    top_y = report.last_frame.y - report.last_frame.height - 14

    horizontal_gap = 12
    vertical_gap = 14
    table_width = (frame.width - 2 * horizontal_gap) / 3
    subtitle_gap = 6

    def _draw_ring_table(ring: str, x: float, y: float) -> float:
        sub_frame = report.add_subsection(
            f"Ring {ring} Sensors",
            x=x,
            y=y,
            width=table_width,
            toc=False,
        )
        ring_sensors = [f"{ring}.{col}" for col in COLUMNS]
        rows = _build_table_rows(
            photodiodes,
            ring_sensors,
            wavelength=wavelength,
            mode=mode,
            power_unit=power_unit,
        )
        table_frame = report.add_table(
            data=rows,
            x=x,
            y=sub_frame.y - sub_frame.height - subtitle_gap,
            width=table_width,
            zebra=True,
            col_align=["center", "center", "center", "center", "center"],
        )
        return table_frame.y - table_frame.height

    row1_y = top_y
    ring0_bottom = _draw_ring_table("0", frame.x, row1_y)
    ring1_bottom = _draw_ring_table("1", frame.x + table_width + horizontal_gap, row1_y)
    ring2_bottom = _draw_ring_table("2", frame.x + 2 * (table_width + horizontal_gap), row1_y)
    row1_bottom = min(ring0_bottom, ring1_bottom, ring2_bottom)

    ring3_top = row1_bottom - vertical_gap
    ring3_bottom = _draw_ring_table("3", frame.x, ring3_top)
    ring4_top = ring3_bottom - vertical_gap
    _draw_ring_table("4", frame.x, ring4_top)

    plot_x = frame.x + table_width + horizontal_gap
    plot_y = row1_bottom
    plot_width = 2 * table_width + horizontal_gap
    plot_height = plot_y - 10
    if plot_height <= 0:
        raise ValueError(
            f"Not enough vertical space for plot area: computed height={plot_height:.2f}"
        )
    return Frame(plot_x, plot_y, plot_width, plot_height)


def _resolve_plot_path(report_data: ReportData, wavelength: str, mode: str) -> str:
    if mode == "power":
        key = f"power_vs_adc_linregs_{wavelength}_simp"
    else:
        key = f"refpd_vs_adc_linregs_{wavelength}"

    plot_rel_path = getattr(report_data.plots, key, None)
    if not plot_rel_path:
        raise ValueError(f"Missing plot path for key '{key}' in report data.")
    return calc_plot_path(plot_rel_path)


def add_characterization_overview(
    report: BaseReportSlides,
    report_data: ReportData,
    frame: Frame,
    wavelength: str,
    title: str,
    mode: str = "refpd",
    power_unit: str = "W",
    show_note: bool = False,
) -> None:
    report.add_section(
        title,
        x=frame.x,
        y=frame.y,
        width=frame.width,
        anchor=f"characterization_overview_{wavelength}",
        toc=True,
    )

    photodiodes = report_data.analysis.photodiodes
    plot_frame = _add_ring_tables(
        report=report,
        frame=frame,
        photodiodes=photodiodes,
        wavelength=wavelength,
        mode=mode,
        power_unit=power_unit,
    )
    plot_path = _resolve_plot_path(report_data, wavelength=wavelength, mode=mode)
    report.add_plot(
        path=plot_path,
        x=plot_frame.x,
        y=plot_frame.y,
        width=plot_frame.width,
        height=plot_frame.height,
    )
