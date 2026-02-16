from dataclasses import dataclass, field

from .helpers.paths import ReportPaths


@dataclass
class CrossboardReportConfig:
    paths: ReportPaths = field(
        default_factory=lambda: ReportPaths(
            root_path="",
            input_file="",
            output_path="",
        )
    )


config = CrossboardReportConfig()
