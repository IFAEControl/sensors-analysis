class Configuration:
    """Holds global configuration settings for crossboard analysis."""

    plot_output_format = "pdf"
    generate_plots = True
    summary_file_name = "crossboard_summary.json"
    final_calification_exclusion_pct_threshold = 10.0

    def to_dict(self):
        return {
            "plot_output_format": self.plot_output_format,
            "generate_plots": self.generate_plots,
            "summary_file_name": self.summary_file_name,
            "final_calification_exclusion_pct_threshold": self.final_calification_exclusion_pct_threshold,
        }


config = Configuration()
