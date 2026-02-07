# Characterization_board_setup2.ipynb — Summary

## Purpose
Processes photodiode characterization sweeps. Each text file is a laser power/current sweep with reference PD and ADC sums. The notebook:
1. Loads multiple runs per sensor.
2. Splits pedestal points from sweep points.
3. Computes ADC mean/std (and sometimes ref PD in W via coefficients).
4. Detects saturation via derivative of ADC vs ref PD.
5. Fits linear regressions to the non-saturated region.
6. Produces low‑level per-sensor plots and high‑level summary plots.
7. Includes optional stability histogram tooling.

## Data Flow (Main Steps)
1. **Read raw file(s)** per sensor, wavelength, and run. Each file has columns:
   - Date/Time, Laser setpoint, TotalSum, TotalSquareSum, meanRefPD, stdRefPD, Temperature, RH, TotalCounts.
2. **Split pedestals vs main sweep**
   - Pedestals: first and last rows from each run (or rows where laser setpoint is 0 in other variants).
   - Main data: all rows except the pedestal rows.
3. **Compute ADC statistics** for each row:
   - `meanADC = TotalSum / TotalCounts`
   - `stdADC = sqrt((TotalSquareSum - TotalCounts * meanADC^2)/(TotalCounts - 1))`
4. **Pedestal stats**
   - Same `meanADC`/`stdADC` computed on the pedestal rows.
   - Weighted pedestal mean/std computed from per‑row stds.
5. **Saturation detection**
   - Compute derivative of `meanADC` vs `meanRefPD` and find first “flat” region (small derivative). Clip data before saturation.
6. **Linear regression** on filtered (non‑saturated) data:
   - `linregress(x, y)` for either:
     - `x = meanRefPD`, `y = meanADC` (ADC vs ref PD), or
     - `x = meanADC`, `y = meanRefPD` (inverse form used later in the notebook).
7. **Aggregate** slopes/intercepts across sensors for a wavelength and generate summary plots.

## Main Equations
1. **ADC mean**
   - `meanADC = TotalSum / TotalCounts`
2. **ADC standard deviation**
   - `stdADC = sqrt((TotalSquareSum - TotalCounts * meanADC^2)/(TotalCounts - 1))`
3. **Ref PD conversion to power (when coefficients are used)**
   - `meanRefPD_W = meanRefPD_V * coeff`
   - `stdRefPD_W = stdRefPD_V * coeff`
4. **Linear regression**
   - `linregress(x, y)` on non‑saturated data points.
5. **Weighted mean of pedestals** (and of slopes in some sections)
   - `weights = 1 / stderr^2`
   - `weighted_mean = sum(weights * values) / sum(weights)`
   - `weighted_mean_error = sqrt(1 / sum(weights))`
   - `weighted_variance = sum(weights * (values - weighted_mean)^2) / sum(weights)`
   - `weighted_std_dev = sqrt(weighted_variance)`

## Saturation Detection
- Uses gradient of `meanADC` vs `meanRefPD`:
  - `dy_dx = gradient(meanADC, meanRefPD)`
- Defines saturation when `|dy_dx| < threshold` (threshold = 10).
- Clips data before the first flat segment (sometimes with a safety offset).

## Plots Generated
### Low‑level (per sensor, per wavelength)
- `meanADC vs laser setpoint` with error bars.
- `meanRefPD vs laser setpoint` with error bars.
- `meanADC vs meanRefPD` with regression line.
- Histograms of temperature and RH (stability plots in a PDF).

### High‑level (across sensors for a wavelength)
- Slopes with error bars across sensor IDs.
- Intercepts with error bars across sensor IDs.
- r‑values (correlation) across sensor IDs.
- Saturation ADC values across sensor IDs.
- Optional grouped plots for sensors **with gain** vs **without gain**.
- Weighted mean slope and associated uncertainty bands.
- “Power range” plot for all sensors on a log scale (when ref‑PD coefficients are used).

## Extra Utilities Included
- `plot_histograms(...)`: outputs a PDF of histograms for numeric columns.
- `MergeDatasets(...)` and `Overall_Stability(...)`: utilities to merge multiple files and plot stability histograms/time series for various columns.

## Notes / Variants in Notebook
- There are multiple analysis functions (`ADC_analysis_std`, `ADC_analysis_sensor_gain`, etc.).
- Some sections use ref‑PD conversion to W via per‑sensor coefficients.
- Some filenames include filter wheel (e.g., `..._FW5_...`) and some do not.
- The regression orientation changes in later sections (ADC→RefPD vs RefPD→ADC).

