from __future__ import annotations

from base_report.base_report_slides import BaseReportSlides

from ..helpers.data_holders import ReportData
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
