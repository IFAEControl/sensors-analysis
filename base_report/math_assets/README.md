Place KaTeX static assets in:

`base_report/math_assets/katex/`

Required files:
- `katex.min.js`
- `katex.min.css`
- `fonts/` directory referenced by the css

How to populate:
1. Download a KaTeX release archive.
2. Copy the `dist/` contents into `base_report/math_assets/katex/`.

Runtime requirements:
- Python dependency: `playwright`
- Browser install: run `playwright install chromium`

Notes:
- Renderer cache is stored in the system temp directory under
  `base_report_formula_cache`.
- Formula helpers prefer vector PDF output for quality; PNG is used as fallback.
- If assets or playwright are missing, formula helpers fall back to plain text.
