"""Module for setting up file paths for characterization data."""
import os
import sys
import tempfile
import zipfile
from characterization.helpers import get_logger
logger = get_logger()

singleton_output_path = None

def get_base_output_path():
    global singleton_output_path
    if singleton_output_path is None:
        logger.error("Output path has not been set up yet. Call setup_paths first.")
        sys.exit(1)
    return singleton_output_path

def setup_paths(char_files_path, output_path=None, overwrite=False):
    if not os.path.exists(char_files_path):
        logger.error("Characterization files path '%s' does not exist.", char_files_path)
        sys.exit(1)

    files_path = None
    base_name = None
    if os.path.isdir(char_files_path):
        if not os.listdir(char_files_path):
            logger.error("Characterization files directory '%s' is empty.", char_files_path)
            sys.exit(1)
        files_path = char_files_path
        base_name = os.path.basename(os.path.normpath(char_files_path))
    else:
        if not char_files_path.lower().endswith('.zip'):
            logger.error("Characterization files path '%s' is not a directory or a zip file.", char_files_path)
            sys.exit(1)
        files_path = tempfile.mkdtemp()
        base_name = os.path.splitext(os.path.basename(char_files_path))[0]
        with zipfile.ZipFile(char_files_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                zip_ref.extract(member, files_path)
                source = os.path.join(files_path, member)
                if os.path.isfile(source):
                    dest = os.path.join(files_path, os.path.basename(member))
                    if source != dest:
                        os.rename(source, dest)

    if output_path is None:
        output_path = f'./output/{base_name}'

    if os.path.exists(output_path):
        if not overwrite:
            logger.error("Output path '%s' already exists. Use --overwrite / -w to overwrite.", output_path)
            sys.exit(1)
        if not os.path.isdir(output_path):
            logger.error("Output path '%s' exists and is not a directory.", output_path)
            sys.exit(1)
        import shutil
        shutil.rmtree(output_path)

    global singleton_output_path
    singleton_output_path = output_path
    os.makedirs(output_path, exist_ok=True)

    logger.info("Characterization files path: %s", files_path)
    logger.info("Output path: %s", output_path)

    return files_path, output_path, base_name
