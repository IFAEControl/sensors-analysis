import os
import argparse

from .helpers import calc_paths, ReportPaths
from .elements.full_report import FullReport

    
    
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

    report_paths:ReportPaths = calc_paths(args.input_path, args.output_path)
    report = FullReport(
        report_paths=report_paths,
    )
    report.build()

if __name__ == "__main__":
    gen_report()