from __future__ import annotations

from datetime import datetime
import os
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.flowables import Flowable

try:
    from pdfrw import PdfReader
    from pdfrw.buildxobj import pagexobj
    from pdfrw.toreportlab import makerl
except ImportError:  # pragma: no cover - optional dependency
    PdfReader = None
    pagexobj = None
    makerl = None


class PdfFigure(Flowable):
    def __init__(self, pdf_path: str, width: float, height: float) -> None:
        super().__init__()
        self.pdf_path = pdf_path
        self.width = width
        self.height = height

    def wrap(self, avail_width, avail_height):
        return self.width, self.height

    def draw(self):
        if PdfReader is None:
            raise ImportError("pdfrw is required to embed PDF figures.")
        page = PdfReader(self.pdf_path).pages[0]
        xobj = pagexobj(page)
        rl_obj = makerl(self.canv, xobj)
        x0, y0, x1, y1 = map(float, xobj.BBox)
        src_width = x1 - x0
        src_height = y1 - y0
        scale_x = self.width / src_width
        scale_y = self.height / src_height
        self.canv.saveState()
        self.canv.scale(scale_x, scale_y)
        self.canv.doForm(rl_obj)
        self.canv.restoreState()


class ReportDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._toc_entry_count = 0

    def beforeBuild(self) -> None:
        self._toc_entry_count = 0

    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            page_number = self.canv.getPageNumber()
            if style_name == "SectionHeading":
                self._toc_entry_count += 1
                self.notify("TOCEntry", (0, flowable.getPlainText(), page_number))
            elif style_name == "SubsectionHeading":
                self._toc_entry_count += 1
                self.notify("TOCEntry", (1, flowable.getPlainText(), page_number))
            elif style_name == "SubsubsectionHeading":
                self._toc_entry_count += 1
                self.notify("TOCEntry", (2, flowable.getPlainText(), page_number))


