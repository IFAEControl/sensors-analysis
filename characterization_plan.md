# Characterization Port Plan

1. Read and summarize the legacy characterization notebook logic, including file naming, data columns, and required metrics/plots.
2. Define the new module structure (characterization package with config, helpers, elements, analysis, and plots), mirroring the calibration coding style.
3. Implement data loading/parsing for characterization files, including pedestal removal, ADC/PM derivations, saturation detection, and linear regression per file.
4. Implement photodiode-level aggregation and characterization-level aggregation across sensors for each wavelength/run.
5. Implement plot generation for per-file (low-level) and per-wavelength/run (high-level) plots.
6. Add CLI entrypoint (main) to run analysis, generate plots, and export JSON summary.
7. Sanity-check with a small dataset (optional) and adjust edge cases (missing sensors, empty runs).
