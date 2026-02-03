from dataclasses import dataclass, field

from .helpers.paths import ReportPaths

@dataclass
class CalibReportConfig:
    paths: ReportPaths = field(default_factory=ReportPaths)




config = CalibReportConfig(paths=ReportPaths(
    input_file="",
    calib_anal_files_path="",
    report_path="",
    output_path="",
))