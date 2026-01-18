import os
import argparse
from datetime import datetime, timezone

from .helpers import get_logger, file_manage
from .elements.calibration import Calibration

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
    args = parser.parse_args()

    file_manage.set_plot_output_format(args.plot_format)
    file_manage.set_generate_plots(not args.no_plots)

    calibration = Calibration(args)
    now = datetime.now(timezone.utc)
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
    calibration.sanity_checks()
    calibration.export_calib_data_summary()


if __name__ == "__main__":
    main()
