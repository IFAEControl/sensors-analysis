# Calibration Column-Policy Review Tasks

## Errors
- [ ] `COL-ERR-001` Unify regression column selection in file-level analysis by using `self._data_holder.pm_col` / `self._data_holder.refpd_col` instead of re-implementing policy with `config.subtract_pedestals`. Current duplication can drift from the canonical policy. (`calibration/elements/analysis/file_analysis.py:51`, `calibration/elements/analysis/file_analysis.py:52`, `calibration/elements/base_element.py:33`)
- [ ] `COL-ERR-002` Avoid mixing fileset plot selectors with direct file internals. Several fileset plots index `calfile._df[...]` using fileset-level selectors (`self.pm_col`, `self.refpd_col`), which bypasses file accessors and can desynchronize column policy if file-level behavior changes. Use `calfile.df[...]` with `calfile.pm_col`/`calfile.refpd_col`. (`calibration/elements/plots/fileset_plots.py:501`, `calibration/elements/plots/fileset_plots.py:502`, `calibration/elements/plots/fileset_plots.py:601`, `calibration/elements/plots/fileset_plots.py:602`)
- [ ] `COL-ERR-003` Enforce compatibility in calibration-evolution plots before comparing historical slopes/intercepts. Historical entries can come from runs using different column policy (`pm_mean/ref_pd_mean` vs `pm_zeroed/ref_pd_zeroed`), which makes trend lines non-comparable unless filtered by `x_var/y_var` (or config snapshot). (`calibration/elements/plots/fileset_plots.py:177`, `calibration/elements/plots/fileset_plots.py:192`, `calibration/elements/plots/fileset_plots.py:203`)

## Improvements
- [ ] `COL-IMP-001` Record and export explicit fileset-level `used_columns` for concatenated regression (`x`, `y`) next to `lr_refpd_vs_pm`, so report/render layers can validate policy consistency without re-inferring from defaults. (`calibration/elements/analysis/fileset_analysis.py:101`, `calibration/elements/analysis/fileset_analysis.py:111`)
- [ ] `COL-IMP-002` Add a runtime validation in `CalibFile.load_data()` after zero-std replacement: when `replace_zero_pm_stds=True`, assert no remaining zero values in `pm_std` for the analysis dataframe and pedestals dataframe, and fail fast with filename context. (`calibration/elements/calib_file.py:103`, `calibration/elements/calib_file.py:152`, `calibration/elements/calib_file.py:154`)
- [ ] `COL-IMP-003` Centralize “raw pedestal columns” vs “analysis columns” through helper methods/properties (e.g., `ped_pm_col='pm_mean'`, `ped_refpd_col='ref_pd_mean'`) to prevent accidental use of non-policy columns in new plots. (`calibration/elements/plots/plot_base.py:290`, `calibration/elements/plots/fileset_plots.py:711`, `calibration/elements/plots/fileset_plots.py:771`)
- [ ] `COL-IMP-004` Remove unused direct `config` dependency in `file_analysis.py` once column selection is delegated to `BaseElement` properties; this reduces policy forks to one implementation path. (`calibration/elements/analysis/file_analysis.py:9`, `calibration/elements/analysis/file_analysis.py:51`)

## Recommendations
- [ ] `COL-REC-001` Add parameterized tests for column policy matrix:
  1) `subtract_pedestals=True/False`
  2) `replace_zero_pm_stds=True/False`
  3) `use_uW_as_power_units=True/False`
  Validate selected analysis columns, zero-std replacement effect, and regression outputs at file/fileset levels.
- [ ] `COL-REC-002` Add snapshot tests for plot inputs (not images) to verify each plot method uses expected columns (`pm_col`, `refpd_col`, `pm_std_col`) under both pedestal modes.
- [ ] `COL-REC-003` Include policy metadata (`subtract_pedestals`, `replace_zero_pm_stds`, `used_columns`) in reduced summaries used for historical evolution, and skip/flag incompatible historical points in evolution plots.
