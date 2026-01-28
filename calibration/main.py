import os
import argparse
from datetime import datetime, timezone
now = datetime.now(timezone.utc)

from .helpers import get_logger
from .elements.calibration import Calibration
from .elements.sanity_checks import SanityChecks
from .config import config
now_libs = datetime.now(timezone.utc)
logger = get_logger()


def main():
    logger.info("Virgo Instrumented Baffles Calibration script")

    parser = argparse.ArgumentParser(description="Virgo Instrumented Baffles Calibration script")
    parser.add_argument("calib_files_path", help="Path to calibration files folder or zip file")
    parser.add_argument("--plot-format", "-f", choices=["pdf", "svg", "png"], default="pdf", help="Plot file format (default: pdf)")
    parser.add_argument("--output-path", "-o", help="Output path (default: './output/<name_of_calib_files>')")
    parser.add_argument("--log-file", "-l", action="store_true", help="Stores log at output folder(default: None, logs only to console)")
    parser.add_argument("--overwrite", "-w", action="store_true", help="Overwrite output directory if it exists")
    parser.add_argument("--no-plots", "-n", action="store_true", help="Do not generate plots")
    # parser.add_argument("--do_not_sub_pedestals", "-d", action="store_true", help="Do not subtract pedestals from data")
    args = parser.parse_args()

    if args.plot_format:
        config.plot_output_format = args.plot_format
    # if args.do_not_sub_pedestals:
    #     config.substract_pedestals = False
    if args.no_plots:
        config.generate_plots = False

    calibration = Calibration(args)

    if args.log_file:
        log_file_path = os.path.join(calibration.output_path, f"{now.strftime('%Y%m%d_%H%M%S')}_calibration.log")
        logger.info("Logging to file: %s", log_file_path)
        from .helpers import add_file_handler
        add_file_handler(log_file_path)
    logger.info("Calibration files path: %s", args.calib_files_path)
    logger.info("Output path: %s", calibration.output_path)
    logger.info("Starting calibration analysis at %s", now.isoformat())

    calibration.load_calibration_files()
    calibration.analyze()
    calibration.generate_plots()
    san = SanityChecks(calibration)
    san.run_checks()
    calibration.export_calib_data_summary({'sanity_checks': san.results})
    try:
        with open(os.path.join(calibration.reports_path, 'sanity_checks_results.json'), 'w', encoding='utf-8') as f:
            import json
            json.dump(san.results, f, indent=2)
    except Exception as e:
        import pprint
        logger.error("Failed to save sanity checks results: %s", str(e))
        pprint.pprint(san.results)
    now_end = datetime.now(timezone.utc)
    logger.info("Finished calibration analysis at %s", now_end.isoformat())
    logger.info("Total duration: %s", str(now_end - now))
    logger.info("Total duration loading libraries: %s", str(now_libs - now))


if __name__ == "__main__":
    main()
