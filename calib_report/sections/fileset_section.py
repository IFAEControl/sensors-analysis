
from ..helpers.data_holders import ReportData, Fileset, FileSetPlots
from ..helpers.paths import calc_plot_path
from base_report.base_report import BaseReport
from ..report_elements.sanity_checks import add_sanity_check_box
from .base_section import BaseSection



class FileSetSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReport) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2  # FileSet section is at depth 2

    def _build(self, depth):
        """Build the fileset section of the report"""
        self.report.add_page()
        self.report.add_section('FileSet Results', 'fileset_results')
        # Further fileset section building logic goes here
        for fs_name, fs_data in self.report_data.analysis.filesets.items():
            fs_plots = self.report_data.plots.filesets.get(fs_name, {})
            self.add_fileset_summary(fs_name, fs_data, fs_plots)
        else:
            self.report.add_paragraph("No FileSets found in the analysis data.")
        
    
    def add_fileset_summary(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
        self.report.add_subsection(f'FileSet: {fs_name}')
        # Add plots and summary information for the fileset
        # "temperature_hist": "calibration_outputs/1064_FW5/temperature_hist.pdf",
        # "humidity_hist": "calibration_outputs/1064_FW5/humidity_hist.pdf",
        # "timeseries": "calibration_outputs/1064_FW5/timeseries.pdf",
        # "ConvFactorSlopes_Comparison": "calibration_outputs/1064_FW5/ConvFactorSlopes_Comparison.pdf",
        # "ConvFactorIntercepts_Comparison": "calibration_outputs/1064_FW5/ConvFactorIntercepts_Comparison.pdf",
        # "pmVsRefPD_fitSlope_vs_Temperature": "calibration_outputs/1064_FW5/pmVsRefPD_fitSlope_vs_Temperature.pdf",
        # "pmVsRefPD_fitSlopes_and_Intercepts_vs_Run": "calibration_outputs/1064_FW5/pmVsRefPD_fitSlopes_and_Intercepts_vs_Run.pdf",
        # "pm_vs_RefPD": "calibration_outputs/1064_FW5/pm_vs_RefPD.pdf",
        # "pm_vs_RefPD_runs": "calibration_outputs/1064_FW5/pm_vs_RefPD_runs.pdf",
        # "pm_vs_LaserSetting": "calibration_outputs/1064_FW5/pm_vs_LaserSetting.pdf",
        # "RefPD_vs_LaserSetting": "calibration_outputs/1064_FW5/RefPD_vs_LaserSetting.pdf",
        # "Pedestals_Histogram": "calibration_outputs/1064_FW5/Pedestals_Histogram.pdf",
        # "Pedestals_vs_runindex": "calibration_outputs/1064_FW5/Pedestals_vs_runindex.pdf",
        # "Pedestals_timeseries": "calibration_outputs/1064_FW5/Pedestals_timeseries.pdf"
        # "meta": {
        #   "wave_length": "1064",
        #   "filter_wheel": "FW5"
        # },
        # "analysis": {
        #   "lr_refpd_vs_pm": {
        #     "x_var": "ref_pd_mean",
        #     "y_var": "pm_mean",
        #     "slope": 175.05422076010103,
        #     "intercept": -0.297737538118902,
        #     "r_value": 0.999926454301069,
        #     "p_value": 5.44878253396974e-251,
        #     "stderr": 0.18621664782237968,
        #     "intercept_stderr": 0.06711493337579023
        #   },
        #   "pedestals": {
        #     "pm": {
        #       "mean": -0.056999999999999995,
        #       "std": 0.04776609676329017,
        #       "samples": 6,
        #       "weighted": true,
        #       "w_mean": -0.09294009352897036,
        #       "w_stderr": 2.5405550879008853e-09,
        #       "ndof": 5,
        #       "chi2": 98691164883230.89,
        #       "chi2_reduced": 19738232976646.18,
        #       "exec_error": false
        #     },
        #     "refpd": {
        #       "mean": 2.143e-06,
        #       "std": 3.6631025101681224e-07,
        #       "samples": 6,
        #       "weighted": true,
        #       "w_mean": 2.1244491076462225e-06,
        #       "w_stderr": 8.712523445015392e-08,
        #       "ndof": 5,
        #       "chi2": 14.214320779147814,
        #       "chi2_reduced": 2.8428641558295626,
        #       "exec_error": false
        #     }
        #   }
        # },
        # "files": {
        if fs_plots.pm_vs_RefPD:
            self.report.add_figure(calc_plot_path(fs_plots.pm_vs_RefPD), 
                                   description="Power Meter vs Ref PD with linear regression fit using data points from all runs",
                                   center=True)