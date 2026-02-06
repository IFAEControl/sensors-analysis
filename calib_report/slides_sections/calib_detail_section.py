
from reportlab.lib import colors
from ..helpers.data_holders import ReportData, Fileset, FileSetPlots
from ..helpers.paths import calc_plot_path
from base_report.base_report_slides import BaseReportSlides
from ..report_elements.sanity_checks import add_sanity_check_box
from .base_section import BaseSection



class CalibDetailSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 1  # FileSet section is at depth 2

    def _build(self, depth):
        """Build the fileset section of the report"""
        self.report.add_slide('Calibration', 'Full calibration acquisition values')
        f = self.report.get_active_area()
        self.report.add_section('Calibration', 
                                x=f.x, y=f.y,
                                width=f.width,
                                anchor='calibration_detailed_results')
        # Further fileset section building logic goes here
        self._acquisition_conditions()
        self._timeseries()

    def _acquisition_conditions(self):
        pass
    def _timeseries(self):
        init_y = self.lf.y - self.lf.height - 20
        self.report.add_paragraph(
            text="The following figure shows the evolution of the acquisition values"
            " during the whole calibration acquisition."
            " Temperature and humidity values are also included.",
            x=self.init_x,
            y=init_y,
            width=460
        )
        y = self.lf.y - self.lf.height - 20
        self.report.add_plot(
            calc_plot_path(self.report_data.plots.timeseries),
            x= self.init_x,
            y = y,
            height = y -10,
            width=460
            )

        self.report.add_rectangle(
            x=480,
            y = init_y,
            width=0,
            height= init_y -10,
            fill_color=colors.white,
            stroke_color=colors.grey,
            stroke_width=0.5
        )
        # self.report.add_paragraph(
        #     "Next figure shows the evolution of the pedestals during the whole calibration acquisition."
        # )
        self.report.add_paragraph(
            text="Next figure shows the evolution of the pedestals during the whole calibration acquisition.",
            x=490,
            y=init_y,
            width=460
        )        
        self.report.add_plot(
            calc_plot_path(self.report_data.plots.pedestals_timeseries),
            x= 490,
            y = self.lf.y - self.lf.height - 20,
            width=460,
            height= self.lf.y - self.lf.height -10
            )

