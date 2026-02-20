# Calibration Module Review Tasks

## Errors
- [X] `CAL-ERR-001` Fix power-unit inconsistency: when `pm_mean` is converted to `uW`, `pm_std` is left in original units, breaking uncertainties and weighted fits. (`calibration/elements/calib_file.py:137`, `calibration/elements/calib_file.py:139`, `calibration/elements/calib_file.py:132`)
- [X] `CAL-ERR-002` Handle missing power-meter resolution keys before replacement. Current code can replace zero `pm_std` with `None` and format `None` with `%g`, causing runtime logging/analysis failures. (`calibration/elements/calib_file.py:108`, `calibration/elements/calib_file.py:112`, `calibration/elements/calib_file.py:113`)
- [X] `CAL-ERR-003` Prevent invalid pedestal subtraction when weighted pedestal stats fail (`ndof <= 0`). Code still uses `w_mean` defaulting to `0.0`, producing wrong zeroed signals. (`calibration/elements/analysis/analysis_base.py:84`, `calibration/elements/calib_file.py:120`, `calibration/elements/calib_file.py:121`)
- [X] `CAL-ERR-004` Align fileset-level linear regression with selected data mode. It always uses non-zeroed columns even when pedestal subtraction is enabled. (`calibration/elements/analysis/fileset_analysis.py:103`)
- [X] `CAL-ERR-005` Remove duplicated sample-plot generation in file-level plots (same two plots generated twice). (`calibration/elements/plots/file_plots.py:54`, `calibration/elements/plots/file_plots.py:55`, `calibration/elements/plots/file_plots.py:56`, `calibration/elements/plots/file_plots.py:57`)
- [X] `CAL-ERR-006` Add empty-data guards before `pd.concat`/time-range conversion. Current flow can crash when there are no valid files or no rows (e.g., `No objects to concatenate`, `int(inf)`). (`calibration/elements/calibration.py:83`, `calibration/elements/calib_fileset.py:44`, `calibration/elements/analysis/calibration_analysis.py:51`, `calibration/elements/analysis/calibration_analysis.py:64`)
- [X] `CAL-ERR-007` Secure ZIP extraction against path traversal and filename collisions. Current `extract` + flatten/rename flow is unsafe and can overwrite files. (`calibration/helpers/file_manage.py:50`, `calibration/helpers/file_manage.py:56`)

## Improvements
- [X] `CAL-IMP-001` Replace mutable default argument in `export_calib_data_summary(meta={})` with `None` to avoid shared-state bugs. (`calibration/elements/calibration.py:153`)
- [ ] `CAL-IMP-002` Replace `print(outdata)` fallback on JSON serialization errors with structured logging and safe redaction to avoid noisy stdout and huge dumps. (`calibration/elements/calibration.py:163`, `calibration/elements/calibration.py:186`)
- [ ] `CAL-IMP-003` Replace broad `except Exception` blocks around critical paths with narrower exception handling and actionable messages. (`calibration/main.py:73`, `calibration/elements/sanity_checks.py:114`, `calibration/elements/calibration.py:73`)
- [ ] `CAL-IMP-004` Use `fig.savefig(...)` instead of global `plt.savefig(...)` in base plot utilities to avoid cross-figure save mistakes in multi-figure contexts. (`calibration/elements/plots/plot_base.py:117`)
- [ ] `CAL-IMP-005` Remove incorrect/unused logger import (`from venv import logger`) and consistently use package logger. (`calibration/elements/plots/plot_base.py:3`)
- [ ] `CAL-IMP-006` Reset `FileSetAnalysis` accumulator arrays at the start of `analyze()` to avoid duplicated values on re-runs in the same process. (`calibration/elements/analysis/fileset_analysis.py:33`, `calibration/elements/analysis/fileset_analysis.py:88`)
- [ ] `CAL-IMP-007` Preserve structured types in sanity result serialization (`check_args` currently stringified), so downstream report/UI code can consume typed values. (`calibration/elements/helpers.py:167`)

## Recommendations
- [ ] `CAL-REC-001` Add regression tests for edge cases: empty input folder, all-invalid filenames, single-row files, and zero-std replacement with unknown `(wavelength, FW)` pairs.
- [ ] `CAL-REC-002` Add integration tests for unit mode (`W` vs `uW`) verifying consistent scaling across `pm_mean`, `pm_std`, pedestals, fits, and exports.
- [ ] `CAL-REC-003` Add security tests for ZIP ingestion (Zip Slip paths, duplicate basenames, nested folders) and enforce safe extraction policy.
- [ ] `CAL-REC-004` Add a pre-analysis validation stage that reports all input/data issues before running fits/plots (schema, required columns, min rows per file/fileset).
- [ ] `CAL-REC-005` Add static quality gates in CI (`ruff`/`mypy`/`pytest`) for typing mismatches, unreachable branches, and broad exception usage.
