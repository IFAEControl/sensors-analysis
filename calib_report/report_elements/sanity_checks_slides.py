from reportlab.lib import colors

from base_report.base_report_slides import BaseReportSlides, Frame
from ..helpers.data_holders import SanityCheckEntry


def _build_sanity_check_box_layout(
    report: BaseReportSlides,
    check: SanityCheckEntry,
    x: float,
    y: float,
    width: float,
    simplified: bool = False,
) -> dict:
    severity_value = (check.severity or "").strip().lower()
    is_warning = severity_value in {"warning", "warnings"}
    is_error = severity_value == "error"

    if check.passed:
        background_color = colors.HexColor("#D4EDDA")
        border_color = colors.HexColor("#28A745")
        text_color = colors.HexColor("#1E4D2B")
    elif is_warning:
        background_color = colors.HexColor("#FFE9D3")
        border_color = colors.HexColor("#C65A00")
        text_color = colors.HexColor("#5A2C00")
    else:
        background_color = colors.HexColor("#F8D7DA")
        border_color = colors.HexColor("#B02A37")
        text_color = colors.HexColor("#5B151A")

    def format_value(value):
        if value is None or value == "":
            return "N/A"
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)

    title_text = check.check_name or "Sanity Check"
    body_texts: list[str] = []
    if check.info:
        body_texts.append(check.info)
    if check.check_explanation and not simplified:
        body_texts.append(check.check_explanation)
    if not body_texts:
        body_texts.append("No additional details.")

    meta_text = ""
    if not simplified:
        meta_parts = [
            f"<b>check_args</b>: {format_value(check.check_args)}",
            f"<b>passed</b>: {format_value(check.passed)}",
            f"<b>severity</b>: {format_value(check.severity)}",
            f"<b>exec_error</b>: {format_value(check.exec_error)}",
            f"<b>internal</b>: {format_value(check.internal)}",
        ]
        meta_text = " | ".join(meta_parts)

    pad_x = 8
    pad_y = 6
    gap = 6
    content_width = width - 2 * pad_x
    left_width = content_width
    left_x = x + pad_x

    severity_display = (check.severity or "").strip().capitalize()
    title_full = title_text
    if not check.passed and severity_display:
        title_full = f"{title_text} ({severity_display})"

    title_frame = report.get_paragraph_frame(
        title_full,
        x=left_x,
        y=y - pad_y,
        width=left_width,
        font_size=12,
        font_color=text_color,
        bold=True,
    )
    left_height = title_frame.height
    cursor_y = title_frame.y - title_frame.height - 2

    body_frames: list[Frame] = []
    for body_text in body_texts:
        frame = report.get_paragraph_frame(
            body_text,
            x=left_x,
            y=cursor_y,
            width=left_width,
            font_size=9.5,
            font_color=colors.HexColor("#444444"),
        )
        body_frames.append(frame)
        left_height += 2 + frame.height
        cursor_y = cursor_y - frame.height - 2

    meta_frame = None
    if meta_text:
        meta_frame = report.get_paragraph_frame(
            meta_text,
            x=left_x,
            y=cursor_y,
            width=left_width,
            font_size=7,
            font_color=colors.HexColor("#333333"),
        )
        left_height += 2 + meta_frame.height

    total_height = left_height + 2 * pad_y
    badge_frame = Frame(x, y, width, total_height)

    return {
        "badge_frame": badge_frame,
        "background_color": background_color,
        "border_color": border_color,
        "text_color": text_color,
        "pad_y": pad_y,
        "title_text": title_full,
        "body_texts": body_texts,
        "meta_text": meta_text,
        "title_frame": title_frame,
        "body_frames": body_frames,
        "meta_frame": meta_frame,
        "severity_display": severity_display,
    }


def get_sanity_check_box_frame(
    report: BaseReportSlides,
    check: SanityCheckEntry,
    x: float,
    y: float,
    width: float,
    simplified: bool = False,
) -> Frame:
    layout = _build_sanity_check_box_layout(report, check, x, y, width, simplified)
    return layout["badge_frame"]


def add_sanity_check_box(
    report: BaseReportSlides,
    check: SanityCheckEntry,
    x: float,
    y: float,
    width: float,
    simplified: bool = False,
) -> Frame:
    layout = _build_sanity_check_box_layout(report, check, x, y, width, simplified)
    badge_frame = layout["badge_frame"]
    title_text = layout["title_text"]
    body_texts = layout["body_texts"]
    meta_text = layout["meta_text"]
    title_frame = layout["title_frame"]
    body_frames = layout["body_frames"]
    meta_frame = layout["meta_frame"]
    severity_display = layout["severity_display"]
    pad_y = layout["pad_y"]

    report.add_rectangle(
        x=badge_frame.x,
        y=badge_frame.y,
        width=badge_frame.width,
        height=badge_frame.height,
        fill_color=layout["background_color"],
        stroke_color=layout["border_color"],
        stroke_width=1.0,
    )
    report.add_paragraph(
        title_text,
        x=title_frame.x,
        y=title_frame.y,
        width=title_frame.width,
        font_size=12,
        font_color=layout["text_color"],
        bold=True,
    )
    for frame, body_text in zip(body_frames, body_texts):
        report.add_paragraph(
            body_text,
            x=frame.x,
            y=frame.y,
            width=frame.width,
            font_size=9.5,
            font_color=colors.HexColor("#444444"),
        )
    if meta_frame and meta_text:
        report.add_paragraph(
            meta_text,
            x=meta_frame.x,
            y=meta_frame.y,
            width=meta_frame.width,
            font_size=7,
            font_color=colors.HexColor("#333333"),
        )
    return badge_frame
