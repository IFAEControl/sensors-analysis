
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from base_report.base_report import BaseReport
from ..helpers.data_holders import SanityCheckEntry

def add_sanity_check_box(report: BaseReport, check:SanityCheckEntry, simplified:bool=False):

        severity_value = (check.severity or "").strip().lower()
        is_warning = severity_value in {"warning", "warnings"}
        is_error = severity_value == "error"

        if check.passed:
            background_color = colors.HexColor("#D4EDDA")
            border_color = colors.HexColor("#28A745")
        elif is_warning:
            background_color = colors.HexColor("#FFE9D3")
            border_color = colors.HexColor("#C65A00")
        else:
            background_color = colors.HexColor("#F8D7DA")
            border_color = colors.HexColor("#B02A37")

        title_para = Paragraph(
            f"<b>{check.check_name or 'Sanity Check'}</b>",
            report.styles["BodyText"],
        )
        body_style = ParagraphStyle(
            name="SanityCheckBody",
            parent=report.styles["BodyText"],
            textColor=colors.HexColor("#444444"),
            fontSize=9,
            leading=9.0,
            spaceBefore=0,
            spaceAfter=0,
        )
        body_lines = []
        if check.info:
            body_lines.append(Paragraph(check.info, body_style))
        if check.check_explanation and not simplified:
            body_lines.append(Paragraph(check.check_explanation, body_style))
        if not body_lines:
            body_lines.append(Paragraph("No additional details.", body_style))

        def format_value(value):
            if value is None or value == "":
                return "N/A"
            if isinstance(value, bool):
                return "Yes" if value else "No"
            return str(value)

        small_style = ParagraphStyle(
            name="SanityCheckMeta",
            parent=report.styles["BodyText"],
            fontSize=6,
            textColor=colors.HexColor("#333333"),
            leading=6.0,
            spaceBefore=0,
            spaceAfter=0,
        )
        meta_parts = [
            f"<b>check_args</b>: {format_value(check.check_args)}",
            f"<b>passed</b>: {format_value(check.passed)}",
            f"<b>severity</b>: {format_value(check.severity)}",
            f"<b>exec_error</b>: {format_value(check.exec_error)}",
            f"<b>internal</b>: {format_value(check.internal)}",
        ]
        meta_para = Paragraph(" | ".join(meta_parts), small_style)

        left_cell = [title_para] + body_lines 
        if not simplified:
            left_cell += [meta_para]

        severity_display = (check.severity or "").strip().capitalize()
        right_cell = ""
        if not check.passed and severity_display:
            severity_style = ParagraphStyle(
                name="SanityCheckSeverity",
                parent=report.styles["BodyText"],
                textColor=colors.HexColor("#333333"),
                alignment=TA_RIGHT,
            )
            right_cell = Paragraph(f"<b>{severity_display}</b>", severity_style)

        check_table = Table(
            [[left_cell, right_cell]],
            colWidths=[report.doc.width * 0.80, report.doc.width * 0.20],
            hAlign="LEFT",
        )
        check_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), background_color),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ROUNDEDCORNERS", [5, 5, 5, 5]),
            ("GRID", (0, 0), (0, -1), 0, colors.transparent),
        ]))

        report.story.append(check_table)
        report.story.append(Spacer(1, 8))
