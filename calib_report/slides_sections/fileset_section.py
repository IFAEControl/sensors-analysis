from reportlab.lib import colors
from ..helpers.data_holders import ReportData, Fileset, FileSetPlots
from ..helpers.paths import calc_plot_path
from base_report.base_report_slides import BaseReportSlides
from .base_section import BaseSection


class FileSetSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 2  # FileSet section is at depth 2

    def _build(self, depth):
        """Build the fileset section of the report"""
        items = self.report_data.analysis.filesets.items()
        for fs_name, fs_data in items:
            fs_plots = self.report_data.plots.filesets.get(fs_name)
            self.add_fileset_summary(fs_name, fs_data, fs_plots)
            self.add_fileset_pedestals_summary(fs_name, fs_data, fs_plots)
            self.add_fileset_acq_summary(fs_name, fs_data, fs_plots)
        if len(items) == 0:
            self.report.add_slide(
                'FileSets', 'No FileSets found in the analysis data')
            self.report.add_section('FileSets',
                                    x=self.init_x, y=self.init_y,
                                    width=self.end_x - self.init_x,
                                    anchor=f'filesets')

            self.report.add_badge(
                "No FileSets found in the analysis data.",
                description="The analysis data does not contain any FileSets. Please review the input data and analysis settings to ensure that FileSets are being correctly identified and included in the analysis.",
                level="Warning",
                x=self.init_x,
                y=self.init_y + 50,
                width=400,
            )

    def _add_acq_info_box(self, fs_name: str, fs_data: Fileset, init_x: float, init_y: float, width: float):
        # Acquisition info
        header = "Acquisition info"
        padding = 5

        hf = self.report.get_paragraph_frame(
            header,
            x=init_x + padding, y=init_y,
            width=width - 2 * padding,
        )
        acq_info_tab = [
            ['Parameter', 'Value'],
            ['Wavelength', f"{fs_data.meta.wave_length} nm"],
            ['Filter Wheel', fs_data.meta.filter_wheel],
            ['Number of Files', str(len(fs_data.files))],
            ['Elapsed Time',
                f"{fs_data.time_info.elapsed_time_s/60:.2f} minutes"],
        ]
        tab_f = self.report.get_table_frame(
            acq_info_tab,
            x=init_x + padding, y=hf.y - hf.height - padding,
            width=width - 2 * padding,
            zebra=True
        )
        f = self.report.add_rectangle(
            x=init_x, y=init_y,
            width=width, height=hf.height + tab_f.height + 3 * padding,
            fill_color=colors.HexColor("#f0f0f0"),
            stroke_color=colors.HexColor("#222222"),
            stroke_width=0.5
        )
        hf = self.report.add_paragraph(
            header,
            x=init_x + padding, y=init_y,
            width=width - 2 * padding,
        )
        tab_f = self.report.add_table(
            acq_info_tab,
            x=init_x + padding, y=hf.y - hf.height - padding,
            width=width - 2 * padding,
            zebra=True
        )
        return f

    def add_fileset_summary(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):

        self.report.add_slide(f'FileSet: {fs_name}', 'Fileset results')
        sf = self.report.add_section(f'FileSet: {fs_name}',
                                     x=self.init_x, y=self.init_y,
                                     width=self.end_x - self.init_x,
                                     anchor=f'fileset_{fs_name}')

        # add result tab left aligned to slide at the same height as section header

        tab = [
            ['Parameter', 'Value'],
            ['Slope', f"{fs_data.analysis.lr_refpd_vs_pm.slope:.3f} {self.units}/V"],
            ['Intercept',
                f"{fs_data.analysis.lr_refpd_vs_pm.intercept:.3f} {self.units}"],
            ['r-value', f"{fs_data.analysis.lr_refpd_vs_pm.r_value:.6f}"],
            ['p-value', f"{fs_data.analysis.lr_refpd_vs_pm.p_value:.4e}"],
            ['Slope stderr', f"{fs_data.analysis.lr_refpd_vs_pm.stderr:.3f}"],
            ['Intercept stderr',
                f"{fs_data.analysis.lr_refpd_vs_pm.intercept_stderr:.3f}"],
        ]

        tab_f = self.report.add_table(
            tab,
            x=self.end_x - 165 - 10,
            y=self.init_y,
            width=165,
            zebra=True,
        )

        # add text below header
        texts = [
            "We aggregate values of all runs for same wavelength and filter and do the linear regression of the values.",
            "We display: Time series of all values, Values of the linear regression, plot of the linear regression values compared to linregs of each run, plot of the aggregated values and the linear regression",
        ]

        text_width = min(560, tab_f.x - 2*10)

        par_w = 210
        f_list = self.report.add_paragraphs(
            texts,
            x=self.init_x,
            y=sf.y - sf.height - 7,
            width=text_width,
            height=150
        )
        # print(
        #     f"Paragraphs frame: x={f_list[0].x}, y={f_list[0].y}, width={f_list[0].width}, height={f_list[0].height}")

        # sc_ix = ts_w + 10

        plot_y = f_list[0].y - f_list[0].height - 10
        pf = self.report.add_plot(
            calc_plot_path(
                fs_plots.pmVsRefPD_fitSlopes_and_Intercepts_vs_Run_vert),
            x=self.init_x,
            y=plot_y,
            width=300,
            height=plot_y - 10
        )
        plot_y = min(plot_y, tab_f.y - tab_f.height - 10)
        plot_x = self.init_x + 300 + 10
        f = self.report.add_plot(
            calc_plot_path(fs_plots.pm_vs_RefPD),
            x=plot_x,
            y=plot_y,
            width=self.end_x - plot_x,
            height=plot_y - 10
        )

    def add_fileset_pedestals_summary(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):

        self.report.add_slide(f'FileSet: {fs_name} summary', 'Pedestals info')
        sf = self.report.add_subsection(f'FileSet: {fs_name} pedestals',
                                        x=self.init_x, y=self.init_y,
                                        width=self.end_x - self.init_x,
                                        anchor=f'fileset_{fs_name}_pedestals')

        col1_width = 370
        col1_end = col1_width + self.init_x
        col2_start = col1_end + 10
        col2_width = self.end_x - col2_start

        text = "At each run file, the first and last measurements are taken when the laser is off."
        pf = self.report.add_paragraph(
            text, x=self.init_x, y=sf.y - sf.height - 7, width=col1_width)

        pf = self.report.add_plot(
            calc_plot_path(fs_plots.pedestals_timeseries),
            x=self.init_x,
            y=pf.y - pf.height - 10,
            width=col1_width,
            height=220  # maximum height to leave space for the histogram
        )

        pf = self.report.add_plot(
            calc_plot_path(fs_plots.Pedestals_Histogram),
            x=self.init_x,
            y=pf.y - pf.height - 10,
            width=col1_width,
            height=pf.y - pf.height - 10 - self.end_y
        )

        # second column
        pm_ped_stats = fs_data.analysis.pedestals.get('pm')
        refpd_ped_stats = fs_data.analysis.pedestals.get('refpd')
        tab = [
            ['Parameter', 'PM', 'Ref PD'],
            ['Mean', f"{pm_ped_stats.mean:.3e} {self.units}", f"{refpd_ped_stats.mean:.3e} V"],
            ['Std Err', f"{pm_ped_stats.std:.3e} {self.units}", f"{refpd_ped_stats.std:.3e} V"],
            ['Number of Samples', str(pm_ped_stats.samples), str(refpd_ped_stats.samples)],
        ]
        if pm_ped_stats.weighted and refpd_ped_stats.weighted:
            tab.extend([
                ['Weighted Mean', f"{pm_ped_stats.w_mean:.3e} {self.units}", f"{refpd_ped_stats.w_mean:.3e} V"],
                ['Weighted Std Err', f"{pm_ped_stats.w_stderr:.3e} {self.units}", f"{refpd_ped_stats.w_stderr:.3e} V"],
                ['Chi2', f"{pm_ped_stats.chi2:.3e}", f"{refpd_ped_stats.chi2:.3e}"],
                ['Reduced Chi2', f"{pm_ped_stats.chi2_reduced:.3e}", f"{refpd_ped_stats.chi2_reduced:.3e}"],
                ['Ndof', str(pm_ped_stats.ndof), str(refpd_ped_stats.ndof)],]
            )
        t_f = self.report.add_table(
            tab,
            x = col2_start,
            y = self.init_y,
            width = 290,
            zebra=True,
            col_align=['left', 'center', 'center'],
            col_widths=[100, 100, 100]
        )

        pm_resol_replace = fs_data.files.get(list(fs_data.files.keys())[
                                             0]).data_preparation.pm_std_replacement_value
        if pm_resol_replace:
            texts = [
                f"The power meter (PM) may provide values of pedestals with std value of 0. In order to do weighted means, for values with std = 0, we use the value of the pm resolution ({pm_resol_replace}) instead of the std. This behaviour can be disabled when analyzing the files. The resolution depends on the scale of the power meter and changes from fileset to fileset."
                # "In this plot we analyze the pedestals, by doing the average for each run file in the fileset and compare it to the mean and std of the whole fileset pedestals."
            ]
        else:
            texts = [
                "The power meter (PM) may provide values of pedestals with std value of 0. On the analysis settings it was set to not replace zero stds with the resolution value, so the weighted means only uses values with non-zero stds. This can lead to some runs not being included in the weighted mean calculation if they have zero stds in their pedestals. The resolution depends on the scale of the power meter and changes from fileset to fileset."
                # "In this plot we analyze the pedestals, by doing the average for each run file in the fileset and compare it to the mean and std of the whole fileset pedestals."
            ]
        prgr_start_x = t_f.x + t_f.width + 10
        pr_d = self.report.add_paragraphs(
            texts,
            x=prgr_start_x,
            y=self.init_y,
            width=self.end_x - prgr_start_x,
            height= 300
        )

        pr_d = pr_d[-1]
        plot_y = min(pr_d.y - pr_d.height - 10, t_f.y - t_f.height - 10)
        self.report.add_plot(
            calc_plot_path(fs_plots.Pedestals_vs_runindex),
            x=col2_start,
            y=plot_y,
            width=col2_width,
            height=plot_y - self.end_y
        )


    def add_fileset_acq_summary(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):

        self.report.add_slide(
            f'FileSet: {fs_name} summary', 'Acquisition info')
        sf = self.report.add_subsection(f'FileSet: {fs_name} acquisition info',
                                        x=self.init_x, y=self.init_y,
                                        width=self.end_x - self.init_x,
                                        anchor=f'fileset_{fs_name}_acquisition_info')

        col1_start = self.init_x
        col1_width = 400
        col2_start = col1_start + col1_width + 10
        col2_width = self.end_x - col2_start

        f = self.report.add_plot(
            calc_plot_path(fs_plots.timeseries),
            x=col2_start,
            y=self.init_y,
            width=col2_width,
            height=self.init_y - 10
        )

        info_f = self._add_acq_info_box(
            fs_name,
            fs_data,
            col1_start,
            init_y=sf.y - sf.height - 7,
            width=180)
        paragraphs = [
            "Values of the fileset acquisition.",
            "Timeseries of all the values acquired on the fileset",
            "The power meter provides the number of samples acquired for each value stored on the run files."
        ]
        prg_f = self.report.add_paragraphs(
            paragraphs,
            x=info_f.x + info_f.width + 10,
            y=info_f.y,
            width=col1_width - info_f.width - info_f.x - 10,
            height=300
        )
        prg_f = prg_f[-1]

        samples_y = min(info_f.y - info_f.height - 10, prg_f.y - prg_f.height - 10)
        self.report.add_plot(
            calc_plot_path(fs_plots.pm_samples_full),
            x=col1_start,
            y=samples_y,
            width=col1_width,
            height=samples_y - self.end_y
        )

    #     self.report.add_plot(calc_plot_path(fs_plots.pm_vs_RefPD),
    #                             caption="Power Meter vs Ref PD with linear regression fit using data points from all runs",
    #                             center=True)
    #     self.report.add_subsubsection(f"{fs_data.meta.wave_length} - {fs_data.meta.filter_wheel} Results")
    #     self.report.add_table(tab, keep_together=True,description="Summary of FileSet metadata", zebra=True, headers='both')

    #     self._add_linreg_section(fs_name, fs_data, fs_plots)
    #     self._add_pedestal_section(fs_name, fs_data, fs_plots)
    #     self._compare_files_section(fs_name, fs_data, fs_plots)

    # def _add_linreg_section(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
    #     self.report.add_subsubsection("Linear Regression: Ref PD vs Power Meter", include_in_toc=False)
    #     self.report.add_paragraph("Linear Regression Results for Ref PD vs Power Meter" \
    #     " using all data points from all runs in the FileSet:")
    #     self.report.add_table(tab, keep_together=True,
    #                           description="Summary of Linear regression results", zebra=True,
    #                           headers='both', center=True)
    # def _add_pedestal_section(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
    #     self.report.add_subsubsection("Pedestal Analysis", include_in_toc=False)
    #     self.report.add_paragraph("Pedestal Analysis Results:")
    #     pm_ped_stats = fs_data.analysis.pedestals.get('pm')
    #     refpd_ped_stats = fs_data.analysis.pedestals.get('refpd')
    #     tab = [
    #         ['Parameter', 'PM', 'Ref PD'],
    #         ['Mean', f"{pm_ped_stats.mean:.6f} {self.units}", f"{refpd_ped_stats.mean:.6e} V"],
    #         ['Std Err', f"{pm_ped_stats.std:.6f} {self.units}", f"{refpd_ped_stats.std:.6e} V"],
    #         ['Number of Samples', str(pm_ped_stats.samples), str(refpd_ped_stats.samples)],
    #     ]
    #     if pm_ped_stats.weighted and refpd_ped_stats.weighted:
    #         tab.extend([
    #             ['Weighted Mean', f"{pm_ped_stats.w_mean:.6f} {self.units}", f"{refpd_ped_stats.w_mean:.6e} V"],
    #             ['Weighted Std Err', f"{pm_ped_stats.w_stderr:.6f} {self.units}", f"{refpd_ped_stats.w_stderr:.6e} V"],
    #             ['Chi2', f"{pm_ped_stats.chi2:.3f}", f"{refpd_ped_stats.chi2:.3f}"],
    #             ['Reduced Chi2', f"{pm_ped_stats.chi2_reduced:.3f}", f"{refpd_ped_stats.chi2_reduced:.3f}"],
    #             ['Ndof', str(pm_ped_stats.ndof), str(refpd_ped_stats.ndof)],]
    #         )
    #     self.report.add_table(tab, keep_together=True,
    #                           description="Summary of Pedestal statistics", zebra=True,
    #                           headers='both', center=True)

    #     if pm_ped_stats.weighted and pm_ped_stats.chi2_reduced > 10.0:
    #         extra_text = ""
    #         if not self.report_data.meta.calling_arguments.do_not_replace_zero_pm_stds:
    #             extra_text = ' In the analysis settings, you\'ve set to replace zero PM stds with the ' \
    #             'resolution value which is usually very small and can lead to high Chi2 values.'
    #         self.report.add_warning_box("The weighted pedestal fit for the Power Meter shows a high reduced Chi2 value, indicating a poor fit." \
    #         " Consider reviewing the pedestal data for potential outliers or inconsistencies." + extra_text)

    #     self.report.add_figure(calc_plot_path(fs_plots.pedestals_timeseries),
    #                            center=True,
    #                            caption="Pedestal values over time for all runs in the FileSet",
    #                            width_mm=120)
    #     self.report.add_figure(calc_plot_path(fs_plots.Pedestals_Histogram),
    #                            center=True,
    #                            caption="Histogram of Pedestal values for all runs in the FileSet",
    #                            width_mm=120)

    # def _compare_files_section(self, fs_name: str, fs_data: Fileset, fs_plots: FileSetPlots):
    #     self.report.add_subsubsection("Comparison of Calibration Files", include_in_toc=False)
    #     self.report.add_paragraph("In next plot we can compare the values of the linear regression when " \
    #     "using each individual calibration file in the FileSet with the linear regression using all data points together.")
    #     self.report.add_figure(calc_plot_path(fs_plots.pmVsRefPD_fitSlopes_and_Intercepts_vs_Run),
    #                            center=True,
    #                            caption="Comparison of slopes and intercepts from individual calibration files vs FileSet linear regression")
