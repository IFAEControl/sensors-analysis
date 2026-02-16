from __future__ import annotations

import argparse

from .config import config
from .helpers import ReportPaths, add_file_handler, calc_paths, get_logger

logger = get_logger()


def build_report(input_path: str, output_path: str | None = None) -> None:
    add_file_handler("crossboard_report.log")
    report_paths: ReportPaths = calc_paths(input_path, output_path)
    config.paths = report_paths

    logger.info("Crossboard report scaffold loaded")
    logger.info("Input summary: %s", report_paths.input_file)
    logger.info("Output path: %s", report_paths.output_path)
    logger.info("No report sections implemented yet for crossboard_report")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a crossboard PDF report")
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
    args = parser.parse_args()

    build_report(args.input_path, args.output_path)


if __name__ == "__main__":
    main()
