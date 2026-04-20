from __future__ import annotations

from collections import defaultdict

from ..helpers import (
    load_deviation_ranking_rows,
    load_final_calification_rows,
)
from .base_section import BaseSection


COMBOS = ("532_G1", "532_G2", "1064_G1", "1064_G2")
WAVELENGTHS = ("532", "1064")


def _fmt_pct(value: str | None) -> str:
    if value is None or value == "":
        return "-"
    try:
        return f"{float(value):.3f}%"
    except (TypeError, ValueError):
        return str(value)


class PlotsSection(BaseSection):
    def __init__(self, summary_data: dict, report, root_path: str) -> None:
        super().__init__(summary_data, report)
        self.section_depth = 2
        self.root_path = root_path
        self.final_rows = load_final_calification_rows(summary_data, root_path)
        self.deviation_rows = load_deviation_ranking_rows(summary_data, root_path)
        self.deviation_by_combo = self._group_deviation_rows(self.deviation_rows)

    def _build(self, depth: int) -> None:
        if not self.final_rows:
            return
        self._build_heatmap_slide()
        for wavelength in WAVELENGTHS:
            self._build_a2p_wavelength_overview_slide(wavelength)
        for combo in COMBOS:
            self._build_a2p_combo_detail_slide(combo)
        for combo in COMBOS:
            self._build_a2p_combo_diagnostic_slide(combo)
        self._build_a2v_summary_slide()

    def _build_heatmap_slide(self) -> None:
        self.report.add_slide("Crossboard Report", "Global outlier map")
        self.report.add_section(
            "Global A2P Outlier Map",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="global_a2p_outlier_map",
            toc=False,
        )
        intro = self.report.add_paragraph(
            "This heatmap shows board-level robust z-scores of mean A2P slope by wavelength and gain combination. "
            "Large absolute color indicates a board sits far from the population median for that combination.",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 10,
            width=self.end_x - self.init_x,
            font_size=10.2,
        )

        left_w = 620
        gap = 16
        plot_y = intro.y - intro.height - 10
        self.add_plot_from_summary(
            "a2p_robust_zscore_heatmap",
            self.root_path,
            x=self.init_x,
            y=plot_y,
            width=left_w,
            height=300,
        )

        right_x = self.init_x + left_w + gap
        right_w = self.end_x - right_x
        facts = self._top_overall_boards(3)
        y = plot_y
        title = self.report.add_subsection("Key Facts", x=right_x, y=y, width=right_w, toc=False)
        y = title.y - title.height - 8
        for line in [
            "Rows are boards and columns are the four A2P combinations used for ranking.",
            "Boards with repeated strong color across columns are likely to rank poorly overall.",
            "The weighted final calification gives more importance to 1064 than 532.",
            "Top boards by final calification:",
            *facts,
        ]:
            frame = self.report.add_paragraph(line, x=right_x, y=y, width=right_w, font_size=9.8)
            y = frame.y - frame.height - 5

    def _build_a2p_wavelength_overview_slide(self, wavelength: str) -> None:
        self.report.add_slide("Crossboard Report", f"A2P overview {wavelength}")
        self.report.add_section(
            f"A2P Population Overview {wavelength}",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor=f"a2p_population_overview_{wavelength}",
            toc=False,
        )
        intro = self.report.add_paragraph(
            f"These plots show how boards cluster in slope-intercept space for wavelength {wavelength}. "
            "They are useful for spotting separated populations and broad outliers before looking at combo-level diagnostics.",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 10,
            width=self.end_x - self.init_x,
            font_size=10.2,
        )
        plot_y = intro.y - intro.height - 10
        self.add_plot_from_summary(
            f"a2p_slope_vs_intercept_{wavelength}",
            self.root_path,
            x=self.init_x,
            y=plot_y,
            width=650,
            height=330,
        )

        notes_x = self.init_x + 666
        notes_w = self.end_x - notes_x
        title = self.report.add_subsection("Interpretation", x=notes_x, y=plot_y, width=notes_w, toc=False)
        y = title.y - title.height - 8
        lines = [
            "Look for boards that sit away from the main cloud or show unusual intercept-slope correlation.",
            "This view is wavelength-wide, so gain-specific effects can still be hidden inside the cloud.",
            f"Relevant combo rankings for {wavelength}:",
            *self._combo_summary_lines(prefix=f"{wavelength}_"),
        ]
        for line in lines:
            frame = self.report.add_paragraph(line, x=notes_x, y=y, width=notes_w, font_size=9.6)
            y = frame.y - frame.height - 5

    def _build_a2p_combo_detail_slide(self, combo: str) -> None:
        wavelength, gain = combo.split("_", 1)
        self.report.add_slide("Crossboard Report", f"A2P combo detail {combo}")
        self.report.add_section(
            f"A2P Combo Detail {combo}",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor=f"a2p_combo_detail_{combo}",
            toc=False,
        )
        intro = self.report.add_paragraph(
            "The scatter plot shows board separation in slope-intercept space for this exact combination, "
            "while the histogram gives the population spread of slope and intercept.",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 10,
            width=self.end_x - self.init_x,
            font_size=10.0,
        )
        plot_y = intro.y - intro.height - 10
        self.add_plot_from_summary(
            f"a2p_slope_vs_intercept_{combo}",
            self.root_path,
            x=self.init_x,
            y=plot_y,
            width=560,
            height=300,
        )
        self.add_plot_from_summary(
            f"a2p_histograms_{combo}",
            self.root_path,
            x=self.init_x + 576,
            y=plot_y,
            width=348,
            height=300,
        )
        y = plot_y - 312
        title = self.report.add_subsection("Most deviating boards", x=self.init_x, y=y, width=self.end_x - self.init_x, toc=False)
        y = title.y - title.height - 6
        for line in self._top_combo_lines(combo, top_n=3):
            frame = self.report.add_paragraph(line, x=self.init_x, y=y, width=self.end_x - self.init_x, font_size=9.8)
            y = frame.y - frame.height - 4

    def _build_a2p_combo_diagnostic_slide(self, combo: str) -> None:
        wavelength, gain = combo.split("_", 1)
        self.report.add_slide("Crossboard Report", f"A2P diagnostics {combo}")
        self.report.add_section(
            f"A2P Deviation Diagnostics {combo}",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor=f"a2p_deviation_diagnostics_{combo}",
            toc=False,
        )
        intro = self.report.add_paragraph(
            "These board-grids show per-photodiode behavior against the combo median. "
            "Use them to understand why a board looks abnormal in the ranking.",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 10,
            width=self.end_x - self.init_x,
            font_size=10.0,
        )
        plot_y = intro.y - intro.height - 10
        self.add_plot_from_summary(
            f"a2p_slope_median_std_by_board_{combo}",
            self.root_path,
            x=self.init_x,
            y=plot_y,
            width=454,
            height=320,
        )
        self.add_plot_from_summary(
            f"a2p_slope_pct_diff_median_std_by_board_{combo}",
            self.root_path,
            x=self.init_x + 470,
            y=plot_y,
            width=454,
            height=320,
        )
        y = plot_y - 332
        note = (
            "Left: absolute slope position versus the combo median and P75 band. "
            "Right: signed percent difference from median, useful to distinguish positive and negative drift."
        )
        self.report.add_paragraph(note, x=self.init_x, y=y, width=self.end_x - self.init_x, font_size=9.6)

    def _build_a2v_summary_slide(self) -> None:
        self.report.add_slide("Crossboard Report", "A2V summary")
        self.report.add_section(
            "A2V Reference Overview",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="a2v_reference_overview",
            toc=False,
        )
        intro = self.report.add_paragraph(
            "A2V plots are included as supporting reference. The board ranking itself is built from A2P, "
            "so this section is mainly for cross-checking whether similar population structure appears in voltage space.",
            x=self.init_x,
            y=self.lf.y - self.lf.height - 10,
            width=self.end_x - self.init_x,
            font_size=10.0,
        )
        plot_y = intro.y - intro.height - 10
        self.add_plot_from_summary(
            "a2v_slope_vs_intercept_532",
            self.root_path,
            x=self.init_x,
            y=plot_y,
            width=454,
            height=300,
        )
        self.add_plot_from_summary(
            "a2v_slope_vs_intercept_1064",
            self.root_path,
            x=self.init_x + 470,
            y=plot_y,
            width=454,
            height=300,
        )
        y = plot_y - 312
        for line in [
            "A2V can help confirm whether a board is globally unusual or only problematic in the ADC-to-power conversion.",
            "If an outlier appears strongly in A2P but not in A2V, that points to the power-conversion path rather than the raw reference-voltage fit.",
        ]:
            frame = self.report.add_paragraph(line, x=self.init_x, y=y, width=self.end_x - self.init_x, font_size=9.6)
            y = frame.y - frame.height - 5

    @staticmethod
    def _group_deviation_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            grouped[str(row.get("combo", ""))].append(row)
        for combo in grouped:
            grouped[combo].sort(key=lambda row: float(row.get("abs_dev_pct", "inf")), reverse=True)
        return grouped

    def _top_overall_boards(self, n: int) -> list[str]:
        rows = sorted(self.final_rows, key=lambda row: int(row.get("rank", "999999")))[:n]
        return [
            f"{row.get('rank', '-')}. {row.get('board_id', '')} ({_fmt_pct(row.get('average_abs_dev_pct'))})"
            for row in rows
        ]

    def _top_combo_lines(self, combo: str, top_n: int) -> list[str]:
        rows = self.deviation_by_combo.get(combo, [])[:top_n]
        if not rows:
            return [f"No deviation ranking rows found for {combo}."]
        return [
            f"{idx}. {row.get('board_id', '')} | abs dev {_fmt_pct(row.get('abs_dev_pct'))} | mean slope {row.get('board_mean_slope', '-')}"
            for idx, row in enumerate(rows, start=1)
        ]

    def _combo_summary_lines(self, prefix: str) -> list[str]:
        lines: list[str] = []
        for combo in COMBOS:
            if not combo.startswith(prefix):
                continue
            top = self.deviation_by_combo.get(combo, [])
            if not top:
                continue
            row = top[0]
            lines.append(
                f"{combo}: worst current deviation is {row.get('board_id', '')} at {_fmt_pct(row.get('abs_dev_pct'))}"
            )
        return lines
