
from ..helpers.data_holders import ReportData, Fileset, FileSetPlots
from ..helpers.paths import calc_plot_path
from base_report.base_report import BaseReport
from ..report_elements.sanity_checks import add_sanity_check_box
from .base_section import BaseSection



class CalibDetailSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReport) -> None:
        super().__init__(report_data, report)
        self.section_depth = 1  # FileSet section is at depth 2

    def _build(self, depth):
        """Build the fileset section of the report"""
        self.report.add_page()
        self.report.add_section('Calibration', 'calibration_detailed_results')
        # Further fileset section building logic goes here
        self._acquisition_conditions()
        self._timeseries()

    def _acquisition_conditions(self):
        pass
    def _timeseries(self):
        self.report.add_subsection('Acquisition timeseries', 'cal_acq_timeseries')
        self.report.add_paragraph(
            "The following figure shows the evolution of the acquisition values"
            " during the whole calibration acquisition."
            " Temperature and humidity values are also included."
        )
        self.report.add_figure(
            calc_plot_path(self.report_data.plots.timeseries),
            caption="Timeseries of acquisition values",
            center=True,
            width_mm=140)

        self.report.add_paragraph(
            "Next figure shows the evolution of the pedestals during the whole calibration acquisition."
        )
        self.report.add_figure(
            calc_plot_path(self.report_data.plots.pedestals_timeseries),
            caption="Timeseries of pedestals values",
            center=True,
            width_mm=125)

        ped_stats = self.report_data.analysis.pedestals
        pm = ped_stats.get('pm')
        refpd = ped_stats.get('refpd')
        if pm and refpd:
            def _fmt(stat):
                if stat.weighted and stat.w_mean is not None and stat.w_stderr is not None:
                    return f'{stat.w_mean:.4e} +/- {stat.w_stderr:.2e} (weighted)'
                if stat.mean is not None and stat.std is not None:
                    return f'{stat.mean:.4e} +/- {stat.std:.2e}'
                return 'N/A'
            self.report.add_paragraph(
                "Global pedestal statistics for the full calibration:"
            )
            ped_table = [
                ['Measurement', 'Calibration pedestal'],
                [f'PM ({self.units})', _fmt(pm)],
                ['RefPD (V)', _fmt(refpd)],
            ]
            self.report.add_table(
                ped_table,
                keep_together=True,
                center=True,
                zebra=True,
                headers='col'
            )

