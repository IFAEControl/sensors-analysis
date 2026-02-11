
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
        has_failed = self._has_failed_checks(depth)
        has_defined = self._has_defined_checks()
        if not has_failed and not has_defined:
            return
        if has_failed:
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
        if has_defined:
            self.checks_defined()

    def _has_failed_checks(self, depth: int) -> bool:
        if any(check.passed is False for check in self.report_data.sanity_checks.calibration_checks.values()):
            return True
        if depth == 0 or depth >= 2:
            for fs_checks in self.report_data.sanity_checks.fileset_checks.values():
                if any(check.passed is False for check in fs_checks.values()):
                    return True
        if depth == 0 or depth >= 3:
            for file_checks in self.report_data.sanity_checks.file_checks.values():
                if any(check.passed is False for check in file_checks.values()):
                    return True
        return False

    def _has_defined_checks(self) -> bool:
        defined = self.report_data.sanity_checks.defined_checks
        if defined is None:
            return False
        return bool(
            defined.calibration_checks
            or defined.fileset_checks
            or defined.file_checks
        )
    
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
        calib_failed = [
            check for check in self.report_data.sanity_checks.calibration_checks.values()
            if check.passed is False
        ]
        if calib_failed:
            self._add_subsection("Calibration Level Sanity Checks", anchor='calib_level_sanity_checks')
            for check in calib_failed:
                self._add_sanity_check_box(check)

        if depth == 0 or depth >=2:
            fileset_failed = {
                fs_name: [check for check in fs_checks.values() if check.passed is False]
                for fs_name, fs_checks in self.report_data.sanity_checks.fileset_checks.items()
            }
            fileset_failed = {fs_name: checks for fs_name, checks in fileset_failed.items() if checks}
            if fileset_failed:
                self._add_subsection("FileSet Level Sanity Checks", 'fileset_level_sanity_checks')
                for fs_name, failed_checks in fileset_failed.items():
                    self._add_subsubsection(f"FileSet {fs_name}", anchor=f'fileset_{fs_name}_sanity_checks')
                    for check in failed_checks:
                        self._add_sanity_check_box(check)
        
        if depth == 0 or depth >=3:
            file_failed = {
                file_name: [check for check in file_checks.values() if check.passed is False]
                for file_name, file_checks in self.report_data.sanity_checks.file_checks.items()
            }
            file_failed = {file_name: checks for file_name, checks in file_failed.items() if checks}
            if file_failed:
                self._add_subsection("File Level Sanity Checks", 'file_level_sanity_checks')
                for file_name, failed_checks in file_failed.items():
                    self._add_subsubsection(f"File {file_name}", anchor=f'file_{file_name}_sanity_checks')
                    for check in failed_checks:
                        self._add_sanity_check_box(check)

    def checks_defined(self):
        """Add a slide with all configured sanity checks from SanityChecksDefined."""
        defined = self.report_data.sanity_checks.defined_checks
        if defined is None:
            return

        groups = [
            ("Calibration", defined.calibration_checks),
            ("FileSet", defined.fileset_checks),
            ("File", defined.file_checks),
        ]
        if not any(checks for _, checks in groups):
            return

        self.report.add_slide('Defined Sanity Checks')
        sec = self.report.add_section(
            'Defined Sanity Checks',
            x=self.init_x,
            y=self.init_y,
            width=self.col_width,
            anchor='defined_sanity_checks'
        )

        col_idx = 0
        curr_y = sec.y - sec.height - 10
        min_y = self.end_y + 20

        def next_column_or_slide():
            nonlocal col_idx, curr_y
            if col_idx == 0:
                col_idx = 1
                curr_y = self.init_y
            else:
                self.report.add_slide('Defined Sanity Checks (cont.)', '')
                col_idx = 0
                curr_y = self.init_y

        def ensure_space(min_height: float):
            nonlocal curr_y
            if curr_y - min_height < min_y:
                next_column_or_slide()

        def add_subsub(title: str):
            nonlocal curr_y
            ensure_space(40)
            f = self.report.add_subsubsection(
                title,
                x=self.frames[col_idx].x,
                y=curr_y,
                width=self.frames[col_idx].width,
                toc=False,
            )
            curr_y = f.y - f.height - 8

        def add_text(text: str, bold: bool = False):
            nonlocal curr_y
            ensure_space(28)
            f = self.report.add_paragraph(
                text,
                x=self.frames[col_idx].x + 8,
                y=curr_y,
                width=self.frames[col_idx].width - 8,
                font_size=9.5,
                bold=bold,
            )
            curr_y = f.y - f.height - 6

        for group_title, checks in groups:
            add_subsub(group_title)
            if not checks:
                add_text("No defined checks.")
                continue
            for check_key, check_data in checks.items():
                sev = check_data.severity or "n/a"
                add_text(f"{check_key} [{sev}]", bold=True)
                if check_data.check_explanation:
                    add_text(check_data.check_explanation)
