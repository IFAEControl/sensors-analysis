"""Module for setting up file paths for calibration data."""
import os
import sys
import shutil
import tempfile
import zipfile
from calibration.helpers import get_logger
logger = get_logger()


singleton_output_path = None
MAX_ZIP_MEMBERS = 5000
MAX_ZIP_TOTAL_UNCOMPRESSED_BYTES = 500 * 1024 * 1024  # 500 MiB
MAX_ZIP_SINGLE_FILE_BYTES = 100 * 1024 * 1024  # 100 MiB


def _safe_flatten_name(member_name: str) -> str:
    norm = os.path.normpath(member_name)
    if os.path.isabs(norm):
        raise ValueError(f"absolute paths are not allowed: '{member_name}'")
    parts = norm.split(os.sep)
    if any(part == ".." for part in parts):
        raise ValueError(f"path traversal detected: '{member_name}'")
    base = os.path.basename(norm)
    if not base:
        raise ValueError(f"invalid zip entry name: '{member_name}'")
    return base


def _extract_zip_safely_flattened(zip_path: str, output_dir: str):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        infos = zip_ref.infolist()
        if len(infos) > MAX_ZIP_MEMBERS:
            raise ValueError(
                f"zip file has too many entries ({len(infos)} > {MAX_ZIP_MEMBERS})"
            )

        total_uncompressed = 0
        seen_names: set[str] = set()

        for info in infos:
            if info.is_dir():
                continue

            total_uncompressed += info.file_size
            if total_uncompressed > MAX_ZIP_TOTAL_UNCOMPRESSED_BYTES:
                raise ValueError(
                    "zip file uncompressed content exceeds allowed limit "
                    f"({MAX_ZIP_TOTAL_UNCOMPRESSED_BYTES} bytes)"
                )
            if info.file_size > MAX_ZIP_SINGLE_FILE_BYTES:
                raise ValueError(
                    f"zip entry '{info.filename}' exceeds allowed size "
                    f"({MAX_ZIP_SINGLE_FILE_BYTES} bytes)"
                )

            flat_name = _safe_flatten_name(info.filename)
            if flat_name in seen_names:
                raise ValueError(
                    f"zip contains colliding flattened filenames: '{flat_name}'"
                )
            seen_names.add(flat_name)

            dest = os.path.abspath(os.path.join(output_dir, flat_name))
            output_root = os.path.abspath(output_dir)
            if not dest.startswith(output_root + os.sep):
                raise ValueError(f"unsafe destination path for zip entry '{info.filename}'")

            with zip_ref.open(info, 'r') as src, open(dest, 'wb') as dst:
                shutil.copyfileobj(src, dst)


def get_base_output_path():
    """Get the base output path for storing analysis results."""
    global singleton_output_path
    if singleton_output_path is None:
        logger.error("Output path has not been set up yet. Call setup_paths first.")
        sys.exit(1)
    return singleton_output_path

def setup_paths(calib_files_path, output_path=None, overwrite=False):
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
        try:
            _extract_zip_safely_flattened(calib_files_path, files_path)
        except (zipfile.BadZipFile, ValueError, OSError) as e:
            logger.error("Failed to extract zip '%s': %s", calib_files_path, str(e))
            sys.exit(1)

    if output_path is None:
        output_path = f'./output/{base_name}'
    
    else:
        output_path = os.path.join(output_path, base_name)
    
    if os.path.exists(output_path):
        if not overwrite:
            logger.error("Output path '%s' already exists. Use --overwrite / -w to overwrite.", output_path)
            sys.exit(1)
        if not os.path.isdir(output_path):
            logger.error("Output path '%s' exists and is not a directory.", output_path)
            sys.exit(1)
        # Remove existing directory
        shutil.rmtree(output_path)
    global singleton_output_path
    singleton_output_path = output_path
    os.makedirs(output_path, exist_ok=True)

    logger.info("Calibration files path: %s", files_path)
    logger.info("Output path: %s", output_path)

    return files_path, output_path, base_name
