from __future__ import annotations

from reportlab.lib import colors

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


def _add_ring_tables(
    report: BaseReportSlides,
    frame: Frame,
    photodiodes: dict,
) -> float:
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
    return row2_y - row2_height - 12


def _add_note_rectangle(
    report: BaseReportSlides,
    frame: Frame,
    note_y: float,
) -> None:
    note_width = frame.width
    note_x = frame.x

    pad_x = 12
    pad_top = 10
    pad_bottom = 10
    paragraph_gap = 4
    formula_gap = 2

    inner_x = note_x + pad_x
    inner_width = note_width - 2 * pad_x
    col_gap = 12
    text_col_width = (inner_width - col_gap) / 2
    formula_col_x = inner_x + text_col_width + col_gap
    formula_col_width = text_col_width

    note_title = "Note"
    note_paragraphs = [
        "The values shown in these tables are used to convert read ADC counts to Reference Photodiode volts.",
        "To convert ADC counts to optical power in watts, this conversion must be combined with the setup calibration.",
    ]
    formulas = [
        r"V_{refpd} = <slope_v> \cdot ADC + <intercept_v>",
        r"P_W = <slope_w> \cdot V_{refpd} + <intercept_w>",
        r"P_W = <slope_w> \cdot (<slope_v> \cdot ADC + <intercept_v>) + <intercept_w>",
    ]
    formula_font_size = 11.0
    formula_width = formula_col_width * 0.99

    title_frame = report.get_paragraph_frame(
        note_title,
        x=inner_x,
        y=note_y - pad_top,
        width=inner_width,
        font_size=12,
        bold=True,
    )
    paragraph_frames = [
        report.get_paragraph_frame(
            p,
            x=inner_x,
            y=note_y,
            width=text_col_width,
            font_size=10.0,
        )
        for p in note_paragraphs
    ]
    paragraphs_height = sum(f.height for f in paragraph_frames) + paragraph_gap * max(
        0, len(paragraph_frames) - 1
    )
    if paragraphs_height > note_y:
        raise ValueError(
            f"Note paragraphs height ({paragraphs_height:.1f}) exceeds available note_y ({note_y:.1f})."
        )

    top_block_height = pad_top + title_frame.height + 6 + paragraphs_height
    note_height = top_block_height + pad_bottom
    if note_height > note_y + 1e-6:
        raise ValueError(
            f"Calculated note height ({note_height:.1f}) exceeds note_y ({note_y:.1f})."
        )
    note_height = max(note_height, note_y - pad_bottom) # enforce a minimum height for aesthetics

    formulas_gaps = formula_gap * max(0, len(formulas) - 1)
    formula_start_y = note_y - pad_top - title_frame.height - 6
    formula_area_height = formula_start_y - 10
    available_for_formulas = formula_area_height - formulas_gaps
    if len(formulas) > 0 and available_for_formulas <= 0:
        raise ValueError(
            "No vertical space available in the right column to place formulas."
        )
    if len(formulas) > 0:
        formula_box_height = available_for_formulas / len(formulas)
    else:
        formula_box_height = 0.0
    if len(formulas) > 0 and formula_box_height <= 0:
        raise ValueError("Computed non-positive formula box height.")

    report.add_rectangle(
        x=note_x,
        y=note_y,
        width=note_width,
        height=note_height,
        fill_color=colors.HexColor("#F7FAFD"),
        stroke_color=colors.HexColor("#B7C3D0"),
        stroke_width=0.6,
    )

    cursor_y = note_y - pad_top
    title_drawn = report.add_paragraph(
        note_title,
        x=inner_x,
        y=cursor_y,
        width=inner_width,
        font_size=12,
        bold=True,
    )
    cursor_y = title_drawn.y - title_drawn.height - 6

    report.add_paragraphs(
        note_paragraphs,
        x=inner_x,
        y=cursor_y,
        width=text_col_width,
        height=paragraphs_height,
        font_size=10.0,
        gap=paragraph_gap,
    )

    formula_cursor_y = cursor_y
    formula_x = formula_col_x + (formula_col_width - formula_width) / 2
    for eq in formulas:
        ff = report.add_formula(
            formula=eq,
            x=formula_x,
            y=formula_cursor_y,
            width=formula_width,
            height=formula_box_height,
            font_size=formula_font_size,
            display_mode=True,
            fallback_to_text=True,
            render_horizontal_padding_px=0,
            render_vertical_padding_px=0,
        )
        formula_cursor_y = ff.y - ff.height - formula_gap


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
    note_y = _add_ring_tables(report=report, frame=frame, photodiodes=photodiodes)
    _add_note_rectangle(report=report, frame=frame, note_y=note_y)
