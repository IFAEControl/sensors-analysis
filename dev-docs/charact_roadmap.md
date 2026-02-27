# Characterization Implementation Roadmap

## Phase 1: Contracts and Core Schema (first)


- [X] `CR-01` Define and enforce multi-level output contract.
  - [x] `CR-01.0` Establish global contract test scaffold (shared fixtures + validator-focused test modules + report-parse validation tests).
  - [x] `CR-01.1` Define required keys per level (`characterization`, `photodiode`, `fileset`, `sweepfile`) for `analysis`, `plots`, and `sanity_checks`.
  - [x] `CR-01.2` Add a contract validator pass before summary export.
  - [x] `CR-01.3` Add non-strict vs strict behavior (warn vs fail).
  - [x] `CR-01.4` Add unit tests with missing-level and malformed-level fixtures.

- [x] `CR-02` Add canonical `issues` schema to outputs.
  - [x] `CR-02.1` Add top-level `issues` key to extended summary (`*_extended.json`).
  - [x] `CR-02.2` Add top-level `issues` key to reduced summary (`*.json`).
  - [x] `CR-02.3` Implement issue key formats. Each key maps to a list of issue items:
    - `charact`
    - `PD_<PD_id>`
    - `PD_<PD_id>_<wavelength_fw>`
    - `PD_<PD_id>_<wavelength_fw>_<run_id>`
  - [x] `CR-02.4` Enforce issue item schema:
    - `description`: string
    - `level` in [`warning`, `error`]
    - `meta`: dict
  - [x] `CR-02.5` Add helper methods to append issues from each level.
  - [x] `CR-02.6` Parse issues in report data holders.

## Phase 2: Domain Invariants and Selection (second)

- [x] `CR-03` Enforce board-specific photodiode/fileset invariants.
  - [x] `CR-03.1` Validate each PD has exactly one `1064_FW5`.
  - [x] `CR-03.2` Validate each PD has exactly one `532_*`.
  - [x] `CR-03.3` Validate 532 filter (`FW4`/`FW5`) matches PD gain mapping.
  - [x] `CR-03.4` Surface violations as `issues` plus sanity-check failures.
  - [x] `CR-03.5` Decide strict-mode failure points (analysis/export/report).

- [x] `CR-04` Unify fileset selection logic across analysis and report.
  - [x] `CR-04.1` Create shared selector utility based on invariant-validated data.
  - [x] `CR-04.2` Replace current table selection logic in report overview.
  - [x] `CR-04.3` Replace current characterization plot selection logic.
  - [x] `CR-04.4` Remove first-match behavior in photodiode slide section.
  - [x] `CR-04.5` Add regression tests to ensure table values and plot values match source fileset.

## Phase 3: Calibration/Characterization Consistency (third)

- [x] `CR-05` Fix ADC->power model composition for pedestal conventions.
  - [x] `CR-05.1` Keep characterization behavior owned by runtime user choice:
    - If user enables pedestal subtraction, characterization uses zeroed data.
    - If user disables pedestal subtraction, characterization uses non-zeroed data.
  - [x] `CR-05.2` Read calibration pedestal-subtraction setting from calibration metadata/config when available.
  - [x] `CR-05.3` Add mismatch warning only (no automatic correction/override):
    - If calibration subtraction setting and characterization subtraction setting differ, add one warning issue at `charact` scope.
    - Include both settings and calibration source path in issue `meta`.
  - [x] `CR-05.4` Keep ADC->power composition unchanged by mismatch (user is source of truth).
  - [x] `CR-05.5` Add tests for matching vs mismatching settings and expected warning issue behavior.

## Phase 4: Report Robustness and Issue Rendering (fourth)

- [x] `CR-06` Make report generation resilient to missing plot tree.
  - [x] `CR-06.1` Add fallback behavior when `plots_path` does not exist.
  - [x] `CR-06.2` Render placeholders/warnings instead of hard failure.
  - [x] `CR-06.3` Keep strict mode available for CI validation.

- [ ] `CR-07` Render `issues` in report.
  - [ ] `CR-07.1` Add report section/subsection for issues, ordered by severity and scope.
  - [ ] `CR-07.2` Group entries by key pattern (`charact`, `PD...`, fileset, run).
  - [ ] `CR-07.3` Include structured `meta` rendering for debugging context.
  - [ ] `CR-07.4` Add at least one concrete rule-backed example:
    - characterization run without zeroing + calibration using zeroed fits.

- [ ] `CR-09` Standardize metric visual identity across all characterization plots.
  - [x] `CR-09.1` Define a single centralized style spec with per-metric visual tokens:
    - fixed color for each metric (same metric always same color)
    - default marker for all metrics: `.`
    - explicit line-style defaults per metric family
  - [x] `CR-09.2` Apply metric-to-axis consistency rules:
    - if an axis is dedicated to one metric, axis label and tick color must match that metric color
    - disallow ad-hoc axis coloring not tied to plotted metrics
  - [x] `CR-09.3` Constrain transparency usage to confidence bands only:
    - `mean ± std` band uses the same metric color with configured alpha
    - mean line is always dashed (`--`) and fully opaque
    - all other plotted items remain fully opaque by default
  - [x] `CR-09.4` Implement shared plot-style helpers and migrate plot modules to use them (remove hardcoded styling in plot bodies).
  - [x] `CR-09.5` Add visual-regression/style checks to detect metric color/marker drift and non-compliant transparency usage.

## Phase 5: Cleanup and Diagnostics (last)

- [x] `CR-08` Replace raw stdout dumps with structured diagnostics.
  - [x] `CR-08.1` Remove `print(self._data_holder._df)` from sweepfile analysis.
  - [x] `CR-08.2` Emit structured log fields (PD, fileset, run, reason code).
  - [x] `CR-08.3` Add reason classification (`all_points_saturated`, `all_points_pedestal`, etc.).

## Implementation Notes

- Recommended execution order: Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5.
- `issues` should be the common transport layer for reportable problems across all levels.
- Domain invariant assumed throughout:
  - per PD exactly 2 filesets total: `1064_FW5` and one of `532_FW4`/`532_FW5`.
