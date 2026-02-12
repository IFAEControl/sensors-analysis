from __future__ import annotations

from collections import defaultdict
from typing import Dict

from reportlab.lib import colors

from base_report.base_report_slides import BaseReportSlides, Frame
from ..helpers.data_holders import CalibrationReference, Photodiode, ReportData


def _fmt(value: object, precision: int = 3) -> str:
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


def _fmt_fixed(value: object, decimals: int = 6) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    return str(value)


def _get_calibration(report_data: ReportData) -> CalibrationReference | None:
    if report_data.calibration is not None:
        return report_data.calibration
    return report_data.meta.calibration


def _build_gain_config_rows(photodiodes: Dict[str, Photodiode]) -> list[list[str]]:
    by_gain = defaultdict(lambda: {"resistors": set(), "1064": set(), "532": set()})
    for pd in photodiodes.values():
        gain = pd.meta.gain or "Unknown"
        resistor = pd.meta.resistor or "N/A"
        by_gain[gain]["resistors"].add(resistor)
        for cfg in pd.filesets.keys():
            if cfg.startswith("1064_"):
                by_gain[gain]["1064"].add(cfg)
            elif cfg.startswith("532_"):
                by_gain[gain]["532"].add(cfg)

    rows = [["Gain", "Resistor", "1064 configuration", "532 configuration"]]
    for gain in sorted(by_gain.keys()):
        resistors = ", ".join(sorted(by_gain[gain]["resistors"])) or "N/A"
        cfg_1064 = ", ".join(sorted(by_gain[gain]["1064"])) or "N/A"
        cfg_532 = ", ".join(sorted(by_gain[gain]["532"])) or "N/A"
        rows.append([gain, resistors, cfg_1064, cfg_532])
    return rows


