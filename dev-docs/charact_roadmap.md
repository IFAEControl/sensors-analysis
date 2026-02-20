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

- [ ] `CR-05` Fix ADC->power model composition for pedestal conventions.
  - [ ] `CR-05.1` Detect calibration fit variable convention from `x_var`/`y_var` and metadata.
  - [ ] `CR-05.2` Implement correct composition for zeroed-vs-non-zeroed combinations.
  - [ ] `CR-05.3` Emit explicit `issues` entry for incompatible/unsafe convention mixes.
  - [ ] `CR-05.4` Add test matrix for all supported combinations and expected intercept behavior.

## Phase 4: Report Robustness and Issue Rendering (fourth)

- [ ] `CR-06` Make report generation resilient to missing plot tree.
  - [ ] `CR-06.1` Add fallback behavior when `plots_path` does not exist.
  - [ ] `CR-06.2` Render placeholders/warnings instead of hard failure.
  - [ ] `CR-06.3` Keep strict mode available for CI validation.

- [ ] `CR-07` Render `issues` in report.
  - [ ] `CR-07.1` Add report section/subsection for issues, ordered by severity and scope.
  - [ ] `CR-07.2` Group entries by key pattern (`charact`, `PD...`, fileset, run).
  - [ ] `CR-07.3` Include structured `meta` rendering for debugging context.
  - [ ] `CR-07.4` Add at least one concrete rule-backed example:
    - characterization run without zeroing + calibration using zeroed fits.

- [ ] `CR-09` Implement plot style guide and enforce it across characterization plots.
  - [ ] `CR-09.1` Define a centralized visual style spec (color palette, line styles, marker rules, transparency defaults).
  - [ ] `CR-09.2` Define fixed color mapping by plotted property so the same property always uses the same color in all plots.
  - [ ] `CR-09.3` Implement shared helper utilities for applying style rules in plot modules.
  - [ ] `CR-09.4` Enforce mean ± std area rendering with the same base shade and transparency policy across plots.
  - [ ] `CR-09.5` Add regression tests/checks to detect style drift for key plot families.

## Phase 5: Cleanup and Diagnostics (last)

- [ ] `CR-08` Replace raw stdout dumps with structured diagnostics.
  - [ ] `CR-08.1` Remove `print(self._data_holder._df)` from sweepfile analysis.
  - [ ] `CR-08.2` Emit structured log fields (PD, fileset, run, reason code).
  - [ ] `CR-08.3` Add reason classification (`all_points_saturated`, `all_points_pedestal`, etc.).

## Implementation Notes

- Recommended execution order: Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5.
- `issues` should be the common transport layer for reportable problems across all levels.
- Domain invariant assumed throughout:
  - per PD exactly 2 filesets total: `1064_FW5` and one of `532_FW4`/`532_FW5`.
