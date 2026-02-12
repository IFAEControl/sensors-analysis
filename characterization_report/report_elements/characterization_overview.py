from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides, Frame


RINGS = ["0", "1", "2", "3", "4"]
COLUMNS = ["0", "1", "2", "3"]


def _extract_linreg_for_sensor(photodiode_data: dict) -> dict | None:
    analysis = photodiode_data.get("analysis", {}) or {}
    pd_linreg = analysis.get("linreg_refpd_vs_adc")
    if isinstance(pd_linreg, dict):
        return pd_linreg

    filesets = photodiode_data.get("filesets", {}) or {}
    preferred_order = ("1064_FW5", "532_FW4", "532_FW5")
    for key in preferred_order:
        fs = filesets.get(key)
        if not isinstance(fs, dict):
            continue
        lr = (fs.get("analysis", {}) or {}).get("linreg_refpd_vs_adc")
        if isinstance(lr, dict):
            return lr

    for fs in filesets.values():
        if not isinstance(fs, dict):
            continue
        lr = (fs.get("analysis", {}) or {}).get("linreg_refpd_vs_adc")
        if isinstance(lr, dict):
            return lr
    return None


def _fmt(value: object, precision: int = 3) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{precision}e}"
    return str(value)


def _build_table_rows(photodiodes: dict, sensors: list[str]) -> list[list[str]]:
    rows = [["Sensor", "Slope", "Slope err", "Intercept", "Intercept err"]]
    for sensor_id in sensors:
        pd_data = photodiodes.get(sensor_id, {}) or {}
        linreg = _extract_linreg_for_sensor(pd_data) or {}
        rows.append(
            [
                sensor_id,
                _fmt(linreg.get("slope")),
                _fmt(linreg.get("stderr")),
                _fmt(linreg.get("intercept")),
                _fmt(linreg.get("intercept_stderr")),
            ]
        )
    return rows


def add_characterization_overview(
    report: BaseReportSlides,
    report_data: dict,
    frame: Frame,
) -> None:
    report.add_section(
        "Characterization Overview",
        x=frame.x,
        y=frame.y,
        width=frame.width,
        anchor="characterization_overview",
        toc=True,
    )

    photodiodes = report_data.get("analysis", {}).get("photodiodes", {}) or {}
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
        rows = _build_table_rows(photodiodes, ring_sensors)
        table_frame = report.add_table(
            data=rows,
            x=x,
            y=sub_frame.y - sub_frame.height - subtitle_gap,
            width=table_width,
            zebra=True,
            col_align=["center", "center", "center", "center", "center"],
        )
        return sub_frame.height + subtitle_gap + table_frame.height

    row1_y = top_y

    # Top row: Rings 0,1,2
    row1_h0 = _draw_ring_table("0", frame.x, row1_y)
    row1_h1 = _draw_ring_table("1", frame.x + table_width + horizontal_gap, row1_y)
    row1_h2 = _draw_ring_table("2", frame.x + 2 * (table_width + horizontal_gap), row1_y)
    row1_height = max(row1_h0, row1_h1, row1_h2)
    row2_y = row1_y - row1_height - vertical_gap

    # Bottom row: Rings 3,4 centered under top row
    bottom_total_width = 2 * table_width + horizontal_gap
    row2_start_x = frame.x + (frame.width - bottom_total_width) / 2
    row2_h3 = _draw_ring_table("3", row2_start_x, row2_y)
    row2_h4 = _draw_ring_table("4", row2_start_x + table_width + horizontal_gap, row2_y)

    row2_height = max(row2_h3, row2_h4)
    paragraph_y = row2_y - row2_height - 14
    available_height = max(60, paragraph_y - 10)
    text_gap = 16
    text_width = (frame.width - text_gap)

    left_paragraphs = [
        "The values shown in these tables are used to convert read ADC counts to Reference Photodiode volts.",
        "ADC -> RefPD conversion: <b>V_refpd = <slope_v> * ADC + <intercept_v></b>.",
        "To convert ADC counts to optical power in watts, this conversion must be combined with the setup calibration.",
        "Setup conversion: <b>P_W = <slope_w> * V_refpd + <intercept_w></b>.",
        "Combined expression: <b>P_W = <slope_w> * (<slope_v> * ADC + <intercept_v>) + <intercept_w></b>.",
    ]
    report.add_paragraphs(
        left_paragraphs,
        x=frame.x,
        y=paragraph_y,
        width=text_width,
        height=available_height,
        font_size=10.5,
        gap=2,
    )

