import os
import argparse
from datetime import datetime, timezone
now = datetime.now(timezone.utc)

from .helpers import get_logger
from .elements.characterization import Characterization
from .elements.sanity_checks import SanityChecks
from .config import config
now_libs = datetime.now(timezone.utc)
logger = get_logger()


def main():
    logger.info("Virgo Instrumented Baffles Characterization script")

    parser = argparse.ArgumentParser(description="Virgo Instrumented Baffles Characterization script")
    parser.add_argument("char_files_path", help="Path to characterization files folder or zip file")
    parser.add_argument("--plot-format", "-f", choices=["pdf", "svg", "png"], default="pdf", help="Plot file format (default: pdf)")
    parser.add_argument("--output-path", "-o", help="Output path (default: './output/<name_of_char_files>')")
    parser.add_argument("--log-file", "-l", action="store_true", help="Stores log at output folder(default: None, logs only to console)")
    parser.add_argument("--overwrite", "-w", action="store_true", help="Overwrite output directory if it exists")
    parser.add_argument("--no-plots", "-n", action="store_true", help="Do not generate plots")
    parser.add_argument("--no-gen-report", action="store_true", help="Do not generate characterization report")
    args = parser.parse_args()

    if args.plot_format:
        config.plot_output_format = args.plot_format
    if args.no_plots:
        config.generate_plots = False

    characterization = Characterization(args)
    if args.log_file:
        log_file_path = os.path.join(characterization.output_path, f"{now.strftime('%Y%m%d_%H%M%S')}_characterization.log")
        logger.info("Logging to file: %s", log_file_path)
        from .helpers import add_file_handler
        add_file_handler(log_file_path)
    logger.info("Characterization files path: %s", args.char_files_path)
    logger.info("Output path: %s", characterization.output_path)
    logger.info("Starting characterization analysis at %s", now.isoformat())

    characterization.load_characterization_files()
    config.summary_file_name = f"{characterization.meta['charact_id']}_extended.json"
    characterization.analyze()
    if config.generate_plots:
        characterization.generate_plots()
    san = SanityChecks(characterization)
    san.run_checks()
    characterization.export_data_summary({'sanity_checks': san.results})
    if not args.no_gen_report:
        from characterization_report.main import build_report
        build_report(characterization.reports_path)

    now_end = datetime.now(timezone.utc)
    logger.info("Finished characterization analysis at %s", now_end.isoformat())
    logger.info("Total duration: %s", str(now_end - now))
    logger.info("Total duration loading libraries: %s", str(now_libs - now))


if __name__ == "__main__":
    main()
