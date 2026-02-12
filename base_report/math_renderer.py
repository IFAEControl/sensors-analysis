from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import tempfile


class MathRenderError(RuntimeError):
    """Raised when formula rendering cannot be completed."""


@dataclass(frozen=True)
class FormulaRenderOptions:
    display_mode: bool = True
    font_size_px: int = 32
    text_color: str = "#1A1A1A"
    background_color: str = "transparent"
    horizontal_padding_px: int = 12
    vertical_padding_px: int = 8
    max_width_px: int = 1800
    scale_factor: float = 2.0


class LocalKaTeXRenderer:
    """
    Local KaTeX renderer scaffold.

    Requirements:
    - playwright Python package installed
    - Chromium installed (`playwright install chromium`)
    - KaTeX assets available at `assets_dir`:
      - katex.min.js
      - katex.min.css
      - fonts/...
    """

    def __init__(
        self,
        assets_dir: str | None = None,
        cache_dir: str | None = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parent
        self.assets_dir = Path(assets_dir) if assets_dir else base_dir / "math_assets" / "katex"
        self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "base_report_formula_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def render_formula_png(
        self,
        formula: str,
        options: FormulaRenderOptions | None = None,
    ) -> str:
        """
        Raster fallback renderer (kept for compatibility).
        Prefer render_formula_pdf() for vector quality.
        """
        opts = options or FormulaRenderOptions()
        self._validate_assets()
        out_path = self._cached_output_path(formula, opts, ext="png")
        if out_path.exists():
            return str(out_path)

        css_path = self.assets_dir / "katex.min.css"
        js_path = self.assets_dir / "katex.min.js"
        css_text = css_path.read_text(encoding="utf-8")
        js_text = js_path.read_text(encoding="utf-8")

        html = self._build_html(formula, css_text, js_text, opts)
        png_tmp = out_path.with_suffix(".tmp.png")

        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise MathRenderError(
                "Playwright is not installed. Install dependencies and run "
                "`playwright install chromium`."
            ) from exc

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(
                    viewport={"width": max(1000, opts.max_width_px), "height": 800}
                )
                box = self._render_into_page(page, html)
                page.screenshot(
                    path=str(png_tmp),
                    clip=box,
                    omit_background=(opts.background_color == "transparent"),
                    scale="device" if opts.scale_factor > 1.0 else "css",
                )
                browser.close()
        except Exception as exc:
            raise MathRenderError(f"Failed to render formula: {exc}") from exc

        shutil.move(str(png_tmp), str(out_path))
        return str(out_path)

    def render_formula_pdf(
        self,
        formula: str,
        options: FormulaRenderOptions | None = None,
    ) -> str:
        """Vector renderer based on Chromium PDF output."""
        opts = options or FormulaRenderOptions()
        self._validate_assets()
        out_path = self._cached_output_path(formula, opts, ext="pdf")
        if out_path.exists():
            return str(out_path)

        css_path = self.assets_dir / "katex.min.css"
        js_path = self.assets_dir / "katex.min.js"
        css_text = css_path.read_text(encoding="utf-8")
        js_text = js_path.read_text(encoding="utf-8")
        html = self._build_html(formula, css_text, js_text, opts)
        pdf_tmp = out_path.with_suffix(".tmp.pdf")

        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise MathRenderError(
                "Playwright is not installed. Install dependencies and run "
                "`playwright install chromium`."
            ) from exc

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(
                    viewport={"width": max(1000, opts.max_width_px), "height": 800}
                )
                box = self._render_into_page(page, html)
                # Chromium PDF accepts CSS length strings; this preserves tight bounds.
                page.pdf(
                    path=str(pdf_tmp),
                    width=f"{max(1.0, box['width']):.2f}px",
                    height=f"{max(1.0, box['height']):.2f}px",
                    margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"},
                    print_background=True,
                    prefer_css_page_size=True,
                )
                browser.close()
        except Exception as exc:
            raise MathRenderError(f"Failed to render formula PDF: {exc}") from exc

        shutil.move(str(pdf_tmp), str(out_path))
        return str(out_path)

    def _validate_assets(self) -> None:
        required = [
            self.assets_dir / "katex.min.css",
            self.assets_dir / "katex.min.js",
        ]
        missing = [str(p) for p in required if not p.exists()]
        if missing:
            raise MathRenderError(
                "KaTeX assets not found. Missing files: "
                + ", ".join(missing)
                + ". Place KaTeX distribution files under "
                + f"{self.assets_dir}."
            )

    def _cached_output_path(self, formula: str, opts: FormulaRenderOptions, ext: str) -> Path:
        key = json.dumps(
            {
                "formula": formula,
                "options": opts.__dict__,
                "assets_dir": str(self.assets_dir),
                "ext": ext,
            },
            sort_keys=True,
        )
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"katex_formula_{digest}.{ext}"

    def _render_into_page(self, page, html: str) -> dict:
        page.set_content(html, wait_until="load")
        page.wait_for_selector("#math .katex", timeout=5000)
        box = page.locator("#wrap").bounding_box()
        if not box or box["width"] <= 0 or box["height"] <= 0:
            raise MathRenderError("Could not compute formula bounding box.")
        return box

    def _build_html(
        self,
        formula: str,
        css_text: str,
        js_text: str,
        opts: FormulaRenderOptions,
    ) -> str:
        formula_json = json.dumps(formula)
        display_mode_js = "true" if opts.display_mode else "false"
        return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      {css_text}
      html, body {{
        margin: 0;
        padding: 0;
        background: {opts.background_color};
      }}
      #wrap {{
        display: inline-block;
        padding: {opts.vertical_padding_px}px {opts.horizontal_padding_px}px;
      }}
      #math {{
        color: {opts.text_color};
        font-size: {opts.font_size_px}px;
      }}
    </style>
    <script>{js_text}</script>
  </head>
  <body>
    <div id="wrap"><div id="math"></div></div>
    <script>
      const formula = {formula_json};
      const node = document.getElementById("math");
      katex.render(formula, node, {{
        throwOnError: false,
        displayMode: {display_mode_js},
        trust: false
      }});
    </script>
  </body>
</html>
"""
