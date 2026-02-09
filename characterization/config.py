
DEFAULT_SENSOR_CONFIG = {
    '0.0': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '0.1': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '0.2': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '0.3': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '1.0': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '1.1': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '1.2': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '1.3': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '2.0': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '2.1': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '2.2': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '2.3': {'gain': 'G1', 'resistor': '26KOhm', 'expected_runs': ['1064_FW5', '532_FW4']},
    '3.0': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
    '3.1': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
    '3.2': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
    '3.3': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
    '4.0': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
    '4.1': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
    '4.2': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
    '4.3': {'gain': 'G2', 'resistor': '43KOhm', 'expected_runs': ['1064_FW5', '532_FW5']},
}

class Configuration:
    """Holds global configuration settings"""
    plot_output_format = "pdf"
    generate_plots = True
    saturation_derivative_threshold = 10.0
    summary_file_name = "characterization_summary.json"
    sensor_config = DEFAULT_SENSOR_CONFIG

    def to_dict(self):
        return {
            'plot_output_format': self.plot_output_format,
            'generate_plots': self.generate_plots,
            'saturation_derivative_threshold': self.saturation_derivative_threshold,
            'summary_file_name': self.summary_file_name,
            'sensor_config': dict(self.sensor_config)
        }

config = Configuration()
