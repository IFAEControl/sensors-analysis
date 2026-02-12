import os
import argparse
import shutil
import glob
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
    parser.add_argument("calibration_json_path", help="Path to calibration summary JSON file")
    parser.add_argument("--plot-format", "-f", choices=["pdf", "svg", "png"], default="pdf", help="Plot file format (default: pdf)")
    parser.add_argument("--output-path", "-o", help="Output path (default: './output/<name_of_char_files>')")
    parser.add_argument("--log-file", "-l", action="store_true", help="Stores log at output folder(default: None, logs only to console)")
    parser.add_argument("--overwrite", "-w", action="store_true", help="Overwrite output directory if it exists")
    parser.add_argument("--zip", action="store_true", help="Zip characterization folder into output root and remove uncompressed folder")
    parser.add_argument("--no-plots", "-n", action="store_true", help="Do not generate plots")
    parser.add_argument("--no-gen-report", action="store_true", help="Do not generate characterization report")
    args = parser.parse_args()
    if not os.path.isfile(args.calibration_json_path):
        parser.error(f"Calibration JSON file does not exist: {args.calibration_json_path}")

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
    output_base_name = characterization.get_output_base_name()
    config.summary_file_name = f"{output_base_name}_extended.json"
    characterization.analyze()
    if config.generate_plots:
        characterization.generate_plots()
    characterization.apply_calibration(args.calibration_json_path)
    san = SanityChecks(characterization)
    san.run_checks()
    characterization.export_data_summary({'sanity_checks': san.results})
    characterization.export_reduced_summary()
    if not args.no_gen_report:
        from characterization_report.main import build_report
        build_report(characterization.reports_path)
        src_report = os.path.join(
            characterization.reports_path,
            f"{characterization.meta['charact_id']}_report.pdf"
        )
        dst_report = os.path.join(
            characterization.reports_path,
            f"{output_base_name}_report.pdf"
        )
        if src_report != dst_report and os.path.exists(src_report):
            if os.path.exists(dst_report):
                if not args.overwrite:
                    raise FileExistsError(
                        f"Report output already exists: {dst_report}. Use --overwrite / -w to overwrite."
                    )
                os.remove(dst_report)
            os.replace(src_report, dst_report)

    if args.zip:
        char_folder = characterization.reports_path
        output_root = characterization.meta['root_output_path']
        zip_base = os.path.join(output_root, characterization.meta['charact_id'])
        zip_path = f"{zip_base}.zip"
        if os.path.exists(zip_path):
            if not args.overwrite:
                raise FileExistsError(
                    f"Zip output already exists: {zip_path}. Use --overwrite / -w to overwrite."
                )
            os.remove(zip_path)
        shutil.make_archive(zip_base, 'zip', root_dir=output_root, base_dir=os.path.basename(char_folder))

        # Keep key deliverables at output root before removing folder.
        kept_files = []
        for pattern in ("*.json", "*.pdf"):
            for src in glob.glob(os.path.join(char_folder, pattern)):
                dst = os.path.join(output_root, os.path.basename(src))
                if os.path.exists(dst):
                    if not args.overwrite:
                        raise FileExistsError(
                            f"Output file already exists at root: {dst}. Use --overwrite / -w to overwrite."
                        )
                    os.remove(dst)
                shutil.move(src, dst)
                kept_files.append(dst)

        shutil.rmtree(char_folder)
        logger.info("Created zip output: %s", zip_path)
        if kept_files:
            logger.info("Moved deliverables to output root: %s", kept_files)
        logger.info("Removed uncompressed characterization folder: %s", char_folder)

    now_end = datetime.now(timezone.utc)
    logger.info("Finished characterization analysis at %s", now_end.isoformat())
    logger.info("Total duration: %s", str(now_end - now))
    logger.info("Total duration loading libraries: %s", str(now_libs - now))


if __name__ == "__main__":
    main()
