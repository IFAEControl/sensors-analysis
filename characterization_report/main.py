from __future__ import annotations

import argparse

from .config import config
from .helpers import ReportPaths, add_file_handler, calc_paths, get_logger
from .slides_sections.full_report import FullReport

logger = get_logger()


def build_report(input_path: str, output_path: str | None = None, strict_plots: bool = False) -> None:
    add_file_handler("characterization_report.log")
    report_paths: ReportPaths = calc_paths(input_path, output_path, strict_plots=strict_plots)
    config.paths = report_paths

    report = FullReport(report_paths=report_paths)
    report.build(depth=0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a characterization PDF report")
    parser.add_argument(
        "input_path",
        help="Path to the input file or directory used to build the report",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="Output PDF directory path",
        default=None,
    )
    parser.add_argument(
        "--strict-plots",
        action="store_true",
        help="Fail report generation if plots path does not exist (CI mode).",
    )
    args = parser.parse_args()

    build_report(args.input_path, args.output_path, strict_plots=args.strict_plots)


if __name__ == "__main__":
    main()
