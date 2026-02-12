from dataclasses import dataclass, field

from .helpers.paths import ReportPaths


@dataclass
class CharacterizationReportConfig:
    paths: ReportPaths = field(
        default_factory=lambda: ReportPaths(
            input_file="",
            char_anal_files_path="",
            report_path="",
            output_path="",
        )
    )


config = CharacterizationReportConfig()
