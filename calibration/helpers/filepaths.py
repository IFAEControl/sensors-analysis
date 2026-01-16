"""Module for setting up file paths for calibration data."""
import os
import sys
import tempfile
import zipfile
from calibration.helpers import get_logger
logger = get_logger()

def setup_paths(calib_files_path, output_path=None):
    """
    Setup file paths for calibration input data files and output directory.

    Implements sanity checks and handles zip file extraction if necessary.

    Args:
        calib_files_path: Path to calibration files
        output_path: Optional output path. Defaults to './output/<name_of_calib_files>'
    """
    if not os.path.exists(calib_files_path):
        logger.error("Calibration files path '%s' does not exist.", calib_files_path)
        sys.exit(1)

    files_path = None
    base_name = None
    if os.path.isdir(calib_files_path):
        if not os.listdir(calib_files_path):
            logger.error("Calibration files directory '%s' is empty.", calib_files_path)
            sys.exit(1)
        files_path = calib_files_path
        base_name = os.path.basename(os.path.normpath(calib_files_path))
    else:
        if not calib_files_path.lower().endswith('.zip'):
            logger.error("Calibration files path '%s' is not a directory or a zip file.", calib_files_path)
            sys.exit(1)
        files_path = tempfile.mkdtemp()
        base_name = os.path.splitext(os.path.basename(calib_files_path))[0]
        with zipfile.ZipFile(calib_files_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                zip_ref.extract(member, files_path)
                # Move files from subdirectories to root
                source = os.path.join(files_path, member)
                if os.path.isfile(source):
                    dest = os.path.join(files_path, os.path.basename(member))
                    if source != dest:
                        os.rename(source, dest)

    if output_path is None:
        output_path = f'./output/{base_name}'
    os.makedirs(output_path, exist_ok=True)

    logger.info("Calibration files path: %s", files_path)
    logger.info("Output path: %s", output_path)

    return files_path, output_path