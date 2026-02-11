import os
import argparse

from .helpers.paths import calc_paths, ReportPaths
# from .sections.full_report import FullReport
from .slides_sections.full_report import FullReport as FullSlidesReport
from .helpers.logger import get_logger, add_file_handler
from .config import config

logger = get_logger()
    
def build_report(input_path: str, output_path: str | None = None) -> None:
    add_file_handler("calibration_report.log")
    report_paths:ReportPaths = calc_paths(input_path, output_path)
    config.paths = report_paths
    # Report as a A4 document using platypus
    # report = FullReport(
    #     report_paths=report_paths,
    # )
    # report.build()
    report = FullSlidesReport(
        report_paths=report_paths,
    )
    report.build(depth=0)  # full depth

def gen_report() -> None:
    parser = argparse.ArgumentParser(description="Generate a calibration PDF report")
    parser.add_argument(
        "input_path",
        help="Path to the input file or directory used to build the report",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="Output PDF file path",
        default=None,
    )

    args = parser.parse_args()

    build_report(args.input_path, args.output_path)

if __name__ == "__main__":
    gen_report()
