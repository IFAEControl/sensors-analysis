from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List

from base_report.base_report_slides import BaseReportSlides, Frame

from ..helpers.data_holders import IssueEntry, ReportData, SanityCheckEntry
from ..report_elements.sanity_checks_slides import add_sanity_check_box, get_sanity_check_box_frame
from .base_section import BaseSection


SEVERITY_ORDER = {"error": 0, "warning": 1}
SCOPE_ORDER = {"charact": 0, "photodiode": 1, "fileset": 2, "run": 3, "other": 4}


@dataclass
class IssueItem:
    scope_key: str
    severity: str
    scope_group: str
    description: str
    meta: Dict


def _scope_group(scope_key: str) -> str:
    if scope_key == "charact":
        return "charact"
    parts = scope_key.split("_")
    if len(parts) == 2 and parts[0] == "PD":
        return "photodiode"
    if len(parts) == 4 and parts[0] == "PD":
        return "fileset"
    if len(parts) == 5 and parts[0] == "PD":
        return "run"
    return "other"


def _flatten_issues(issues: Dict[str, list[IssueEntry]]) -> List[IssueItem]:
    out: List[IssueItem] = []
    for scope_key, entries in issues.items():
        for entry in entries:
            sev = (entry.level or "").lower()
            if sev not in SEVERITY_ORDER:
                sev = "warning"
            out.append(
                IssueItem(
                    scope_key=scope_key,
                    severity=sev,
                    scope_group=_scope_group(scope_key),
                    description=entry.description or "",
                    meta=entry.meta or {},
                )
            )
    out.sort(
        key=lambda item: (
            SEVERITY_ORDER.get(item.severity, 99),
            SCOPE_ORDER.get(item.scope_group, 99),
            item.scope_key,
            item.description,
        )
    )
    return out


class IssuesSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2
        margin = 10
        self.col_width = (self.end_x - self.init_x - margin) / 2
        self.col_height = self.init_y - self.end_y
        self.frames = [
            Frame(self.init_x, self.init_y, self.col_width, self.col_height),
            Frame(self.init_x + self.col_width + margin, self.init_y, self.col_width, self.col_height),
        ]
        self.curr_height = self.init_y
        self.curr_frame_idx = 0
        self.sec_padding = 0

    def _build(self, depth: int) -> None:
        items = _flatten_issues(self.report_data.issues)
        if not items:
            return

        self.report.add_slide("Issues")
        self.report.add_section(
            "Issues",
            x=self.init_x,
            y=self.init_y,
            width=self.col_width,
            anchor="issues",
            toc=True,
        )
        self.curr_height = self.report.last_frame.y - self.report.last_frame.height - 10
        intro = (
            "Issues are internal hardcoded checks in the analysis software. "
            "As with sanity checks, they have different severity levels."
        )
        f = self.report.add_paragraph(
            intro,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            font_size=9.5,
        )
        self.curr_height = f.y - f.height - 8
        self._add_summary(items)

        by_sev_then_scope: Dict[str, Dict[str, List[IssueItem]]] = {}
        for item in items:
            by_sev_then_scope.setdefault(item.severity, {})
            by_sev_then_scope[item.severity].setdefault(item.scope_group, [])
            by_sev_then_scope[item.severity][item.scope_group].append(item)

        for sev in ("error", "warning"):
            scope_map = by_sev_then_scope.get(sev, {})
            if not scope_map:
                continue
            self._add_subsection(f"{sev.title()} Issues ({sum(len(v) for v in scope_map.values())})")
            for scope in ("charact", "photodiode", "fileset", "run", "other"):
                scoped_items = scope_map.get(scope, [])
                if not scoped_items:
                    continue
                self._add_subsubsection(f"{scope.title()} scope ({len(scoped_items)})")
                for item in scoped_items:
                    self._add_issue_box(item)

    def _add_summary(self, items: List[IssueItem]) -> None:
        num_errors = sum(1 for it in items if it.severity == "error")
        num_warnings = sum(1 for it in items if it.severity == "warning")
        msg = f"Total issues: {len(items)} | errors: {num_errors} | warnings: {num_warnings}"
        f = self.report.add_paragraph(
            msg,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            font_size=10.5,
            bold=True,
        )
        self.curr_height = f.y - f.height - 8

    def _switch_column_or_slide(self):
        if self.curr_frame_idx == 0:
            self.curr_frame_idx = 1
            self.curr_height = self.init_y
            self.sec_padding = 0
            return
        self.report.add_slide("Issues (cont.)")
        self.curr_frame_idx = 0
        self.curr_height = self.init_y
        self.sec_padding = 0

    def _add_subsection(self, title: str) -> None:
        if self.curr_height < 130:
            self._switch_column_or_slide()
        f = self.report.add_subsection(
            title,
            x=self.frames[self.curr_frame_idx].x,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width,
            toc=False,
        )
        self.curr_height = f.y - f.height - 6
        self.sec_padding = 0

    def _add_subsubsection(self, title: str) -> None:
        if self.curr_height < 110:
            self._switch_column_or_slide()
        f = self.report.add_subsubsection(
            title,
            x=self.frames[self.curr_frame_idx].x + self.sec_padding,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width - self.sec_padding,
            toc=False,
        )
        self.curr_height = f.y - f.height - 6
        self.sec_padding += 8

    def _add_issue_box(self, item: IssueItem) -> None:
        meta_text = json.dumps(item.meta, sort_keys=True, ensure_ascii=True)
        info_text = (
            f"[{item.scope_key}] {item.description}\n"
            f"meta: {meta_text}"
        )
        check = SanityCheckEntry(
            check_name=f"Issue ({item.scope_group})",
            check_args=None,
            passed=False,
            info=info_text,
            severity=item.severity,
            exec_error=False,
            internal=False,
            check_explanation="",
        )
        box_frame = get_sanity_check_box_frame(
            self.report,
            check,
            x=self.frames[self.curr_frame_idx].x + self.sec_padding,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width - self.sec_padding,
            simplified=True,
        )
        if box_frame.height > self.curr_height:
            self._switch_column_or_slide()
        rendered = add_sanity_check_box(
            self.report,
            check,
            x=self.frames[self.curr_frame_idx].x + self.sec_padding,
            y=self.curr_height,
            width=self.frames[self.curr_frame_idx].width - self.sec_padding,
            simplified=True,
        )
        self.curr_height = rendered.y - rendered.height - 8
