from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Sequence

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas

try:
    from pdfrw import PdfReader
    from pdfrw.buildxobj import pagexobj
    from pdfrw.toreportlab import makerl
except ImportError:  # pragma: no cover - optional dependency
    PdfReader = None
    pagexobj = None
    makerl = None


SLIDE_16x9 = (13.333 * inch, 7.5 * inch)


@dataclass(frozen=True)
class TextStyle:
    font_name: str
    font_size: float
    leading: float
    color: colors.Color


@dataclass(frozen=True)
class Frame:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class TocEntry:
    level: int
    text: str
    anchor: str | None
    page_number: int


class BaseReportSlides:
    def __init__(
        self,
        output_path: str,
        title: str,
        subtitle: str | None = None,
        logo_path: str | None = None,
        page_size: tuple[float, float] = SLIDE_16x9,
        header_height: float = 50,
        debug: bool = False,
    ) -> None:
        self.output_path = output_path
        self.title = title
        self.subtitle = subtitle
        self.logo_path = logo_path
        self.page_size = page_size
        self.header_height = header_height
        self.debug = debug

        self._canvas = canvas.Canvas(self.output_path, pagesize=self.page_size)
        self._page_number = 0
        self._toc_entries: list[TocEntry] = []

        self.header_background = colors.HexColor("#0B6B46")
        self.header_text = colors.white
        self.body_text = colors.HexColor("#1A1A1A")
        self.table_header_bg = colors.HexColor("#2C3331")
        self.table_grid = colors.HexColor("#B5BCC3")
        self.table_zebra_bg = colors.HexColor("#EDF2F6")

        self.header_style = TextStyle("Helvetica-Bold", 18, 22, self.header_text)
        self.subtitle_style = TextStyle("Helvetica", 12, 14, self.header_text)
        self.section_style = TextStyle("Helvetica-Bold", 20, 24, self.body_text)
        self.subsection_style = TextStyle("Helvetica-Bold", 16, 20, self.body_text)
        self.subsubsection_style = TextStyle("Helvetica-Bold", 13, 17, self.body_text)
        self.paragraph_style = TextStyle("Helvetica", 11.5, 15, self.body_text)
        self.table_style = TextStyle("Helvetica", 10, 12, self.body_text)
        self.table_header_style = TextStyle("Helvetica-Bold", 10, 12, colors.HexColor("#F2F5F3"))
        self.debug_style = TextStyle("Helvetica", 7.5, 9, colors.HexColor("#7A7A7A"))

    def add_slide(self, title: str | None = None, subtitle: str | None = None) -> None:
        if self._page_number > 0:
            self._canvas.showPage()
        self._page_number += 1
        self._draw_header(title or self.title, subtitle or self.subtitle)

    def add_section(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        anchor: str | None = None,
        toc: bool = False,
    ) -> Frame:
        self._register_toc_entry(level=0, text=text, anchor=anchor, toc=toc)
        height = self._draw_wrapped_text(text, x, y, width, self.section_style)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        return frame

    def add_subsection(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        anchor: str | None = None,
        toc: bool = False,
    ) -> Frame:
        self._register_toc_entry(level=1, text=text, anchor=anchor, toc=toc)
        height = self._draw_wrapped_text(text, x, y, width, self.subsection_style)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        return frame

    def add_subsubsection(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        anchor: str | None = None,
        toc: bool = False,
    ) -> Frame:
        self._register_toc_entry(level=2, text=text, anchor=anchor, toc=toc)
        height = self._draw_wrapped_text(text, x, y, width, self.subsubsection_style)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        return frame

    def add_paragraph(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        font_size: float | None = None,
        font_color: colors.Color | None = None,
        bold: bool = False,
        preserve_newlines: bool = False,
    ) -> Frame:
        normalized_text = text if preserve_newlines else self._normalize_text(text)
        base_style = self.paragraph_style
        resolved_font_size = font_size if font_size is not None else base_style.font_size
        resolved_leading = max(base_style.leading, resolved_font_size * 1.2)
        style = TextStyle(
            "Helvetica-Bold" if bold else base_style.font_name,
            resolved_font_size,
            resolved_leading,
            font_color if font_color is not None else base_style.color,
        )
        height = self._draw_wrapped_text(normalized_text, x, y, width, style)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        return frame

    def get_paragraph_frame(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        font_size: float | None = None,
        font_color: colors.Color | None = None,
        bold: bool = False,
        preserve_newlines: bool = False,
    ) -> Frame:
        normalized_text = text if preserve_newlines else self._normalize_text(text)
        base_style = self.paragraph_style
        resolved_font_size = font_size if font_size is not None else base_style.font_size
        resolved_leading = max(base_style.leading, resolved_font_size * 1.2)
        style = TextStyle(
            "Helvetica-Bold" if bold else base_style.font_name,
            resolved_font_size,
            resolved_leading,
            font_color if font_color is not None else base_style.color,
        )
        height = self._measure_wrapped_text(normalized_text, width, style)
        return Frame(x, y, width, height)

    def add_table(
        self,
        data: Sequence[Sequence[str]],
        x: float,
        y: float,
        width: float,
        header_rows: int = 1,
        zebra: bool = False,
        col_widths: Sequence[float] | None = None,
        col_align: Sequence[str] | None = None,
    ) -> Frame:
        if not data:
            frame = Frame(x, y, width, 0)
            self._maybe_draw_debug(frame)
            return frame

        num_cols = max(len(row) for row in data)
        if col_align is None:
            col_align = ["left"] * num_cols
        elif len(col_align) != num_cols:
            raise ValueError("col_align length must match number of columns")

        if col_widths is None:
            col_widths = [width / num_cols] * num_cols
        else:
            if len(col_widths) != num_cols:
                raise ValueError("col_widths length must match number of columns")
            total = sum(col_widths)
            if total <= 0:
                raise ValueError("col_widths total must be > 0")
            scale = width / total
            col_widths = [w * scale for w in col_widths]

        wrapped_rows: list[list[list[str]]] = []
        row_heights: list[float] = []
        for row in data:
            row_cells: list[list[str]] = []
            max_lines = 1
            for col_idx, cell in enumerate(row):
                style = self.table_header_style if len(wrapped_rows) < header_rows else self.table_style
                lines = simpleSplit(str(cell), style.font_name, style.font_size, col_widths[col_idx] - 8)
                max_lines = max(max_lines, len(lines))
                row_cells.append(lines)
            wrapped_rows.append(row_cells)
            style = self.table_header_style if len(wrapped_rows) <= header_rows else self.table_style
            row_heights.append(max_lines * style.leading + 6)

        table_height = sum(row_heights)
        current_y = y
        for row_idx, row in enumerate(wrapped_rows):
            row_height = row_heights[row_idx]
            row_y = current_y - row_height
            if row_idx < header_rows:
                self._canvas.setFillColor(self.table_header_bg)
                self._canvas.rect(x, row_y, width, row_height, fill=1, stroke=0)
            elif zebra and row_idx % 2 == 1:
                self._canvas.setFillColor(self.table_zebra_bg)
                self._canvas.rect(x, row_y, width, row_height, fill=1, stroke=0)

            col_x = x
            for col_idx, cell_lines in enumerate(row):
                style = self.table_header_style if row_idx < header_rows else self.table_style
                self._canvas.setFont(style.font_name, style.font_size)
                self._canvas.setFillColor(style.color)
                text_y = row_y + row_height - style.leading - 3
                for line in cell_lines:
                    align = col_align[col_idx].lower()
                    if align == "center":
                        self._canvas.drawCentredString(col_x + col_widths[col_idx] / 2, text_y, line)
                    elif align == "right":
                        self._canvas.drawRightString(col_x + col_widths[col_idx] - 4, text_y, line)
                    else:
                        self._canvas.drawString(col_x + 4, text_y, line)
                    text_y -= style.leading
                col_x += col_widths[col_idx]

            current_y = row_y

        self._canvas.setStrokeColor(self.table_grid)
        self._canvas.setLineWidth(0.6)
        self._canvas.rect(x, y - table_height, width, table_height, fill=0, stroke=1)

        col_x = x
        for col_width in col_widths[:-1]:
            col_x += col_width
            self._canvas.line(col_x, y, col_x, y - table_height)

        row_y = y
        for height in row_heights[:-1]:
            row_y -= height
            self._canvas.line(x, row_y, x + width, row_y)

        frame = Frame(x, y, width, table_height)
        self._maybe_draw_debug(frame)
        return frame

    def set_table_style(
        self,
        header_style: TextStyle | None = None,
        body_style: TextStyle | None = None,
        header_background: colors.Color | None = None,
        grid_color: colors.Color | None = None,
        zebra_background: colors.Color | None = None,
    ) -> None:
        if header_style is not None:
            self.table_header_style = header_style
        if body_style is not None:
            self.table_style = body_style
        if header_background is not None:
            self.table_header_bg = header_background
        if grid_color is not None:
            self.table_grid = grid_color
        if zebra_background is not None:
            self.table_zebra_bg = zebra_background

    def add_plot(
        self,
        path: str,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
    ) -> Frame:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Plot not found: {path}")

        ext = os.path.splitext(path)[1].lower()
        frame = self.get_plot_frame(path, x, y, width=width, height=height)
        draw_width = frame.width
        draw_height = frame.height
        if ext == ".pdf":
            if PdfReader is None:
                raise ImportError("pdfrw is required to embed PDF figures.")
            page = PdfReader(path).pages[0]
            media_box = list(map(float, page.MediaBox))
            src_width = media_box[2] - media_box[0]
            src_height = media_box[3] - media_box[1]
            scale_x = draw_width / src_width
            scale_y = draw_height / src_height
            xobj = pagexobj(page)
            rl_obj = makerl(self._canvas, xobj)
            self._canvas.saveState()
            self._canvas.translate(x, y - draw_height)
            self._canvas.scale(scale_x, scale_y)
            self._canvas.doForm(rl_obj)
            self._canvas.restoreState()
        else:
            img = ImageReader(path)
            width_px, height_px = img.getSize()
            self._canvas.drawImage(
                img,
                x,
                y - draw_height,
                width=draw_width,
                height=draw_height,
                preserveAspectRatio=True,
                mask="auto",
            )

        self._maybe_draw_debug(frame)
        return frame

    def get_plot_frame(
        self,
        path: str,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
    ) -> Frame:
        src_width, src_height = self._get_plot_source_size(path)
        draw_width, draw_height = self._resolve_plot_size(
            src_width, src_height, width, height
        )
        return Frame(x, y, draw_width, draw_height)

    def add_rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill_color: colors.Color,
        stroke_color: colors.Color | None = None,
        stroke_width: float = 0.5,
    ) -> Frame:
        self._canvas.setFillColor(fill_color)
        if stroke_color is None:
            self._canvas.rect(x, y - height, width, height, fill=1, stroke=0)
            frame = Frame(x, y, width, height)
            self._maybe_draw_debug(frame)
            return frame
        self._canvas.setStrokeColor(stroke_color)
        self._canvas.setLineWidth(stroke_width)
        self._canvas.rect(x, y - height, width, height, fill=1, stroke=1)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        return frame

    def save(self) -> None:
        self._canvas.save()

    def get_toc_entries(self) -> list[TocEntry]:
        return list(self._toc_entries)

    def add_table_of_contents(
        self,
        x: float,
        y: float,
        width: float,
        title: str = "Table of Contents",
    ) -> Frame:
        if not self._toc_entries:
            frame = Frame(x, y, width, 0)
            self._maybe_draw_debug(frame)
            return frame

        used_height = self._draw_wrapped_text(title, x, y, width, self.section_style)
        cursor_y = y - used_height - 6

        for entry in self._toc_entries:
            indent = entry.level * 18
            label = entry.text
            page_text = str(entry.page_number)
            text_width = width - indent - 28
            line_height = self.paragraph_style.leading
            lines = simpleSplit(label, self.paragraph_style.font_name, self.paragraph_style.font_size, text_width)
            for line in lines:
                self._canvas.setFont(self.paragraph_style.font_name, self.paragraph_style.font_size)
                self._canvas.setFillColor(self.paragraph_style.color)
                self._canvas.drawString(x + indent, cursor_y - line_height, line)
                cursor_y -= line_height
                used_height += line_height
            self._canvas.drawRightString(x + width, cursor_y + line_height, page_text)
            cursor_y -= 4
            used_height += 4

        frame = Frame(x, y, width, used_height)
        self._maybe_draw_debug(frame)
        return frame

    def _draw_header(self, title: str, subtitle: str | None) -> None:
        page_width, page_height = self.page_size
        self._canvas.setFillColor(self.header_background)
        self._canvas.rect(0, page_height - self.header_height, page_width, self.header_height, fill=1, stroke=0)

        left_margin = 32
        right_margin = 32
        header_mid = page_height - self.header_height / 2

        if self.logo_path and os.path.exists(self.logo_path):
            logo_height = self.header_height - 16
            logo_width, logo_height = self._scaled_logo_size(logo_height)
            self._canvas.drawImage(
                self.logo_path,
                left_margin,
                page_height - self.header_height + (self.header_height - logo_height) / 2,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )
            title_x = left_margin + logo_width + 12
        else:
            title_x = left_margin

        self._canvas.setFont(self.header_style.font_name, self.header_style.font_size)
        self._canvas.setFillColor(self.header_style.color)
        self._canvas.drawString(title_x, header_mid + 2, title)

        if subtitle:
            self._canvas.setFont(self.subtitle_style.font_name, self.subtitle_style.font_size)
            self._canvas.setFillColor(self.subtitle_style.color)
            self._canvas.drawString(title_x, header_mid - 14, subtitle)

        self._canvas.setFont("Helvetica", 9)
        self._canvas.setFillColor(self.header_text)
        self._canvas.drawRightString(page_width - right_margin, header_mid - 14, f"Slide {self._page_number}")

    def _draw_wrapped_text(self, text: str, x: float, y: float, width: float, style: TextStyle) -> float:
        lines = simpleSplit(text, style.font_name, style.font_size, width)
        self._canvas.setFont(style.font_name, style.font_size)
        self._canvas.setFillColor(style.color)
        text_y = y - style.leading
        for line in lines:
            self._canvas.drawString(x, text_y, line)
            text_y -= style.leading
        return len(lines) * style.leading

    def _measure_wrapped_text(self, text: str, width: float, style: TextStyle) -> float:
        lines = simpleSplit(text, style.font_name, style.font_size, width)
        return len(lines) * style.leading

    def _normalize_text(self, text: str) -> str:
        return " ".join(text.split())

    def _scaled_logo_size(self, target_height: float) -> tuple[float, float]:
        width_px, height_px = ImageReader(self.logo_path).getSize()
        ratio = width_px / float(height_px)
        return target_height * ratio, target_height

    def _get_plot_source_size(self, path: str) -> tuple[float, float]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Plot not found: {path}")
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            if PdfReader is None:
                raise ImportError("pdfrw is required to embed PDF figures.")
            page = PdfReader(path).pages[0]
            media_box = list(map(float, page.MediaBox))
            src_width = media_box[2] - media_box[0]
            src_height = media_box[3] - media_box[1]
            return src_width, src_height
        img = ImageReader(path)
        width_px, height_px = img.getSize()
        return float(width_px), float(height_px)

    def _resolve_plot_size(
        self,
        src_width: float,
        src_height: float,
        width: float | None,
        height: float | None,
    ) -> tuple[float, float]:
        if width is None and height is None:
            return src_width, src_height
        if width is None:
            return height * (src_width / src_height), height
        if height is None:
            return width, width * (src_height / src_width)
        return width, height

    def _register_toc_entry(
        self,
        level: int,
        text: str,
        anchor: str | None,
        toc: bool,
    ) -> None:
        if anchor:
            self._canvas.bookmarkPage(anchor)
            try:
                self._canvas.addOutlineEntry(text, anchor, level=level, closed=False)
            except Exception:
                pass
        if toc:
            self._toc_entries.append(
                TocEntry(
                    level=level,
                    text=text,
                    anchor=anchor,
                    page_number=self._page_number,
                )
            )

    def _maybe_draw_debug(self, frame: Frame) -> None:
        if not self.debug:
            return
        label = f"({frame.x:.1f}, {frame.y:.1f}, {frame.width:.1f}, {frame.height:.1f})"
        self._canvas.setFont(self.debug_style.font_name, self.debug_style.font_size)
        self._canvas.setFillColor(self.debug_style.color)
        self._canvas.drawString(frame.x + 2, frame.y - 2, label)
