from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides

from ..helpers.data_holders import ReportData
from ..helpers.paths import calc_plot_path
from ..report_elements import add_characterization_overview, add_power_conversion_note
from .base_section import BaseSection


class CharacterizationOverviewSection(BaseSection):
    def __init__(self, report_data: ReportData, report: BaseReportSlides) -> None:
        super().__init__(report_data, report)
        self.section_depth = 1

    def _build(self, depth: int) -> None:
        power_unit = "W"
        if self.report_data.calibration and self.report_data.calibration.power_unit:
            power_unit = self.report_data.calibration.power_unit
        elif self.report_data.meta.calibration and self.report_data.meta.calibration.power_unit:
            power_unit = self.report_data.meta.calibration.power_unit

        self.report.add_slide()
        frame = self.report.get_active_area()
        add_characterization_overview(
            self.report,
            self.report_data,
            frame,
            wavelength="1064",
            title="1064 board characterization Power vs adc counts",
            mode="power",
            power_unit=power_unit,
            show_note=True,
        )
        self.report.add_slide()
        frame = self.report.get_active_area()
        add_characterization_overview(
            self.report,
            self.report_data,
            frame,
            wavelength="532",
            title="532 board characterization Power vs adc counts",
            mode="power",
            power_unit=power_unit,
            show_note=False,
        )
        self.report.add_slide()
        frame = self.report.get_active_area()
        add_characterization_overview(
            self.report,
            self.report_data,
            frame,
            wavelength="532",
            title="532 board characterization RefPD V vs adc counts",
            mode="refpd",
            power_unit=power_unit,
            show_note=False,
        )
        self._add_power_range_slide()
        self.report.add_slide()
        frame = self.report.get_active_area()
        add_power_conversion_note(
            self.report,
            self.report_data,
            frame,
            power_unit=power_unit,
        )

        self.report.add_slide()
        frame = self.report.get_active_area()
        add_characterization_overview(
            self.report,
            self.report_data,
            frame,
            wavelength="1064",
            title="1064 board characterization RefPD V vs adc counts",
            mode="refpd",
            power_unit=power_unit,
            show_note=False,
        )

    def _add_power_range_slide(self) -> None:
        self.report.add_slide("Power Range")
        self.report.add_section(
            "Power Range",
            x=self.init_x,
            y=self.init_y,
            width=self.end_x - self.init_x,
            anchor="power_range",
            toc=True,
        )

        top_y = self.lf.y - self.lf.height - 12
        plot_width = (self.end_x - self.init_x - 14) / 2
        plot_height = top_y - self.end_y
        if plot_height <= 0:
            return

        left_plot = self.report_data.plots.power_range_by_sensor_1064
        right_plot = self.report_data.plots.power_range_by_sensor_532

        if left_plot:
            self.report.add_plot(
                path=calc_plot_path(left_plot),
                x=self.init_x,
                y=top_y,
                width=plot_width,
                height=plot_height,
            )
        else:
            self.report.add_paragraph(
                "Missing plot: power_range_by_sensor_1064",
                x=self.init_x,
                y=top_y,
                width=plot_width,
                font_size=10,
            )

        right_x = self.init_x + plot_width + 14
        if right_plot:
            self.report.add_plot(
                path=calc_plot_path(right_plot),
                x=right_x,
                y=top_y,
                width=plot_width,
                height=plot_height,
            )
        else:
            self.report.add_paragraph(
                "Missing plot: power_range_by_sensor_532",
                x=right_x,
                y=top_y,
                width=plot_width,
                font_size=10,
            )
