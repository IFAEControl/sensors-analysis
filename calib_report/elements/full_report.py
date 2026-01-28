import json

from base_report.base_report import BaseReport
from .data_holders import ReportData


class FullReport:
    def __init__(self, report_paths: ReportPaths, depth:int = 0) -> None:
        self.report_paths = report_paths
        self.depth = depth
        self._data:ReportData|None = None
        self.load_data()

        self.report = BaseReport(output_path=report_paths.report_path,
                                 logo_path=report_paths.logo_path,
                                 title="Calibration Report",
                                 subtitle="Generated Calibration Analysis Report",
                                 serial_number=self.data.meta.calib_id)
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
    
    def build(self):
        """Build the full report"""
        self.report.add_section('Calibration Summary', 'summary')
        # Further report building logic goes here

        self.report.build()