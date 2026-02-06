
from reportlab.lib import colors
from base_report.base_report_slides import BaseReportSlides, Frame
from ..helpers.data_holders import ReportData
from ..report_elements.sanity_checks_slides import add_sanity_check_box, get_sanity_check_box_frame
from .base_section import BaseSection


class SanityChecksSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2
        margin = 10
        self.sec_padding = 0
        self.col_width = (self.end_x - self.init_x - margin) / 2
        self.col_height = (self.init_y - self.end_y)
        self.frames = [
            Frame(self.init_x, self.init_y, self.col_width, self.col_height),
            Frame(self.init_x + self.col_width + margin, self.init_y, self.col_width, self.col_height)
        ]
        self.curr_height = self.init_y
        self.curr_frame_idx = 0

    def _update_height(self):
        self.curr_height -= self.lf.height + 10

    def _build(self, depth: int):
        """Build the sanity checks section of the report"""
        self.report.add_slide('Sanity Checks')
        self.report.add_section(
            'Sanity Checks', 
            x=self.init_x,
            y=self.init_y,
            width = self.col_width,
            anchor='sanity_checks')
        self._update_height()
        
        # Further sanity checks section building logic goes here
        self.add_sanity_checks(depth)
    
    def _add_sanity_check_box(self, check: SanityCheckEntry):
        f = get_sanity_check_box_frame(
            self.report,
            check,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            simplified=True
        )
        if f.height > self.curr_height:
            if self.curr_frame_idx == 0:
                self.report.add_paragraph(
                    "Continuing sanity checks in the right column.",
                    x=self.frames[0].x + self.sec_padding,
                    y=self.curr_height,
                    width=self.frames[0].width,
                    font_color=colors.HexColor("#9F9F9F"),
                    font_size=9,
                )
                self.curr_frame_idx = 1
                self.curr_height = self.init_y
            else:
                f = self.report.add_paragraph(
                    "Continuing sanity checks in next slide",
                    x=self.frames[1].x + self.sec_padding,
                    y=self.curr_height,
                    width=self.frames[1].width,
                    font_color=colors.HexColor("#9F9F9F"),
                    font_size=9,
                )
                self.report.add_slide('Sanity Checks (cont.)', '')
                self.curr_frame_idx = 0
                self.curr_height = self.init_y
        f = add_sanity_check_box(self.report, check, 
                                    x=self.frames[self.curr_frame_idx].x + self.sec_padding, 
                                    y=self.curr_height, 
                                    width=self.frames[self.curr_frame_idx].width - self.sec_padding,
                                    simplified=True
                                    )
        self.curr_height = f.y - f.height - 10

    def _add_subsection(self, title: str, anchor: str):
        if self.curr_height < 130:
            if self.curr_frame_idx == 0:
                self.curr_frame_idx = 1
                self.curr_height = self.init_y
            else:
                self.report.add_slide('Sanity Checks (cont.)')
                self.curr_frame_idx = 0
                self.curr_height = self.init_y
        self.report.add_subsection(
            title,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            anchor=anchor
        )
        self._update_height()
        self.sec_padding = 0
    def _add_subsubsection(self, title: str, anchor: str):
        if self.curr_height < 100:
            if self.curr_frame_idx == 0:
                self.curr_frame_idx = 1
                self.curr_height = self.init_y
            else:
                self.report.add_slide('Sanity Checks (cont.)')
                self.curr_frame_idx = 0
                self.curr_height = self.init_y
        self.report.add_subsubsection(
            title,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            anchor=anchor
        )
        self._update_height()
        self.sec_padding += 10


    def add_sanity_checks(self, depth: int):
        """Add a subsection for sanity checks"""
        self._add_subsection(
            "Calibration Level Sanity Checks", 
            anchor = 'calib_level_sanity_checks')
        for name, check in self.report_data.sanity_checks.calibration_checks.items():
            self._add_sanity_check_box(check)
        if depth == 0 or depth >=2:
            self._add_subsection(f"FileSet Level Sanity Checks", 'fileset_level_sanity_checks')
            for fs_name, fs_checks in self.report_data.sanity_checks.fileset_checks.items():
                self._add_subsubsection(f"FileSet {fs_name}", anchor=f'fileset_{fs_name}_sanity_checks')
                for name, check in fs_checks.items():
                    self._add_sanity_check_box(check)
        
        if depth == 0 or depth >=3:
            self._add_subsection(f"File Level Sanity Checks", 'file_level_sanity_checks')
            for file_name, file_checks in self.report_data.sanity_checks.file_checks.items():
                self._add_subsubsection(f"File {file_name}", anchor=f'file_{file_name}_sanity_checks')
                for name, check in file_checks.items():
                    self._add_sanity_check_box(check)

