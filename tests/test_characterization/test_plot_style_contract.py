from __future__ import annotations

import re
import unittest
from pathlib import Path

from characterization.elements.plots.plot_base import BasePlots
from characterization.elements.plots.style_spec import DEFAULT_MARKER, METRIC_STYLES


ROOT = Path(__file__).resolve().parents[2]
PLOTS_DIR = ROOT / "characterization" / "elements" / "plots"


class _DummyPlot(BasePlots):
    @property
    def output_path(self) -> str:
        return "."

    def generate_plots(self):
        return None


class TestPlotStyleContract(unittest.TestCase):
    def test_metric_styles_have_default_marker(self):
        self.assertTrue(METRIC_STYLES, "METRIC_STYLES should not be empty")
        for metric, style in METRIC_STYLES.items():
            self.assertEqual(
                style.get("marker"),
                DEFAULT_MARKER,
                f"Metric '{metric}' should use default marker '{DEFAULT_MARKER}'",
            )

    def test_series_marker_cycle_provides_distinct_markers(self):
        dummy = _DummyPlot()
        markers = [dummy._series_marker(i) for i in range(8)]
        self.assertEqual(len(set(markers[:4])), 4)
        self.assertIn("o", markers)
        self.assertIn("x", markers)
        self.assertIn("s", markers)

    def test_no_hardcoded_hex_colors_outside_style_spec(self):
        hex_re = re.compile(r"#[0-9A-Fa-f]{6}")
        for py_file in PLOTS_DIR.glob("*.py"):
            if py_file.name == "style_spec.py":
                continue
            text = py_file.read_text(encoding="utf-8")
            self.assertIsNone(
                hex_re.search(text),
                f"Hardcoded hex color found in {py_file.relative_to(ROOT)}",
            )

    def test_no_hardcoded_fmt_markers_in_plot_modules(self):
        fmt_re = re.compile(r"fmt\s*=\s*['\"][^'\"]+['\"]")
        for py_file in PLOTS_DIR.glob("*.py"):
            if py_file.name in {"style_spec.py", "plot_base.py"}:
                continue
            text = py_file.read_text(encoding="utf-8")
            self.assertIsNone(
                fmt_re.search(text),
                f"Hardcoded fmt marker found in {py_file.relative_to(ROOT)}",
            )

    def test_fileset_multi_series_uses_marker_cycle(self):
        fileset_plot_path = PLOTS_DIR / "fileset_plots.py"
        text = fileset_plot_path.read_text(encoding="utf-8")
        # Three run-overlay plots should use marker cycling.
        self.assertGreaterEqual(text.count("_series_marker("), 3)


if __name__ == "__main__":
    unittest.main()
