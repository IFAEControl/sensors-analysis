# Sensors Analysis Code Organization

## Top-Level Modules

- `calibration/`
  - Builds calibration products from setup measurements.
  - Produces reduced calibration JSONs (for downstream characterization) and extended artifacts/plots/reports.
- `characterization/`
  - Analyzes DUT sweep files, computes per-file/per-fileset/per-photodiode regressions, applies calibration, exports summaries.
- `characterization_report/`
  - Reads characterization extended summary JSON and renders PDF slides.
- `calib_report/`
  - Report generator for calibration outputs.
- `crossboard/` and `crossboard_report/`
  - Cross-board comparative analysis and reporting.
- `base_report/`
  - Shared slide/report rendering primitives.

## Characterization Processing Flow

1. Entry point: `characterization/main.py`
2. Orchestration object: `characterization/elements/characterization.py`
3. Input parsing:
   - `characterization/elements/sweep_file.py` parses filename metadata and tabular data.
4. Hierarchy:
   - `Characterization` -> `Photodiode` -> `Fileset` -> `SweepFile`
5. Analysis layer:
   - `characterization/elements/analysis/`
   - File-level and fileset-level linear regressions (`ref_pd_mean` vs `mean_adc`), pedestal/saturation stats.
6. Calibration merge:
   - `Characterization.apply_calibration(...)` composes characterization and calibration linear models to derive ADC->power conversion factors.
   - Characterization pedestal subtraction is controlled only by runtime user setting.
   - If calibration and characterization subtraction settings differ, emit a warning issue; do not override user-selected characterization behavior.
7. Outputs:
   - Extended summary (`*_extended.json`)
   - Reduced summary (`*.json`)
   - Optional plots and report PDF
8. Sanity checks:
   - `characterization/elements/sanity_checks.py` + `characterization/elements/sanity/`

## Required Processing Levels

- `characterization` level
  - Global aggregates, global plots, top-level sanity checks.
- `photodiode` level
  - Per-sensor aggregates/plots and sensor-scoped sanity checks.
- `fileset` level
  - Per `(wavelength, filter)` aggregates/plots and fileset-scoped sanity checks.
- `sweepfile` level
  - Per-run analysis/plots and run-scoped sanity checks.

The system design assumes all four levels are consistently represented in outputs (analysis + plots + sanity checks) so downstream report parsing remains deterministic.
Issue reporting should follow the same four-level structure through canonical `issues` keys.

## Characterization Report Flow

1. Entry point: `characterization_report/main.py`
2. Path/data resolution: `characterization_report/helpers/paths.py`
3. Typed parsing of summary JSON: `characterization_report/helpers/data_holders.py`
4. Slide assembly: `characterization_report/slides_sections/full_report.py`
   - `CharacterizationOverviewSection`
   - `ToCSection`
   - `PhotodiodeOverviewSection`
   - `SanityChecksSection`
5. Per-slide content helpers:
   - `characterization_report/report_elements/`

## Key Data Contracts

- Calibration reduced JSON (e.g., `out-calibs/calibration_16022026.json`)
  - `filesets.<cfg>.full_dataset_linreg`
  - `power_unit`
- Calibration extended JSON (source of convention metadata for CR-05)
  - `meta.config.subtract_pedestals` (primary)
  - `meta.calling_arguments.do_not_sub_pedestals` (fallback, inverted)
- Characterization extended JSON
  - `meta` + `analysis` + `plots` + `sanity_checks`
  - Must include characterization subtraction setting in `meta` for mismatch warning checks.
  - Optional calibration metadata and conversion factors.
- Characterization extended and reduced JSON
  - Top-level `issues` dictionary for reportable issues.
  - Supported child keys under `issues`:
    - `charact`
    - `PD_<PD_id>`
    - `PD_<PD_id>_<wavelength_fw>`
    - `PD_<PD_id>_<wavelength_fw>_<run_id>`
  - Issue object schema:
    - `description`: string
    - `level`: one of `warning`, `error`
    - `meta`: object/dict with contextual payload

## Domain Invariants (Board Characterization)

- The board has 20 photodiodes.
- PD gains are not uniform across sensors.
- For each PD:
  - exactly one `1064` fileset is expected, and it must use `FW5`.
  - exactly one `532` fileset is expected.
  - `532` filter must be gain-dependent (`FW4` or `FW5` according to PD gain group).
- Therefore each PD should expose exactly 2 filesets total in characterization outputs: one for `1064_FW5` and one for `532_FW4` or `532_FW5`.

## Current Coupling Points to Watch

- Calibration-to-characterization model composition:
  - `characterization/elements/characterization.py`
  - Mismatch between calibration and characterization subtraction settings should produce a warning issue only.
- Fileset selection/validation logic:
  - Report overview tables: `characterization_report/report_elements/characterization_overview.py`
  - Summary plots: `characterization/elements/plots/characterization_plots.py`
  - PD slide selection: `characterization_report/slides_sections/photodiode_overview_section.py`
- Report dependence on plot filesystem presence:
  - `characterization_report/helpers/paths.py`
