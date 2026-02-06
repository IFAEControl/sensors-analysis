from __future__ import annotations

from dataclasses import dataclass
import io
import os
from typing import Sequence

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth
import re
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
        serial_number: str | None = None,
        active_area: Frame | None = None,
        page_size: tuple[float, float] = SLIDE_16x9,
        header_height: float = 50,
        debug: bool = False,
    ) -> None:
        self.output_path = output_path
        self.title = title
        self.subtitle = subtitle
        self.logo_path = logo_path
        self.serial_number = serial_number
        self.active_area = active_area or Frame(10, 480, 940, 470)
        self.page_size = page_size
        self.header_height = header_height
        self.debug = debug

        self._canvas = canvas.Canvas(self.output_path, pagesize=self.page_size)
        self._page_number = 0
        self._toc_entries: list[TocEntry] = []
        self._toc_snapshot: list[TocEntry] | None = None
        self._ops: list[tuple[str, tuple, dict]] = []
        self._suspend_recording = False
        self.last_frame: Frame | None = None

        self.header_background = colors.HexColor("#085F3E")
        self.header_text = colors.white
        self.body_text = colors.HexColor("#1A1A1A")
        self._reset_table_styles()

        self.header_style = TextStyle("Helvetica-Bold", 18, 22, self.header_text)
        self.subtitle_style = TextStyle("Helvetica", 12, 14, self.header_text)
        self.section_style = TextStyle("Helvetica-Bold", 20, 24, self.body_text)
        self.subsection_style = TextStyle("Helvetica-Bold", 16, 20, self.body_text)
        self.subsubsection_style = TextStyle("Helvetica-Bold", 13, 17, self.body_text)
        self.paragraph_style = TextStyle("Helvetica", 11.5, 15, self.body_text)
        self.debug_style = TextStyle("Helvetica", 7.5, 9, colors.HexColor("#7A7A7A"))

    def add_slide(self, title: str | None = None, subtitle: str | None = None) -> None:
        self._record_op("add_slide", title=title, subtitle=subtitle)
        if self._page_number > 0:
            self._canvas.showPage()
        self._page_number += 1
        self._draw_header(title or self.title, subtitle or self.subtitle)

    def get_active_area(self) -> Frame:
        return self.active_area

    def create_table_of_contents_slide(
        self,
        title: str = "ToC",
        subtitle: str = "Table of Contents",
        num_columns: int = 3,
        dot_leader: bool = True,
        draw_backgrounds: bool = False,
    ) -> Frame:
        if num_columns <= 0:
            raise ValueError("num_columns must be >= 1")

        self.add_slide(title=title, subtitle=subtitle)
        frames: list[Frame] = []
        margin_x = 20
        margin_y = 10
        page_width, page_height = self.page_size
        full_width = page_width
        full_height = page_height - self.header_height
        column_width = (full_width - (num_columns + 1) * margin_x) / num_columns
        x = margin_x
        y = full_height - margin_y
        toc_height = full_height - 2 * margin_y
        for _ in range(num_columns):
            frames.append(Frame(x=x, y=y, width=column_width, height=toc_height))
            x += column_width + margin_x

        if draw_backgrounds:
            for frame in frames:
                self.add_rectangle(
                    x=frame.x - margin_x / 3,
                    y=frame.y + margin_y / 2,
                    width=frame.width + 0.666 * margin_x,
                    height=frame.height + margin_y,
                    fill_color=colors.HexColor("#F3FFF6"),
                    stroke_color=colors.HexColor("#00501F"),
                    stroke_width=0.5,
                )

        return self.add_table_of_contents(frames=frames, dot_leader=dot_leader)

    def add_section(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        anchor: str | None = None,
        toc: bool = True,
    ) -> Frame:
        self._record_op(
            "add_section",
            text,
            x,
            y,
            width,
            anchor=anchor,
            toc=toc,
        )
        self._register_toc_entry(level=0, text=text, anchor=anchor, toc=toc)
        height = self._draw_wrapped_text(text, x, y, width, self.section_style)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        self._set_last_frame(frame)
        return frame

    def add_subsection(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        anchor: str | None = None,
        toc: bool = True,
    ) -> Frame:
        self._record_op(
            "add_subsection",
            text,
            x,
            y,
            width,
            anchor=anchor,
            toc=toc,
        )
        self._register_toc_entry(level=1, text=text, anchor=anchor, toc=toc)
        height = self._draw_wrapped_text(text, x, y, width, self.subsection_style)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        self._set_last_frame(frame)
        return frame

    def add_subsubsection(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        anchor: str | None = None,
        toc: bool = True,
    ) -> Frame:
        self._record_op(
            "add_subsubsection",
            text,
            x,
            y,
            width,
            anchor=anchor,
            toc=toc,
        )
        self._register_toc_entry(level=2, text=text, anchor=anchor, toc=toc)
        height = self._draw_wrapped_text(text, x, y, width, self.subsubsection_style)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        self._set_last_frame(frame)
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
        link_anchor: str | None = None,
    ) -> Frame:
        self._record_op(
            "add_paragraph",
            text,
            x,
            y,
            width,
            font_size=font_size,
            font_color=font_color,
            bold=bold,
            preserve_newlines=preserve_newlines,
            link_anchor=link_anchor,
        )
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
        if self._has_rich_tags(normalized_text):
            height = self._draw_wrapped_rich_text(normalized_text, x, y, width, style)
        else:
            height = self._draw_wrapped_text(normalized_text, x, y, width, style)
        frame = Frame(x, y, width, height)
        if link_anchor:
            self._canvas.linkRect(
                "",
                link_anchor,
                Rect=(frame.x, frame.y - frame.height, frame.x + frame.width, frame.y),
                relative=1,
                thickness=0,
                color=None,
            )
        self._maybe_draw_debug(frame)
        self._set_last_frame(frame)
        return frame

    def add_paragraphs(
        self,
        paragraphs: Sequence[str],
        x: float | None = None,
        y: float | None = None,
        width: float | None = None,
        height: float | None = None,
        frames: Sequence[Frame] | None = None,
        font_size: float | None = None,
        font_color: colors.Color | None = None,
        bold: bool = False,
        preserve_newlines: bool = False,
        gap: float = 6,
    ) -> list[Frame]:
        self._record_op(
            "add_paragraphs",
            paragraphs,
            x,
            y,
            width,
            height,
            frames=frames,
            font_size=font_size,
            font_color=font_color,
            bold=bold,
            preserve_newlines=preserve_newlines,
            gap=gap,
        )
        if frames is None:
            if x is None or y is None or width is None or height is None:
                raise ValueError("x, y, width, and height are required when frames is not provided")
            frames = [Frame(x, y, width, height)]

        added_frames: list[Frame] = []
        used_frames: list[Frame] = []
        frame_index = 0
        current_frame = frames[frame_index]
        cursor_y = current_frame.y
        remaining_height = current_frame.height
        used_height = 0.0

        def advance_frame() -> bool:
            nonlocal frame_index, current_frame, cursor_y, remaining_height
            nonlocal used_height
            if used_height > 0:
                used_frames.append(Frame(current_frame.x, current_frame.y, current_frame.width, used_height))
            frame_index += 1
            if frame_index >= len(frames):
                return False
            current_frame = frames[frame_index]
            cursor_y = current_frame.y
            remaining_height = current_frame.height
            used_height = 0.0
            return True

        prev_suspend = self._suspend_recording
        self._suspend_recording = True
        try:
            for text in paragraphs:
                frame = self.get_paragraph_frame(
                    text,
                    x=current_frame.x,
                    y=cursor_y,
                    width=current_frame.width,
                    font_size=font_size,
                    font_color=font_color,
                    bold=bold,
                    preserve_newlines=preserve_newlines,
                )
                needed = frame.height
                if needed > remaining_height:
                    if not advance_frame():
                        break
                    frame = self.get_paragraph_frame(
                        text,
                        x=current_frame.x,
                        y=cursor_y,
                        width=current_frame.width,
                        font_size=font_size,
                        font_color=font_color,
                        bold=bold,
                        preserve_newlines=preserve_newlines,
                    )
                    needed = frame.height
                    if needed > remaining_height:
                        break
                drawn = self.add_paragraph(
                    text,
                    x=current_frame.x,
                    y=cursor_y,
                    width=current_frame.width,
                    font_size=font_size,
                    font_color=font_color,
                    bold=bold,
                    preserve_newlines=preserve_newlines,
                )
                added_frames.append(drawn)
                cursor_y -= needed + gap
                remaining_height -= needed + gap
                used_height += needed + gap
        finally:
            self._suspend_recording = prev_suspend
        if used_height > 0:
            used_frames.append(Frame(current_frame.x, current_frame.y, current_frame.width, used_height))
        if used_frames:
            self._set_last_frame(used_frames[-1])
        return used_frames

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
        if self._has_rich_tags(normalized_text):
            height = self._measure_wrapped_rich_text(normalized_text, width, style)
        else:
            height = self._measure_wrapped_text(normalized_text, width, style)
        return Frame(x, y, width, height)

    def add_badge(
        self,
        title: str,
        description: str,
        level: str,
        x: float,
        y: float,
        width: float,
    ) -> Frame:
        level_key = level.strip().lower()
        if level_key not in ("error", "warning", "info"):
            raise ValueError("level must be one of: Error, Warning, Info")

        if level_key == "error":
            bg_color = colors.HexColor("#F8D7DA")
            stroke_color = colors.HexColor("#B02A37")
            text_color = colors.HexColor("#5B151A")
        elif level_key == "warning":
            bg_color = colors.HexColor("#FFF3CD")
            stroke_color = colors.HexColor("#D39E00")
            text_color = colors.HexColor("#5C3A00")
        else:
            bg_color = colors.HexColor("#E7F1FF")
            stroke_color = colors.HexColor("#2F6FCC")
            text_color = colors.HexColor("#1C3F75")

        inner_pad_x = 14
        inner_pad_y = 12
        title_frame = self.get_paragraph_frame(
            title,
            x + inner_pad_x,
            y - inner_pad_y,
            width - 2 * inner_pad_x,
            font_size=22,
            font_color=text_color,
            bold=True,
        )
        description_frame = self.get_paragraph_frame(
            description,
            x + inner_pad_x,
            title_frame.y - title_frame.height - 6,
            width - 2 * inner_pad_x,
            font_size=14,
            font_color=text_color,
        )

        total_height = inner_pad_y + title_frame.height + 6 + description_frame.height + inner_pad_y
        badge_frame = Frame(x, y, width, total_height)
        self.add_rectangle(
            x=badge_frame.x,
            y=badge_frame.y,
            width=badge_frame.width,
            height=badge_frame.height,
            fill_color=bg_color,
            stroke_color=stroke_color,
            stroke_width=0.5,
        )
        self.add_paragraph(
            title,
            x=title_frame.x,
            y=title_frame.y,
            width=title_frame.width,
            font_size=22,
            font_color=text_color,
            bold=True,
        )
        self.add_paragraph(
            description,
            x=description_frame.x,
            y=description_frame.y,
            width=description_frame.width,
            font_size=14,
            font_color=text_color,
        )
        self._set_last_frame(badge_frame)
        return badge_frame

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
        self._record_op(
            "add_table",
            data,
            x,
            y,
            width,
            header_rows=header_rows,
            zebra=zebra,
            col_widths=col_widths,
            col_align=col_align,
        )
        if not data:
            frame = Frame(x, y, width, 0)
            self._maybe_draw_debug(frame)
            self._set_last_frame(frame)
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
            elif zebra:
                fill_color = self.table_zebra_odd_bg if row_idx % 2 == 1 else self.table_zebra_even_bg
                self._canvas.setFillColor(fill_color)
                self._canvas.rect(x, row_y, width, row_height, fill=1, stroke=0)

            col_x = x
            for col_idx, cell_lines in enumerate(row):
                style = self.table_header_style if row_idx < header_rows else self.table_style
                self._canvas.setFont(style.font_name, style.font_size)
                self._canvas.setFillColor(style.color)
                text_block_height = len(cell_lines) * style.leading
                text_y = row_y + (row_height + text_block_height) / 2 - 0.8*style.leading
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
        self._set_last_frame(frame)
        return frame

    def get_table_frame(
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
            return Frame(x, y, width, 0)

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

        row_heights: list[float] = []
        wrapped_rows: list[list[list[str]]] = []
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
        return Frame(x, y, width, table_height)

    def set_table_style(
        self,
        header_style: TextStyle | None = None,
        body_style: TextStyle | None = None,
        header_background: colors.Color | None = None,
        grid_color: colors.Color | None = None,
        zebra_background: colors.Color | None = None,
        zebra_even_background: colors.Color | None = None,
    ) -> None:
        self._record_op(
            "set_table_style",
            header_style=header_style,
            body_style=body_style,
            header_background=header_background,
            grid_color=grid_color,
            zebra_background=zebra_background,
            zebra_even_background=zebra_even_background,
        )
        if header_style is not None:
            self.table_header_style = header_style
        if body_style is not None:
            self.table_style = body_style
        if header_background is not None:
            self.table_header_bg = header_background
        if grid_color is not None:
            self.table_grid = grid_color
        if zebra_background is not None:
            self.table_zebra_odd_bg = zebra_background
        if zebra_even_background is not None:
            self.table_zebra_even_bg = zebra_even_background

    def reset_table_style(self) -> None:
        self._record_op("reset_table_style")
        self._reset_table_styles()

    def add_plot(
        self,
        path: str,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
    ) -> Frame:
        self._record_op(
            "add_plot",
            path,
            x,
            y,
            width=width,
            height=height,
        )
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
            self._canvas.translate(frame.x, frame.y - draw_height)
            self._canvas.scale(scale_x, scale_y)
            self._canvas.doForm(rl_obj)
            self._canvas.restoreState()
        else:
            img = ImageReader(path)
            width_px, height_px = img.getSize()
            self._canvas.drawImage(
                img,
                frame.x,
                frame.y - draw_height,
                width=draw_width,
                height=draw_height,
                preserveAspectRatio=True,
                mask="auto",
            )

        self._maybe_draw_debug(frame)
        self._set_last_frame(frame)
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
        return self._resolve_plot_frame(src_width, src_height, x, y, width, height)

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
        self._record_op(
            "add_rectangle",
            x,
            y,
            width,
            height,
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )
        self._canvas.setFillColor(fill_color)
        if stroke_color is None:
            self._canvas.rect(x, y - height, width, height, fill=1, stroke=0)
            frame = Frame(x, y, width, height)
            self._maybe_draw_debug(frame)
            self._set_last_frame(frame)
            return frame
        self._canvas.setStrokeColor(stroke_color)
        self._canvas.setLineWidth(stroke_width)
        self._canvas.rect(x, y - height, width, height, fill=1, stroke=1)
        frame = Frame(x, y, width, height)
        self._maybe_draw_debug(frame)
        self._set_last_frame(frame)
        return frame

    def save(self) -> None:
        self._canvas.save()

    def build(self, multibuild: bool = True) -> None:
        if not multibuild or not self._ops:
            self.save()
            return

        ops = list(self._ops)

        self._canvas = canvas.Canvas(io.BytesIO(), pagesize=self.page_size)
        self._page_number = 0
        self._toc_entries = []
        self._toc_snapshot = None
        self._reset_table_styles()
        self._replay_ops(ops)
        toc_snapshot = list(self._toc_entries)

        self._canvas = canvas.Canvas(self.output_path, pagesize=self.page_size)
        self._page_number = 0
        self._toc_entries = []
        self._toc_snapshot = toc_snapshot
        self._reset_table_styles()
        self._replay_ops(ops)
        self.save()

    def get_toc_entries(self) -> list[TocEntry]:
        return list(self._toc_entries)

    def add_table_of_contents(
        self,
        x: float | None = None,
        y: float | None = None,
        width: float | None = None,
        title: str = "Table of Contents",
        frames: Sequence[Frame] | None = None,
        dot_leader: bool = False,
    ) -> Frame:
        self._record_op(
            "add_table_of_contents",
            x,
            y,
            width,
            title=title,
            frames=frames,
            dot_leader=dot_leader,
        )
        toc_entries = self._toc_snapshot if self._toc_snapshot is not None else self._toc_entries
        if not toc_entries:
            fallback_x = 0 if x is None else x
            fallback_y = 0 if y is None else y
            fallback_w = 0 if width is None else width
            frame = Frame(fallback_x, fallback_y, fallback_w, 0)
            self._maybe_draw_debug(frame)
            self._set_last_frame(frame)
            return frame

        if frames is None:
            if x is None or y is None or width is None:
                raise ValueError("x, y, and width are required when frames is not provided")
            frames = [Frame(x, y, width, 0)]

        frame_index = 0
        current_frame = frames[frame_index]
        current_x = current_frame.x
        current_y = current_frame.y
        current_width = current_frame.width
        remaining_height = current_frame.height if current_frame.height > 0 else None

        def advance_frame() -> bool:
            nonlocal frame_index, current_frame, current_x, current_y, current_width, remaining_height
            frame_index += 1
            if frame_index >= len(frames):
                return False
            current_frame = frames[frame_index]
            current_x = current_frame.x
            current_y = current_frame.y
            current_width = current_frame.width
            remaining_height = current_frame.height if current_frame.height > 0 else None
            return True

        title_height = self._measure_wrapped_text(title, current_width, self.section_style)
        if remaining_height is not None and title_height + 6 > remaining_height:
            if not advance_frame():
                frame = Frame(frames[0].x, frames[0].y, frames[0].width, 0)
                self._maybe_draw_debug(frame)
                self._set_last_frame(frame)
                return frame

        used_height_first = 0.0
        used_height = self._draw_wrapped_text(title, current_x, current_y, current_width, self.section_style)
        if frame_index == 0:
            used_height_first += used_height
        cursor_y = current_y - used_height - 6
        if remaining_height is not None:
            remaining_height = remaining_height - used_height - 6

        for entry in toc_entries:
            indent = entry.level * 18
            label = entry.text
            page_text = str(entry.page_number)
            text_width = current_width - indent - 28
            line_height = self.paragraph_style.leading
            lines = simpleSplit(label, self.paragraph_style.font_name, self.paragraph_style.font_size, text_width)
            last_line_y = None
            for line in lines:
                if remaining_height is not None and line_height > remaining_height:
                    if not advance_frame():
                        frame = Frame(frames[0].x, frames[0].y, frames[0].width, used_height_first)
                        self._maybe_draw_debug(frame)
                        self._set_last_frame(frame)
                        return frame
                    cursor_y = current_y
                    remaining_height = current_frame.height if current_frame.height > 0 else None
                    text_width = current_width - indent - 28
                self._canvas.setFont(self.paragraph_style.font_name, self.paragraph_style.font_size)
                self._canvas.setFillColor(self.paragraph_style.color)
                text_y = cursor_y - line_height
                last_line_y = text_y
                self._canvas.drawString(current_x + indent, text_y, line)
                if entry.anchor:
                    line_right = current_x + current_width
                    self._canvas.linkRect(
                        "",
                        entry.anchor,
                        Rect=(current_x + indent, text_y - 2, line_right, text_y + line_height - 2),
                        relative=1,
                        thickness=0,
                        color=None,
                    )
                cursor_y -= line_height
                if frame_index == 0:
                    used_height_first += line_height
                if remaining_height is not None:
                    remaining_height -= line_height
            if remaining_height is not None and 4 > remaining_height:
                if not advance_frame():
                    frame = Frame(frames[0].x, frames[0].y, frames[0].width, used_height_first)
                    self._maybe_draw_debug(frame)
                    self._set_last_frame(frame)
                    return frame
                cursor_y = current_y
                remaining_height = current_frame.height if current_frame.height > 0 else None
            page_y = last_line_y if last_line_y is not None else cursor_y - line_height
            if dot_leader:
                dots_start = current_x + indent
                dots_end = current_x + current_width - 6
                if last_line_y is not None:
                    label_width = stringWidth(
                        lines[-1],
                        self.paragraph_style.font_name,
                        self.paragraph_style.font_size,
                    )
                    dots_start = min(dots_end, current_x + indent + label_width + 6)
                if dots_end > dots_start:
                    dot_width = stringWidth(".", self.paragraph_style.font_name, self.paragraph_style.font_size)
                    dot_count = max(0, int((dots_end - dots_start) / dot_width))
                    if dot_count > 0:
                        self._canvas.drawString(dots_start, page_y, "." * dot_count)
            self._canvas.drawRightString(current_x + current_width, page_y, page_text)
            cursor_y -= 4
            if frame_index == 0:
                used_height_first += 4
            if remaining_height is not None:
                remaining_height -= 4

        frame = Frame(frames[0].x, frames[0].y, frames[0].width, used_height_first)
        self._maybe_draw_debug(frame)
        self._set_last_frame(frame)
        return frame

    def _draw_header(self, title: str, subtitle: str | None) -> None:
        page_width, page_height = self.page_size
        self._canvas.setFillColor(self.header_background)
        self._canvas.rect(0, page_height - self.header_height, page_width, self.header_height, fill=1, stroke=0)

        left_margin = 10
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

        self._canvas.setFont("Helvetica", 14)
        self._canvas.setFillColor(self.header_text)
        if self.serial_number:
            self._canvas.drawRightString(
                page_width - right_margin,
                header_mid + 2,
                f"{self.serial_number}",
            )
        self._canvas.setFont("Helvetica", 9)
        self._canvas.drawRightString(
            page_width - right_margin,
            header_mid - 14,
            f"Slide {self._page_number}",
        )

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

    def _has_rich_tags(self, text: str) -> bool:
        lowered = text.lower()
        return "<a" in lowered or "<b>" in lowered or "<em>" in lowered

    def _parse_rich_text(self, text: str) -> list[tuple[str, str | None, bool, bool]]:
        pattern = re.compile(r"(<a\s+href=['\"].*?['\"]>|</a>|<b>|</b>|<em>|</em>)", re.IGNORECASE)
        parts = pattern.split(text)
        segments: list[tuple[str, str | None, bool, bool]] = []
        href: str | None = None
        bold = False
        italic = False
        for part in parts:
            if not part:
                continue
            tag = part.lower()
            if tag.startswith("<a "):
                match = re.search(r"href=['\"](.*?)['\"]", part, re.IGNORECASE)
                href = match.group(1).strip() if match else None
            elif tag == "</a>":
                href = None
            elif tag == "<b>":
                bold = True
            elif tag == "</b>":
                bold = False
            elif tag == "<em>":
                italic = True
            elif tag == "</em>":
                italic = False
            else:
                segments.append((part, href, bold, italic))
        return segments

    def _wrap_segments(
        self,
        segments: list[tuple[str, str | None, bool, bool]],
        max_width: float,
        style: TextStyle,
    ) -> list[list[tuple[str, str | None, bool, bool]]]:
        lines: list[list[tuple[str, str | None, bool, bool]]] = []
        current_line: list[tuple[str, str | None, bool, bool]] = []
        current_width = 0.0

        def flush_line() -> None:
            nonlocal current_line, current_width
            lines.append(current_line)
            current_line = []
            current_width = 0.0

        for segment_text, href, bold, italic in segments:
            parts = segment_text.split("\n")
            for part_idx, part in enumerate(parts):
                tokens = re.findall(r"\S+|\s+", part)
                for token in tokens:
                    if token.isspace() and current_width == 0:
                        continue
                    token_font = self._resolve_font_name(style.font_name, bold, italic)
                    token_width = stringWidth(token, token_font, style.font_size)
                    if token.strip() and current_width + token_width > max_width and current_width > 0:
                        flush_line()
                    if token.isspace() and current_width + token_width > max_width:
                        continue
                    current_line.append((token, href, bold, italic))
                    current_width += token_width
                if part_idx < len(parts) - 1:
                    flush_line()
        if current_line or not lines:
            flush_line()
        return lines

    def _draw_wrapped_rich_text(
        self, text: str, x: float, y: float, width: float, style: TextStyle
    ) -> float:
        segments = self._parse_rich_text(text)
        lines = self._wrap_segments(segments, width, style)
        self._canvas.setFillColor(style.color)
        text_y = y - style.leading
        for line in lines:
            cursor_x = x
            for token, href, bold, italic in line:
                if token:
                    token_font = self._resolve_font_name(style.font_name, bold, italic)
                    self._canvas.setFont(token_font, style.font_size)
                    self._canvas.drawString(cursor_x, text_y, token)
                    token_width = stringWidth(token, token_font, style.font_size)
                    if href:
                        self._canvas.linkRect(
                            "",
                            href,
                            Rect=(cursor_x, text_y - 2, cursor_x + token_width, text_y + style.leading - 2),
                            relative=1,
                            thickness=0,
                            color=None,
                        )
                    cursor_x += token_width
            text_y -= style.leading
        return len(lines) * style.leading

    def _measure_wrapped_rich_text(self, text: str, width: float, style: TextStyle) -> float:
        segments = self._parse_rich_text(text)
        lines = self._wrap_segments(segments, width, style)
        return len(lines) * style.leading

    def _resolve_font_name(self, base_font: str, bold: bool, italic: bool) -> str:
        base = base_font
        if base.endswith("-BoldOblique"):
            base = base.replace("-BoldOblique", "")
        elif base.endswith("-Bold"):
            base = base.replace("-Bold", "")
        elif base.endswith("-Oblique"):
            base = base.replace("-Oblique", "")

        if bold and italic:
            return f"{base}-BoldOblique"
        if bold:
            return f"{base}-Bold"
        if italic:
            return f"{base}-Oblique"
        return base_font

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
        scale = min(width / src_width, height / src_height)
        return src_width * scale, src_height * scale

    def _resolve_plot_frame(
        self,
        src_width: float,
        src_height: float,
        x: float,
        y: float,
        width: float | None,
        height: float | None,
    ) -> Frame:
        draw_width, draw_height = self._resolve_plot_size(
            src_width, src_height, width, height
        )
        if width is None or height is None:
            return Frame(x, y, draw_width, draw_height)
        offset_x = (width - draw_width) / 2
        offset_y = (height - draw_height) / 2
        return Frame(x + offset_x, y - offset_y, draw_width, draw_height)

    def _reset_table_styles(self) -> None:
        self.table_header_bg = colors.HexColor("#2C3331")
        self.table_grid = colors.HexColor("#B5BCC3")
        self.table_zebra_odd_bg = colors.HexColor("#EDF2F6")
        self.table_zebra_even_bg = colors.white
        self.table_style = TextStyle("Helvetica", 10, 12, self.body_text)
        self.table_header_style = TextStyle("Helvetica-Bold", 10, 12, colors.HexColor("#F2F5F3"))

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

    def _record_op(self, name: str, *args, **kwargs) -> None:
        if self._suspend_recording:
            return
        self._ops.append((name, args, kwargs))

    def _replay_ops(self, ops: list[tuple[str, tuple, dict]]) -> None:
        self._suspend_recording = True
        for name, args, kwargs in ops:
            getattr(self, name)(*args, **kwargs)
        self._suspend_recording = False

    def _set_last_frame(self, frame: Frame) -> None:
        self.last_frame = frame

    def _maybe_draw_debug(self, frame: Frame) -> None:
        if not self.debug:
            return
        label = f"({frame.x:.1f}, {frame.y:.1f}, {frame.width:.1f}, {frame.height:.1f})"
        self._canvas.setFont(self.debug_style.font_name, self.debug_style.font_size)
        self._canvas.setFillColor(self.debug_style.color)
        self._canvas.drawString(frame.x + 2, frame.y - 2, label)
