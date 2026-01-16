import os
import argparse
from datetime import datetime, timezone

from .helpers import get_logger
from .elements.calibration import Calibration

logger = get_logger()


    
    


if __name__ == "__main__":
    logger.info("Virgo Instrumented Baffles Calibration script")
    
    parser = argparse.ArgumentParser(description="Virgo Instrumented Baffles Calibration script")
    parser.add_argument("calib_files_path", help="Path to calibration files folder or zip file")
    parser.add_argument("--output-path", "-o", help="Output path (default: './output/<name_of_calib_files>')")
    parser.add_argument("--log-file", "-l", action="store_true", help="Stores log at output folder(default: None, logs only to console)")
    
    args = parser.parse_args()
    
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
    calibration.export_calib_data_summary()
