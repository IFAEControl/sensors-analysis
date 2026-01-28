




class Configuration:
    """Holds global configuration settings"""
    plot_output_format = "pdf"
    generate_plots = True
    # substract_pedestals = True

    def to_dict(self):
        """Convert configuration to dictionary."""
        return {
            'plot_output_format': self.plot_output_format,
            'generate_plots': self.generate_plots,
            # 'substract_pedestals': self.substract_pedestals
        }



config = Configuration()
