import json

from base_report.base_report import BaseReport
from ..helpers.data_holders import ReportData

from .summary_section import SummarySection
from .sanity_checks import SanityChecksSection
from .fileset_section import FileSetSection
from .toc_section import ToCSection
from .calib_detail_section import CalibDetailSection


class FullReport:
    def __init__(self, report_paths: ReportPaths) -> None:
        self.report_paths = report_paths
        self._data:ReportData|None = None
        self.load_data()

        self.report = BaseReport(output_path=report_paths.report_path,
                                 logo_path=report_paths.logo_path,
                                 title="Calibration Report",
                                 subtitle="Generated Calibration Analysis Report",
                                 serial_number=self.data.meta.calib_id)
        self.sections = []

    @property
    def data(self) -> ReportData:
        """Return the report data"""
        if self._data is not None:
            return self._data
        raise ValueError("Report data not loaded yet.")
    
    def load_data(self):
        with open(self.report_paths.input_file, 'r') as f:
            json_data = json.load(f)
        self._data = ReportData.from_dict(json_data)
    
    def load_sections(self):
        """Load report sections"""

        self.sections.append(SummarySection(self.data, self.report))
        self.sections.append(ToCSection(self.data, self.report))
        self.sections.append(CalibDetailSection(self.data, self.report))
        self.sections.append(FileSetSection(self.data, self.report))
        # Load other sections as needed

        # last section always sanity checks
        self.sections.append(SanityChecksSection(self.data, self.report))

    def build(self, depth=0):
        """
        Build the full report
        depth = 0: full depth
        depth = 1: only calibration results
        depth = 2: up to fileset results
        depth = 3: up to file results

        From depth > 1, ToC is included 
        """
        self.load_sections()
        for section in self.sections:
            section.build(depth)

        self.report.build()