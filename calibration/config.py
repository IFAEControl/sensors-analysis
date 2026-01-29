


PowerMeterResolutions = {
    '532-FW4': 4.51E-8,
    '532-FW5': 4.56E-9,
    '1064-FW5': 4.57E-9,
}


class Configuration:
    """Holds global configuration settings"""
    plot_output_format = "pdf"
    generate_plots = True
    subtract_pedestals = True # whether we select the results with or without pedestal subtraction
    replace_zero_pm_stds = True # whether we substitute pm stds that are zero with the power meter resolution
    power_meter_resolutions = PowerMeterResolutions
    use_first_pedestal_in_linreg = False  # whether to use the first pedestal measurement in linear regression calculations
    use_uW_as_power_units = True  # whether to convert power meter values to uW

    def to_dict(self):
        """Convert configuration to dictionary."""
        return {
            'plot_output_format': self.plot_output_format,
            'generate_plots': self.generate_plots,
            'subtract_pedestals': self.subtract_pedestals,
            'replace_zero_pm_stds': self.replace_zero_pm_stds,
            'power_meter_resolutions': self.power_meter_resolutions,
            'use_first_pedestal_in_linreg': self.use_first_pedestal_in_linreg,
            'use_uW_as_power_units': self.use_uW_as_power_units,
        }


# Easiest way to create a singleton configuration object
config = Configuration()
