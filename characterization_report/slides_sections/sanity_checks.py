from __future__ import annotations

import re

from reportlab.lib import colors

from base_report.base_report_slides import BaseReportSlides, Frame

from ..helpers.data_holders import ReportData, SanityCheckEntry
from ..report_elements.sanity_checks_slides import add_sanity_check_box, get_sanity_check_box_frame
from .base_section import BaseSection


def _anchor_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower()
    return slug or "sanity"


class SanityChecksSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2
        margin = 10
        self.sec_padding = 0
        self.col_width = (self.end_x - self.init_x - margin) / 2
        self.col_height = self.init_y - self.end_y
        self.frames = [
            Frame(self.init_x, self.init_y, self.col_width, self.col_height),
            Frame(self.init_x + self.col_width + margin, self.init_y, self.col_width, self.col_height),
        ]
        self.curr_height = self.init_y
        self.curr_frame_idx = 0

    def _update_height(self) -> None:
        self.curr_height -= self.lf.height + 10

    def _build(self, depth: int) -> None:
        has_failed = self._has_failed_checks(depth)
        has_defined = self._has_defined_checks()
        if not has_failed and not has_defined:
            return
        if has_failed:
            self.report.add_slide("Sanity Checks")
            self.report.add_section(
                "Sanity Checks",
                x=self.init_x,
                y=self.init_y,
                width=self.col_width,
                anchor="sanity_checks",
            )
            self._update_height()
            self.add_sanity_checks(depth)
        if has_defined:
            self.checks_defined()

    def _has_failed_checks(self, depth: int) -> bool:
        for run in self.report_data.sanity_checks.runs.values():
            if any(check.passed is False for check in run.checks.values()):
                return True
            if depth == 0 or depth >= 2:
                for fs in run.filesets.values():
                    if any(check.passed is False for check in fs.checks.values()):
                        return True
            if depth == 0 or depth >= 3:
                for fs in run.filesets.values():
                    for file_checks in fs.sweepfiles.values():
                        if any(check.passed is False for check in file_checks.values()):
                            return True
        return False

    def _has_defined_checks(self) -> bool:
        defined = self.report_data.sanity_checks.defined_checks
        if defined is None:
            return False
        return bool(
            defined.characterization_checks
            or defined.fileset_checks
            or defined.sweepfile_checks
        )

    def _add_sanity_check_box(self, check: SanityCheckEntry) -> None:
        f = get_sanity_check_box_frame(
            self.report,
            check,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            simplified=True,
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
                self.report.add_paragraph(
                    "Continuing sanity checks in next slide",
                    x=self.frames[1].x + self.sec_padding,
                    y=self.curr_height,
                    width=self.frames[1].width,
                    font_color=colors.HexColor("#9F9F9F"),
                    font_size=9,
                )
                self.report.add_slide("Sanity Checks (cont.)", "")
                self.curr_frame_idx = 0
                self.curr_height = self.init_y

        f = add_sanity_check_box(
            self.report,
            check,
            x=self.frames[self.curr_frame_idx].x + self.sec_padding,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width - self.sec_padding,
            simplified=True,
        )
        self.curr_height = f.y - f.height - 10

    def _add_subsection(self, title: str, anchor: str) -> None:
        if self.curr_height < 130:
            if self.curr_frame_idx == 0:
                self.curr_frame_idx = 1
                self.curr_height = self.init_y
            else:
                self.report.add_slide("Sanity Checks (cont.)")
                self.curr_frame_idx = 0
                self.curr_height = self.init_y
        self.report.add_subsection(
            title,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            anchor=anchor,
            toc=False,
        )
        self._update_height()
        self.sec_padding = 0

    def _add_subsubsection(self, title: str, anchor: str) -> None:
        if self.curr_height < 100:
            if self.curr_frame_idx == 0:
                self.curr_frame_idx = 1
                self.curr_height = self.init_y
            else:
                self.report.add_slide("Sanity Checks (cont.)")
                self.curr_frame_idx = 0
                self.curr_height = self.init_y
        self.report.add_subsubsection(
            title,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            anchor=anchor,
            toc=False,
        )
        self._update_height()
        self.sec_padding += 10

    def add_sanity_checks(self, depth: int) -> None:
        for run_name in sorted(self.report_data.sanity_checks.runs.keys()):
            run = self.report_data.sanity_checks.runs[run_name]
            run_failed = [check for check in run.checks.values() if check.passed is False]
            fileset_failed = {
                fs_name: [check for check in fs_data.checks.values() if check.passed is False]
                for fs_name, fs_data in run.filesets.items()
            }
            fileset_failed = {fs_name: checks for fs_name, checks in fileset_failed.items() if checks}
            file_failed = {}
            for fs_name, fs_data in run.filesets.items():
                for file_name, file_checks in fs_data.sweepfiles.items():
                    failed_checks = [check for check in file_checks.values() if check.passed is False]
                    if failed_checks:
                        file_failed[f"{fs_name}:{file_name}"] = failed_checks

            include_filesets = (depth == 0 or depth >= 2) and bool(fileset_failed)
            include_files = (depth == 0 or depth >= 3) and bool(file_failed)
            if not run_failed and not include_filesets and not include_files:
                continue

            run_slug = _anchor_slug(run_name)
            self._add_subsection(f"Run {run_name}", anchor=f"sanity_run_{run_slug}")

            if run_failed:
                self._add_subsubsection(
                    "Characterization Level",
                    anchor=f"sanity_run_{run_slug}_characterization",
                )
                for check in run_failed:
                    self._add_sanity_check_box(check)

            if include_filesets:
                self._add_subsubsection(
                    "FileSet Level",
                    anchor=f"sanity_run_{run_slug}_filesets",
                )
                for fs_name, failed_checks in fileset_failed.items():
                    self._add_subsubsection(
                        f"FileSet {fs_name}",
                        anchor=f"sanity_run_{run_slug}_fileset_{_anchor_slug(fs_name)}",
                    )
                    for check in failed_checks:
                        self._add_sanity_check_box(check)

            if include_files:
                self._add_subsubsection(
                    "File Level",
                    anchor=f"sanity_run_{run_slug}_files",
                )
                for fs_file, failed_checks in file_failed.items():
                    self._add_subsubsection(
                        f"File {fs_file}",
                        anchor=f"sanity_run_{run_slug}_file_{_anchor_slug(fs_file)}",
                    )
                    for check in failed_checks:
                        self._add_sanity_check_box(check)

    def checks_defined(self) -> None:
        defined = self.report_data.sanity_checks.defined_checks
        if defined is None:
            return

        groups = [
            ("Characterization", defined.characterization_checks),
            ("FileSet", defined.fileset_checks),
            ("SweepFile", defined.sweepfile_checks),
        ]
        if not any(checks for _, checks in groups):
            return

        self.report.add_slide("Defined Sanity Checks")
        self.report.add_section(
            "Defined Sanity Checks",
            x=self.init_x,
            y=self.init_y,
            width=self.col_width,
            anchor="defined_sanity_checks",
            toc=False,
        )

        col_idx = 0
        curr_y = self.report.last_frame.y - self.report.last_frame.height - 10
        min_y = self.end_y + 20

        def next_column_or_slide() -> None:
            nonlocal col_idx, curr_y
            if col_idx == 0:
                col_idx = 1
                curr_y = self.init_y
            else:
                self.report.add_slide("Defined Sanity Checks (cont.)", "")
                col_idx = 0
                curr_y = self.init_y

        def ensure_space(min_height: float) -> None:
            nonlocal curr_y
            if curr_y - min_height < min_y:
                next_column_or_slide()

        def add_subsub(title: str) -> None:
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

        def add_text(text: str, bold: bool = False) -> None:
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
