
DEFAULT_SENSOR_CONFIG = {
    '0.0': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '0.1': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '0.2': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '0.3': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '1.0': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '1.1': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '1.2': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '1.3': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '2.0': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '2.1': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '2.2': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '2.3': {'gain': 'G1', 'resistor': '26KOhm', 'valid_setups': ['1064_FW5', '532_FW4']},
    '3.0': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
    '3.1': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
    '3.2': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
    '3.3': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
    '4.0': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
    '4.1': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
    '4.2': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
    '4.3': {'gain': 'G2', 'resistor': '43KOhm', 'valid_setups': ['1064_FW5', '532_FW5']},
}

#Simulation values in W
simulation_values ={
  "ring_0":
    {
      "ring": 0,
      "mean": 1.990725e-05,
      "max": 6.637512e-05,
      "min": 3.169594e-08,
      "std": 1.874367e-05
    },
    "ring_1":
    {
      "ring": 1,
      "mean": 1.458260e-05,
      "max": 6.896541e-05,
      "min": 3.786805e-07,
      "std": 1.646452e-05
    },
    "ring_2":
    {
      "ring": 2,
      "mean": 1.835189e-05,
      "max": 6.818298e-05,
      "min": 1.317082e-06,
      "std": 1.804822e-05
    },
    "ring_3":
    {
      "ring": 3,
      "mean": 4.745450e-06,
      "max": 4.141094e-05,
      "min": 2.736418e-08,
      "std": 8.890185e-06
    },
    "ring_4":
    {
      "ring": 4,
      "mean": 5.174421e-11,
      "max": 2.851689e-10,
      "min": 1.056834e-12,
      "std": 7.221893e-11
    }
}
class Configuration:
    """Holds global configuration settings"""
    plot_output_format = "pdf"
    generate_plots = True
    generate_file_plots = True
    subtract_pedestals = True
    saturation_derivative_threshold = 10.0
    summary_file_name = "characterization_summary.json"
    sensor_config = DEFAULT_SENSOR_CONFIG

    def to_dict(self):
        return {
            'plot_output_format': self.plot_output_format,
            'generate_plots': self.generate_plots,
            'generate_file_plots': self.generate_file_plots,
            'subtract_pedestals': self.subtract_pedestals,
            'saturation_derivative_threshold': self.saturation_derivative_threshold,
            'summary_file_name': self.summary_file_name,
            'sensor_config': dict(self.sensor_config)
        }

config = Configuration()
