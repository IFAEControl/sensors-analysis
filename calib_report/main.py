import os
import argparse

from .helpers.paths import calc_paths, ReportPaths
from .sections.full_report import FullReport
from .helpers.logger import get_logger, add_file_handler
from .config import config

logger = get_logger()
    
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

    add_file_handler("calibration_report.log")
    args = parser.parse_args()

    report_paths:ReportPaths = calc_paths(args.input_path, args.output_path)
    config.paths = report_paths
    report = FullReport(
        report_paths=report_paths,
    )
    report.build()

if __name__ == "__main__":
    gen_report()