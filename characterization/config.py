
DEFAULT_SENSOR_ORDER = [
    '0.0','0.1','0.2','0.3',
    '1.0','1.1','1.2','1.3',
    '2.0','2.1','2.2','2.3',
    '3.0','3.1','3.2','3.3',
    '4.0','4.1','4.2','4.3'
]

class Configuration:
    """Holds global configuration settings"""
    plot_output_format = "pdf"
    generate_plots = True
    adc_to_power_factor = 0.61e-3
    saturation_derivative_threshold = 10.0
    summary_file_name = "characterization_summary.json"
    sensor_order = DEFAULT_SENSOR_ORDER
    sensors_without_gain = DEFAULT_SENSOR_ORDER[:16]
    sensors_with_gain = DEFAULT_SENSOR_ORDER[-4:]

    def to_dict(self):
        return {
            'plot_output_format': self.plot_output_format,
            'generate_plots': self.generate_plots,
            'adc_to_power_factor': self.adc_to_power_factor,
            'saturation_derivative_threshold': self.saturation_derivative_threshold,
            'sensor_order': list(self.sensor_order),
            'sensors_without_gain': list(self.sensors_without_gain),
            'sensors_with_gain': list(self.sensors_with_gain),
        }

config = Configuration()