class BaseReport:
    def __init__(
        self,
        output_path: str,
        title: str,
        subtitle: str | None,
        logo_path: str,
        serial_number: str,
        page_size=A4,
    ) -> None:
        self.output_path = output_path
        self.title = title
        self.subtitle = subtitle
        self.logo_path = logo_path
        self.serial_number = serial_number

        self.styles = getSampleStyleSheet()
        self.styles["BodyText"].textColor = colors.HexColor("#1A1A1A")
        self.styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=self.styles["Heading1"],
                spaceAfter=6,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TOCHeading",
                parent=self.styles["SectionHeading"],
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="LinkText",
                parent=self.styles["BodyText"],
                textColor=colors.HexColor("#1B66C9"),
                underline=True,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SubsectionHeading",
                parent=self.styles["Heading2"],
                spaceAfter=4,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SubsubsectionHeading",
                parent=self.styles["Heading3"],
                fontSize=10.5,
                leading=12,
                spaceAfter=3,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CalloutText",
                parent=self.styles["BodyText"],
                fontSize=9.5,
                leading=12,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="FigureCaption",
                parent=self.styles["BodyText"],
                fontSize=8.5,
                leading=10,
                textColor=colors.HexColor("#6F7680"),
                alignment=TA_LEFT,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TableCaption",
                parent=self.styles["BodyText"],
                fontSize=8.5,
                leading=10,
                textColor=colors.HexColor("#6F7680"),
                alignment=TA_LEFT,
            )
        )

        self.doc = ReportDocTemplate(
            self.output_path,
            pagesize=page_size,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=25 * mm,
            bottomMargin=12 * mm,
            title=self.title,
        )
        self.story = []
        self.toc = TableOfContents()
        self.figure_index = 0
        self.table_index = 0
        self.section_index = 0
        self.subsection_index = 0
        self.subsubsection_index = 0
        self.toc.levelStyles = [
            ParagraphStyle(
                name="TOCLevel0",
                parent=self.styles["BodyText"],
                fontSize=9,
                leading=5,
                leftIndent=0,
                firstLineIndent=0,
                spaceAfter=0.1,
                textColor=colors.HexColor("#48494A")
            ),
            ParagraphStyle(
                name="TOCLevel1",
                parent=self.styles["BodyText"],
                fontSize=8.5,
                leading=3.5,
                leftIndent=8,
                firstLineIndent=0,
                spaceAfter=0.1,
                textColor=colors.HexColor("#6A6B6D"),
            ),
            ParagraphStyle(
                name="TOCLevel2",
                parent=self.styles["BodyText"],
                fontSize=7,
                leading=2,
                leftIndent=16,
                firstLineIndent=0,
                spaceAfter=0.1,
                textColor=colors.HexColor("#848585"),
            ),
        ]

    def add_page(self) -> None:
        self.story.append(PageBreak())

    def add_section(self, text: str, anchor: str | None = None) -> None:
        self.section_index += 1
        self.subsection_index = 0
        self.subsubsection_index = 0
        numbered_text = f"{self.section_index}. {text}"
        if anchor:
            numbered_text = f'<a name="{anchor}"/>{numbered_text}'
        self.story.append(Paragraph(numbered_text, self.styles["SectionHeading"]))
        self.story.append(Spacer(1, 6))

    def add_subsection(self, text: str, anchor: str | None = None) -> None:
        self.subsection_index += 1
        self.subsubsection_index = 0
        numbered_text = f"{self.section_index}.{self.subsection_index} {text}"
        if anchor:
            numbered_text = f'<a name="{anchor}"/>{numbered_text}'
        self.story.append(Paragraph(numbered_text, self.styles["SubsectionHeading"]))
        self.story.append(Spacer(1, 4))

    def add_subsubsection(self, text: str, anchor: str | None = None) -> None:
        self.subsubsection_index += 1
        numbered_text = (
            f"{self.section_index}.{self.subsection_index}.{self.subsubsection_index} {text}"
        )
        if anchor:
            numbered_text = f'<a name="{anchor}"/>{numbered_text}'
        self.story.append(Paragraph(numbered_text, self.styles["SubsubsectionHeading"]))
        self.story.append(Spacer(1, 3))

    def add_paragraph(self, text: str) -> None:
        self.story.append(Paragraph(text, self.styles["BodyText"]))
        self.story.append(Spacer(1, 6))

    def add_info_box(self, text: str) -> None:
        self._add_callout(
            text,
            background_color=colors.HexColor("#E9F4FE"),
            border_color=colors.HexColor("#6AA5D9"),
        )

    def add_warning_box(self, text: str) -> None:
        self._add_callout(
            text,
            background_color=colors.HexColor("#FFF3CD"),
            border_color=colors.HexColor("#D39E00"),
        )

    def add_error_box(self, text: str) -> None:
        self._add_callout(
            text,
            background_color=colors.HexColor("#F8D7DA"),
            border_color=colors.HexColor("#B02A37"),
        )
    
    def add_sanity_check(self, severity:str, title:str, description: str, passed: bool) -> None:
        background_color = colors.HexColor("#D4EDDA") if passed else colors.HexColor("#F8D7DA")
        border_color = colors.HexColor("#28A745") if passed else colors.HexColor("#B02A37")

        severity_color_map = {
            "Error": colors.HexColor("#8B0000"),
            "Warning": colors.HexColor("#CC7000"),
            "Info": colors.HexColor("#003366"),
        }
        severity_color = severity_color_map.get(severity, colors.black)

        title_para = Paragraph(f"<b>{title}</b>", self.styles["BodyText"])
        desc_para = Paragraph(description, ParagraphStyle(
            name="SanityCheckDesc",
            parent=self.styles["BodyText"],
            textColor=colors.HexColor("#555555"),
            fontSize=9,
        ))
        severity_para = Paragraph(f"<b>{severity}</b>", ParagraphStyle(
            name="SeverityText",
            parent=self.styles["BodyText"],
            textColor=severity_color,
            alignment=TA_RIGHT,
        ))

        left_cell = Table([[title_para], [desc_para]], colWidths=[self.doc.width * 0.85])
        left_cell.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        right_cell = Table([[severity_para]], colWidths=[self.doc.width * 0.15])
        right_cell.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        check_table = Table([[left_cell, right_cell]], colWidths=[self.doc.width * 0.85, self.doc.width * 0.15], hAlign="LEFT")
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

        self.story.append(check_table)
        self.story.append(Spacer(1, 8))


    def add_table(
        self,
        data: Sequence[Sequence[str]],
        keep_together: bool = False,
        description: str | None = None,
        center: bool = False,
        zebra: bool = False,
    ) -> None:

        table = Table(data, hAlign="CENTER" if center else "LEFT")
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EDF2")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1A1A1A")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B5BCC3")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
        ]
        if zebra:
            style_commands.append(
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EDF2F6")])
            )
        table.setStyle(TableStyle(style_commands))
        self._append_table_with_caption(
            table,
            keep_together=keep_together,
            description=description,
        )

    def add_condensed_table(
        self,
        data: Sequence[Sequence[str]],
        keep_together: bool = False,
        description: str | None = None,
        center: bool = False,
        zebra: bool = False,
    ) -> None:
        table = Table(data, hAlign="CENTER" if center else "LEFT")
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F2F5")),
            ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#F7F9FB")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1A1A1A")),
            ("TEXTCOLOR", (0, 1), (0, -1), colors.HexColor("#1A1A1A")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7CCD1")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]
        if zebra:
            style_commands.append(
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EDF2F6")])
            )
        table.setStyle(TableStyle(style_commands))
        self._append_table_with_caption(
            table,
            keep_together=keep_together,
            description=description,
        )

    def add_figure(
        self,
        image_path: str,
        width_mm: float = 140,
        description: str | None = None,
        center: bool = False,
    ) -> None:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        ext = os.path.splitext(image_path)[1].lower()
        if ext == ".pdf":
            if PdfReader is None:
                raise ImportError("pdfrw is required to embed PDF figures.")
            page = PdfReader(image_path).pages[0]
            media_box = list(map(float, page.MediaBox))
            src_width = media_box[2] - media_box[0]
            src_height = media_box[3] - media_box[1]
            aspect_ratio = src_height / src_width
            draw_width = width_mm * mm
            draw_height = draw_width * aspect_ratio
            image = PdfFigure(image_path, draw_width, draw_height)
        else:
            image = Image(image_path)
            width_px, height_px = ImageReader(image_path).getSize()
            aspect_ratio = height_px / float(width_px)
            image.drawWidth = width_mm * mm
            image.drawHeight = image.drawWidth * aspect_ratio
            draw_width = image.drawWidth
        self.figure_index += 1
        caption_text = f"Figure {self.figure_index}"
        if description:
            caption_text = f"{caption_text}: {description}"
        caption = Paragraph(caption_text, self.styles["FigureCaption"])
        if hasattr(image, "hAlign"):
            image.hAlign = "LEFT"
        figure_table = Table(
            [[image], [caption]],
            colWidths=[draw_width],
            hAlign="CENTER" if center else "LEFT",
        )
        figure_table.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 1), (0, 1), 1),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        self.story.append(KeepTogether([figure_table]))
        self.story.append(Spacer(1, 10))

    def build(self) -> None:
        self.doc.multiBuild(
            self.story,
            onFirstPage=self._draw_header,
            onLaterPages=self._draw_header,
        )

    def _draw_header(self, canvas, doc) -> None:
        canvas.saveState()
        page_width, page_height = doc.pagesize
        header_top = page_height - 5 * mm
        header_bottom = page_height - 20 * mm

        if os.path.exists(self.logo_path):
            logo_width, logo_height = self._scaled_logo_size(14 * mm)
            logo_y = header_bottom + (15 * mm - logo_height) / 2
            canvas.drawImage(
                self.logo_path,
                doc.leftMargin,
                logo_y,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )

        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColorRGB(6 / 255, 78 / 255, 59 / 255)
        title_y = header_bottom + 8.5 * mm
        canvas.drawCentredString(page_width / 2, title_y, self.title)
        if self.subtitle:
            canvas.setFillColorRGB(0, 0, 0)
            canvas.setFont("Helvetica", 12)
            canvas.drawCentredString(page_width / 2, title_y - 4 * mm, self.subtitle)

        meta_table = self._build_meta_table(canvas.getPageNumber())
        table_width, table_height = meta_table.wrap(0, 0)
        table_x = page_width - doc.rightMargin - table_width
        table_y = header_bottom + (15 * mm - table_height) / 2
        meta_table.drawOn(canvas, table_x, table_y)

        canvas.setLineWidth(0.5)
        canvas.setStrokeColor(colors.HexColor("#B5BCC3"))
        canvas.line(doc.leftMargin, header_bottom, page_width - doc.rightMargin, header_bottom)

        canvas.restoreState()

    def _build_meta_table(self, page_number: int) -> Table:
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [
            [now_text],
            [str(page_number)],
            [self.serial_number],
        ]
        table = Table(data, colWidths=[35 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return table

    def _add_callout(self, text: str, background_color, border_color) -> None:
        paragraph = Paragraph(text, self.styles["CalloutText"])
        table = Table([[paragraph]], colWidths=[self.doc.width], hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), background_color),
                    ("BOX", (0, 0), (-1, -1), 0.8, border_color),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("ROUNDEDCORNERS", [6, 6, 6, 6]),
                ]
            )
        )
        self.story.append(table)
        self.story.append(Spacer(1, 8))

    def _append_table(self, table: Table, keep_together: bool) -> None:
        if keep_together:
            self.story.append(KeepTogether([table, Spacer(1, 10)]))
        else:
            self.story.append(table)
            self.story.append(Spacer(1, 10))

    def _append_table_with_caption(
        self,
        table: Table,
        keep_together: bool,
        description: str | None,
    ) -> None:
        self.table_index += 1
        caption_text = f"Table {self.table_index}"
        if description:
            caption_text = f"{caption_text}: {description}"
        caption = Paragraph(caption_text, self.styles["TableCaption"])
        table_width, _ = table.wrap(self.doc.width, 0)
        wrapper = Table(
            [[table], [caption]],
            colWidths=[table_width],
            hAlign=getattr(table, "hAlign", "LEFT"),
        )
        wrapper.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 1), (0, 1), 2),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        if keep_together:
            self.story.append(KeepTogether([wrapper, Spacer(1, 10)]))
        else:
            self.story.append(wrapper)
            self.story.append(Spacer(1, 10))

    def _scaled_logo_size(self, target_height: float) -> tuple[float, float]:
        width_px, height_px = ImageReader(self.logo_path).getSize()
        ratio = width_px / float(height_px)
        return target_height * ratio, target_height

    def extend(self, flowables: Iterable) -> None:
        self.story.extend(flowables)

    def add_table_of_contents(self, page_break: bool = True) -> None:
        if page_break:
            self.story.append(PageBreak())
        self.story.append(Paragraph("Table of Contents", self.styles["TOCHeading"]))
        self.story.append(Spacer(1, 4))
        self.story.append(self.toc)