def _build_calibration_linreg_rows(
    calibration: CalibrationReference | None,
    power_unit: str,
) -> list[list[str]]:
    rows = [[
        "Configuration",
        f"slope ({power_unit}/V)",
        f"slope_err ({power_unit}/V)",
        f"intercept ({power_unit})",
        f"intercept_err ({power_unit})",
        "R",
    ]]
    if calibration is None:
        rows.append(["N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
        return rows

    for cfg in calibration.used_configurations:
        lr = calibration.linreg_by_configuration.get(cfg)
        rows.append([
            cfg,
            _fmt_fixed(lr.slope if lr else None, 3),
            _fmt(lr.stderr if lr else None),
            _fmt(lr.intercept if lr else None),
            _fmt(lr.intercept_stderr if lr else None),
            _fmt_r_value(lr.r_value if lr else None),
        ])
    return rows


def add_power_conversion_note(
    report: BaseReportSlides,
    report_data: ReportData,
    frame: Frame,
    power_unit: str,
) -> None:
    report.add_section(
        "Power Conversion Factors: Derivation and Calibration Mapping",
        x=frame.x,
        y=frame.y,
        width=frame.width,
        anchor="characterization_overview_power_conversion_note",
        toc=True,
    )

    top_y = report.last_frame.y - report.last_frame.height - 10
    gap = 12
    left_w = frame.width * 0.56
    right_w = frame.width - left_w - gap
    left_x = frame.x
    right_x = left_x + left_w + gap

    intro_paragraphs = [
        f"The conversion factors shown on the first two slides map board ADC counts to optical power in {power_unit}.",
        "They combine setup calibration (Power vs RefPD) with board characterization (RefPD vs ADC).",
        "The selected filter-wheel configuration depends on sensor gain. This determines the calibration configuration applied to convert ADC to power.",
    ]

    intro_frames = [
        report.get_paragraph_frame(
            p,
            x=left_x,
            y=top_y,
            width=left_w,
            font_size=10.5,
        )
        for p in intro_paragraphs
    ]
    intro_height = sum(f.height for f in intro_frames) + 4 * max(0, len(intro_frames) - 1)
    report.add_paragraphs(
        intro_paragraphs,
        x=left_x,
        y=top_y,
        width=left_w,
        height=intro_height,
        font_size=10.5,
        gap=4,
    )

    cal = _get_calibration(report_data)
    calib_info = [[
        "Calibration id",
        "Execution date",
        "Power unit",
    ], [
        (cal.id if cal and cal.id else "N/A"),
        (cal.execution_date if cal and cal.execution_date else "N/A"),
        power_unit,
    ]]
    gain_rows = _build_gain_config_rows(report_data.analysis.photodiodes)
    linreg_rows = _build_calibration_linreg_rows(calibration=cal, power_unit=power_unit)

    title_table_gap = 8
    section_gap = 10

    y_tables = top_y - intro_height - 6
    s1 = report.add_subsection("Calibration Used", x=left_x, y=y_tables, width=left_w, toc=False)
    t1 = report.add_table(
        data=calib_info,
        x=left_x,
        y=s1.y - s1.height - title_table_gap,
        width=left_w,
        zebra=True,
        col_align=["left", "center", "center"],
    )

    y_gain = t1.y - t1.height - section_gap
    s2 = report.add_subsection("Gain to Calibration Configuration", x=left_x, y=y_gain, width=left_w, toc=False)
    t2 = report.add_table(
        data=gain_rows,
        x=left_x,
        y=s2.y - s2.height - title_table_gap,
        width=left_w,
        zebra=True,
        col_align=["center", "center", "center", "center"],
    )

    y_lr = t2.y - t2.height - section_gap
    s3 = report.add_subsection("Setup Calibration: Power vs RefPD Linear Regression", x=left_x, y=y_lr, width=left_w, toc=False)
    report.add_table(
        data=linreg_rows,
        x=left_x,
        y=s3.y - s3.height - title_table_gap,
        width=left_w,
        zebra=True,
        col_align=["center", "center", "center", "center", "center", "center"],
    )

    box_y = top_y
    inner_pad = 8
    title_gap = 8
    formula_gap = -5
    formula_height = 50
    formulas = [
        r"P = S_{cal}\,V_{refpd} + I_{cal}",
        r"V_{refpd} = S_{char}\,ADC + I_{char}",
        r"P = (S_{cal}\,S_{char})\,ADC + (S_{cal}\,I_{char}+I_{cal})",
        r"S_{adc\rightarrow power}=S_{cal}\,S_{char}",
        r"I_{adc\rightarrow power}=S_{cal}\,I_{char}+I_{cal}",
        r"S_{err,adc\rightarrow power}=\sqrt{(S_{char}\,S_{err,cal})^2+(S_{cal}\,S_{err,char})^2}",
        r"I_{err,adc\rightarrow power}=\sqrt{(I_{char}\,S_{err,cal})^2+(S_{cal}\,I_{err,char})^2+I_{err,cal}^2}",
    ]
    title_probe = report.get_paragraph_frame(
        "Equations and Error Propagation",
        x=right_x + inner_pad,
        y=box_y - inner_pad,
        width=right_w - 2 * inner_pad,
        font_size=16,
        bold=True,
    )
    legend_text = "Notation: S = slope, I = intercept."
    legend_probe = report.get_paragraph_frame(
        legend_text,
        x=right_x + inner_pad,
        y=box_y - inner_pad,
        width=right_w - 2 * inner_pad,
        font_size=10.0,
    )
    formulas_total_h = len(formulas) * formula_height + max(0, len(formulas) - 1) * formula_gap
    box_h = inner_pad + title_probe.height + 4 + legend_probe.height + title_gap + formulas_total_h + inner_pad
    max_available_h = top_y - 10
    # if box_h > max_available_h:
    #     raise ValueError(
    #         f"Equation panel height ({box_h:.1f}) exceeds available space ({max_available_h:.1f})."
    #     )
    report.add_rectangle(
        x=right_x,
        y=box_y,
        width=right_w,
        height=box_h,
        fill_color=colors.HexColor("#F7FAFD"),
        stroke_color=colors.HexColor("#B7C3D0"),
        stroke_width=0.6,
    )
    title_frame = report.add_paragraph(
        "Equations and Error Propagation",
        x=right_x + inner_pad,
        y=box_y - inner_pad,
        width=right_w - 2 * inner_pad,
        font_size=16,
        bold=True,
    )

    legend_frame = report.add_paragraph(
        legend_text,
        x=right_x + inner_pad,
        y=title_frame.y - title_frame.height - 4,
        width=right_w - 2 * inner_pad,
        font_size=10.0,
    )

    formula_y = legend_frame.y - legend_frame.height - title_gap
    for formula in formulas:
        f = report.add_formula(
            formula=formula,
            x=right_x + inner_pad,
            y=formula_y,
            width=right_w - 2 * inner_pad,
            height=formula_height,
            font_size=11.0,
            display_mode=True,
            fallback_to_text=True,
            render_horizontal_padding_px=0,
            render_vertical_padding_px=0,
        )
        formula_y = f.y - f.height - formula_gap
