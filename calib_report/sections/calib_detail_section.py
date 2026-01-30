
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
            description="Timeseries of acquisition values",
            center=True,
            width_mm=140)

        self.report.add_paragraph(
            "Next figure shows the evolution of the pedestals during the whole calibration acquisition."
        )
        self.report.add_figure(
            calc_plot_path(self.report_data.plots.pedestals_timeseries),
            description="Timeseries of pedestals values",
            center=True,
            width_mm=125)

