

from ..base_element import BaseElement, DataHolderLevel

from ..helpers import SanityCheckResult

class SanityBase:
    """Base class for sanity checks
    Contains sanity checks applicable to all levels of calibration data holders
    """

    def __init__(self, data_holder: BaseElement, level: DataHolderLevel):
        self.data_holder = data_holder
        self.df = data_holder.df
        self.df_pedestals = data_holder.df_pedestals
        self.df_full = data_holder.df_full
        self.level = level
    
    @property
    def level_header(self) -> str:
        """Return the label of the element based on its level"""
        return self.data_holder.level_header


    def san_check_max_temperature_swing(self, max_swing, severity) -> SanityCheckResult:
        """Check that the maximum temperature swing is within the specified range."""
        temp_series = self.df['temperature']
        temp_swing = temp_series.max() - temp_series.min()
        passed = temp_swing <= max_swing
        info = f"Temperature swing: {temp_swing:.2f} °C, Allowed range: {max_swing} °C"
        return SanityCheckResult(
            severity=severity,
            check_name='max_temperature_swing',
            check_args={'max_swing': max_swing},
            passed=passed,
            info=info,
            check_explanation=f"Checks if the maximum temperature swing during the calibration is within the limit: {max_swing} °C"
        )

    def san_info_max_temperature_swing(self, max_swing, severity) -> dict:
        """Return info for maximum temperature swing check."""
        temp_series = self.df['temperature']
        temp_swing = temp_series.max() - temp_series.min()
        info = f"Temperature swing: {temp_swing:.2f} °C, Allowed range: {max_swing} °C"
        return {
            'check_name': 'max_temperature_swing',
            'check_args': {'max_swing': max_swing},
            'severity': severity,
            'info': info,
            'check_explanation': f"Checks if the maximum temperature swing during the calibration is within the limit: {max_swing} °C",
        }
    
    def san_check_avg_temperature_range(self, min_avg, max_avg, severity) -> SanityCheckResult:
        """Check that the average temperature is within the specified range."""
        temp_series = self.df['temperature']
        avg_temp = temp_series.mean()
        passed = min_avg <= avg_temp <= max_avg
        info = f"Average temperature: {avg_temp:.2f} °C, Allowed range: [{min_avg}, {max_avg}] °C"
        return SanityCheckResult(
            severity=severity,
            check_name='avg_temperature_range',
            check_args={'min_avg': min_avg, 'max_avg': max_avg},
            passed=passed,
            info=info,
            check_explanation=f"Checks if the average temperature during the calibration is within limits:[{min_avg}, {max_avg}] °C"
        )

    def san_info_avg_temperature_range(self, min_avg, max_avg, severity) -> dict:
        """Return info for average temperature range check."""
        temp_series = self.df['temperature']
        avg_temp = temp_series.mean()
        info = f"Average temperature: {avg_temp:.2f} °C, Allowed range: [{min_avg}, {max_avg}] °C"
        return {
            'check_name': 'avg_temperature_range',
            'check_args': {'min_avg': min_avg, 'max_avg': max_avg},
            'severity': severity,
            'info': info,
            'check_explanation': f"Checks if the average temperature during the calibration is within limits:[{min_avg}, {max_avg}] °C",
        }
    
    def san_check_max_rh(self, max_rh, severity) -> SanityCheckResult:
        """Check that the maximum relative humidity is within the specified limit."""
        rh_series = self.df['RH']
        max_rh_value = rh_series.max()
        passed = max_rh_value <= max_rh
        info = f"Maximum relative humidity: {max_rh_value:.2f} %, Allowed maximum: {max_rh} %"
        return SanityCheckResult(
            severity=severity,
            check_name='max_relative_humidity',
            check_args={'max_rh': max_rh},
            passed=passed,
            info=info,
            check_explanation=f"Checks if the maximum relative humidity during the calibration is within the limit: {max_rh} %"
        )

    def san_info_max_rh(self, max_rh, severity) -> dict:
        """Return info for maximum relative humidity check."""
        rh_series = self.df['RH']
        max_rh_value = rh_series.max()
        info = f"Maximum relative humidity: {max_rh_value:.2f} %, Allowed maximum: {max_rh} %"
        return {
            'check_name': 'max_relative_humidity',
            'check_args': {'max_rh': max_rh},
            'severity': severity,
            'info': info,
            'check_explanation': f"Checks if the maximum relative humidity during the calibration is within the limit: {max_rh} %",
        }
    
    def san_check_max_acq_time_span_hours(self, max_hours, severity) -> SanityCheckResult:
        """Check that the total acquisition time span is within the specified limit in hours."""
        time_series = self.df['datetime']
        time_span = (time_series.max() - time_series.min()).total_seconds() / 3600.0
        passed = time_span <= max_hours
        info = f"Acquisition time span: {time_span:.2f} hours, Allowed maximum: {max_hours} hours"
        return SanityCheckResult(
            severity=severity,
            check_name='max_acquisition_time_span_hours',
            check_args={'max_hours': max_hours},
            passed=passed,
            info=info,
            check_explanation=f"Checks if the total acquisition time span during the calibration is within the limit: {max_hours} hours"
        )

    def san_info_max_acq_time_span_hours(self, max_hours, severity) -> dict:
        """Return info for acquisition time span check."""
        time_series = self.df['datetime']
        time_span = (time_series.max() - time_series.min()).total_seconds() / 3600.0
        info = f"Acquisition time span: {time_span:.2f} hours, Allowed maximum: {max_hours} hours"
        return {
            'check_name': 'max_acquisition_time_span_hours',
            'check_args': {'max_hours': max_hours},
            'severity': severity,
            'info': info,
            'check_explanation': f"Checks if the total acquisition time span during the calibration is within the limit: {max_hours} hours",
        }
    
    def san_check_min_data_points(self, min_points, severity) -> SanityCheckResult:
        """Check that the number of data points is above the specified minimum."""
        num_points = len(self.df)
        passed = num_points >= min_points
        info = f"Number of data points: {num_points}, Required minimum: {min_points}"
        return SanityCheckResult(
            severity=severity,
            check_name='min_data_points',
            check_args={'min_points': min_points},
            passed=passed,
            info=info,
            check_explanation=f"Checks if the number of data points in the calibration is above the minimum required: {min_points}"
        )

    def san_info_min_data_points(self, min_points, severity) -> dict:
        """Return info for minimum data points check."""
        num_points = len(self.df)
        info = f"Number of data points: {num_points}, Required minimum: {min_points}"
        return {
            'check_name': 'min_data_points',
            'check_args': {'min_points': min_points},
            'severity': severity,
            'info': info,
            'check_explanation': f"Checks if the number of data points in the calibration is above the minimum required: {min_points}",
        }
    
    def san_check_no_std_points(self, _, severity) -> SanityCheckResult:
        """Check that there are no points with standard deviation equal to zero in the data."""
        no_std_points = self.df[(self.df['pm_std']==0) | (self.df['ref_pd_std']==0)]
        num_std_points = len(no_std_points)
        info = f"There are {num_std_points} points with std = 0"
        passed = not num_std_points > 0
        return SanityCheckResult(
            severity=severity,
            check_name='no_std_points',
            check_args={},
            passed=passed,
            info=info,
            check_explanation="Checks that there are no points with standard deviation equal to zero in the calibration data"
        )

    def san_info_no_std_points(self, _, severity) -> dict:
        """Return info for no std points check."""
        no_std_points = self.df[(self.df['pm_std']==0) | (self.df['ref_pd_std']==0)]
        num_std_points = len(no_std_points)
        info = f"There are {num_std_points} points with std = 0"
        return {
            'check_name': 'no_std_points',
            'check_args': {},
            'severity': severity,
            'info': info,
            'check_explanation': "Checks that there are no points with standard deviation equal to zero in the calibration data",
        }

    def san_check_no_std_pedestals(self, _, severity) -> SanityCheckResult:
        """Check that there are no pedestal points with standard deviation equal to zero in the data."""
        no_std_points = self.df_pedestals[(self.df_pedestals['pm_std']==0) | (self.df_pedestals['ref_pd_std']==0)]
        num_std_points = len(no_std_points)
        info = f"There are {num_std_points} points with std = 0"
        passed = not num_std_points > 0
        return SanityCheckResult(
            severity=severity,
            check_name='no_std_pedestals',
            check_args={},
            passed=passed,
            info=info,
            check_explanation="Checks that there are no pedestal points with standard deviation equal to zero in the calibration data"
        )

    def san_info_no_std_pedestals(self, _, severity) -> dict:
        """Return info for no std pedestals check."""
        no_std_points = self.df_pedestals[(self.df_pedestals['pm_std']==0) | (self.df_pedestals['ref_pd_std']==0)]
        num_std_points = len(no_std_points)
        info = f"There are {num_std_points} points with std = 0"
        return {
            'check_name': 'no_std_pedestals',
            'check_args': {},
            'severity': severity,
            'info': info,
            'check_explanation': "Checks that there are no pedestal points with standard deviation equal to zero in the calibration data",
        }

    def san_check_zero_pedestals(self, _, severity) -> SanityCheckResult:
        """Check that there are no pedestal points with zero value in the data."""
        zero_pedestals = self.df_pedestals[(self.df_pedestals['pm_mean']==0) | (self.df_pedestals['ref_pd_mean']==0)]
        num_zero_pedestals = len(zero_pedestals)
        info = f"There are {num_zero_pedestals} pedestal points with zero value"
        passed = not num_zero_pedestals > 0
        return SanityCheckResult(
            severity=severity,
            check_name='zero_pedestals',
            check_args={},
            passed=passed,
            info=info,
            check_explanation="Checks that there are no pedestal points with zero value in the calibration data"
        )    

    def san_info_zero_pedestals(self, _, severity) -> dict:
        """Return info for zero pedestals check."""
        zero_pedestals = self.df_pedestals[(self.df_pedestals['pm_mean']==0) | (self.df_pedestals['ref_pd_mean']==0)]
        num_zero_pedestals = len(zero_pedestals)
        info = f"There are {num_zero_pedestals} pedestal points with zero value"
        return {
            'check_name': 'zero_pedestals',
            'check_args': {},
            'severity': severity,
            'info': info,
            'check_explanation': "Checks that there are no pedestal points with zero value in the calibration data",
        }
