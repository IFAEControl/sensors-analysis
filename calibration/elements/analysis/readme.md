


# Files

- We calculate: 
  - linear regression fits of Power Meter (PM) mean vs Reference Photodiode (RefPD) mean for each calibration file.
  - pedestal values for each calibration file

# File Sets (same wavelength and filter wheel settings)

## Power Meter vs Reference Photodiode Analysis
- We aggregate data from multiple calibration files into a single df at file sets level
- With aggregated data we do a linear regression fit of PM mean vs RefPD mean over the entire file set
- For sanity check we also calculate the weighted mean of linear regression slopes across the file set.
  - Then we calculate chi2 and chi2_reduced to assess the goodness of fit.
  - This values should only be used as sanity checks (if chi2_reduced >> 1, something is wrong).

## Pedestals
- We also aggregate pedestal data from multiple calibration files into a single df at file sets level
- We calculate the mean and standard deviation of the pedestal values across the file set.
- We use weighted means for pedestals
- We calculate chi2 and chi2_reduced for pedestal fits as sanity checks.

## Environmental Parameters
- We aggregate environmental parameters (temperature, humidity) from multiple calibration files into a single df at file sets level and at calibration level.
- We calculate mean and standard deviation of these parameters across the aggregated dfs.