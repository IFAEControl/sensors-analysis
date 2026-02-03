
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
        ix = 0
        for fs_name, fs_data in self.report_data.analysis.filesets.items():
            fs_plots = self.report_data.plots.filesets.get(fs_name)
            if ix > 0:
                self.report.add_page()
            self.add_fileset_summary(fs_name, fs_data, fs_plots)
            ix = 1
        else:
            self.report.add_paragraph("No FileSets found in the analysis data.")
        
    
    def add_fileset_summary(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
        self.report.add_subsection(f'FileSet: {fs_name}', f'fileset_{fs_name}')

        if fs_plots.pm_vs_RefPD:
            self.report.add_figure(calc_plot_path(fs_plots.pm_vs_RefPD), 
                                   caption="Power Meter vs Ref PD with linear regression fit using data points from all runs",
                                   center=True)
        self.report.add_subsubsection(f"{fs_data.meta.wave_length} - {fs_data.meta.filter_wheel} Results")
        tab = [
            ['Parameter', 'Value'],
            ['Wavelength', f"{fs_data.meta.wave_length} nm"],
            ['Filter Wheel', fs_data.meta.filter_wheel],
            ['Number of Files', str(len(fs_data.files))],
            ['Elapsed Time', f"{fs_data.time_info.elapsed_time_s/60:.2f} minutes"],
        ]
        self.report.add_table(tab, keep_together=True,description="Summary of FileSet metadata", zebra=True, headers='both')

        self._add_linreg_section(fs_name, fs_data, fs_plots)
        self._add_pedestal_section(fs_name, fs_data, fs_plots)
        self._compare_files_section(fs_name, fs_data, fs_plots)

    def _add_linreg_section(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
        self.report.add_subsubsection("Linear Regression: Ref PD vs Power Meter", include_in_toc=False)
        tab = [
            ['Parameter', 'Value'],
            ['Slope', f"{fs_data.analysis.lr_refpd_vs_pm.slope:.3f} {self.units}/V"],
            ['Intercept', f"{fs_data.analysis.lr_refpd_vs_pm.intercept:.3f} {self.units}"],
            ['r-value', f"{fs_data.analysis.lr_refpd_vs_pm.r_value:.6f}"],
            ['p-value', f"{fs_data.analysis.lr_refpd_vs_pm.p_value:.4e}"],
            ['Slope stderr', f"{fs_data.analysis.lr_refpd_vs_pm.stderr:.3f}"],
            ['Intercept stderr', f"{fs_data.analysis.lr_refpd_vs_pm.intercept_stderr:.3f}"],
        ]
        self.report.add_paragraph("Linear Regression Results for Ref PD vs Power Meter" \
        " using all data points from all runs in the FileSet:")
        self.report.add_table(tab, keep_together=True,
                              description="Summary of Linear regression results", zebra=True, 
                              headers='both', center=True)
    def _add_pedestal_section(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
        self.report.add_subsubsection("Pedestal Analysis", include_in_toc=False)
        self.report.add_paragraph("Pedestal Analysis Results:")
        pm_ped_stats = fs_data.analysis.pedestals.get('pm')
        refpd_ped_stats = fs_data.analysis.pedestals.get('refpd')
        tab = [
            ['Parameter', 'PM', 'Ref PD'],
            ['Mean', f"{pm_ped_stats.mean:.6f} {self.units}", f"{refpd_ped_stats.mean:.6e} V"],
            ['Std Err', f"{pm_ped_stats.std:.6f} {self.units}", f"{refpd_ped_stats.std:.6e} V"],
            ['Number of Samples', str(pm_ped_stats.samples), str(refpd_ped_stats.samples)],
        ]
        if pm_ped_stats.weighted and refpd_ped_stats.weighted:
            tab.extend([
                ['Weighted Mean', f"{pm_ped_stats.w_mean:.6f} {self.units}", f"{refpd_ped_stats.w_mean:.6e} V"],
                ['Weighted Std Err', f"{pm_ped_stats.w_stderr:.6f} {self.units}", f"{refpd_ped_stats.w_stderr:.6e} V"],
                ['Chi2', f"{pm_ped_stats.chi2:.3f}", f"{refpd_ped_stats.chi2:.3f}"],
                ['Reduced Chi2', f"{pm_ped_stats.chi2_reduced:.3f}", f"{refpd_ped_stats.chi2_reduced:.3f}"],
                ['Ndof', str(pm_ped_stats.ndof), str(refpd_ped_stats.ndof)],]
            )
        self.report.add_table(tab, keep_together=True,
                              description="Summary of Pedestal statistics", zebra=True, 
                              headers='both', center=True)
        
        if pm_ped_stats.weighted and pm_ped_stats.chi2_reduced > 10.0:
            extra_text = ""
            if not self.report_data.meta.calling_arguments.do_not_replace_zero_pm_stds:
                extra_text = ' In the analysis settings, you\'ve set to replace zero PM stds with the ' \
                'resolution value which is usually very small and can lead to high Chi2 values.'
            self.report.add_warning_box("The weighted pedestal fit for the Power Meter shows a high reduced Chi2 value, indicating a poor fit." \
            " Consider reviewing the pedestal data for potential outliers or inconsistencies." + extra_text)
        
        self.report.add_figure(calc_plot_path(fs_plots.pedestals_timeseries),
                               center=True,
                               caption="Pedestal values over time for all runs in the FileSet",
                               width_mm=120)
        self.report.add_figure(calc_plot_path(fs_plots.Pedestals_Histogram),
                               center=True,
                               caption="Histogram of Pedestal values for all runs in the FileSet",
                               width_mm=120)
    
    def _compare_files_section(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
        self.report.add_subsubsection("Comparison of Calibration Files", include_in_toc=False)
        self.report.add_paragraph("In next plot we can compare the values of the linear regression when " \
        "using each individual calibration file in the FileSet with the linear regression using all data points together.")
        self.report.add_figure(calc_plot_path(fs_plots.pmVsRefPD_fitSlopes_and_Intercepts_vs_Run),
                               center=True,
                               caption="Comparison of slopes and intercepts from individual calibration files vs FileSet linear regression")