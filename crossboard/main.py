import argparse
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone

from crossboard_report import build_report

from .config import config
from .dataframe import CrossboardDataFrame, DATAFRAME_COLUMNS
from .helpers import add_file_handler, get_logger
from .plotter import CrossboardPlotter

logger = get_logger()


def _zip_directory(source_dir: str, zip_path: str) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for folder, _, files in os.walk(source_dir):
            for file_name in sorted(files):
                file_path = os.path.join(folder, file_name)
                arcname = os.path.relpath(file_path, source_dir)
                zf.write(file_path, arcname)


def _publish_crossboard_artifacts(staging_dir: str, output_path: str) -> None:
    for file_name in sorted(os.listdir(staging_dir)):
        source = os.path.join(staging_dir, file_name)
        if not os.path.isfile(source):
            continue
        if not file_name.startswith("crossboard"):
            continue
        shutil.move(source, os.path.join(output_path, file_name))


def main():
    logger.info("Virgo Instrumented Baffles Crossboard script")

    parser = argparse.ArgumentParser(description="Virgo Instrumented Baffles Crossboard script")
    parser.add_argument("input_path", help="Path to board JSON root directory or crossboard dataframe CSV")
    parser.add_argument(
        "--plot-format",
        "-f",
        choices=["pdf", "svg", "png"],
        default="pdf",
        help="Plot file format (default: pdf)",
    )
    parser.add_argument(
        "--output-path",
        "-o",
        help="Output path (default: './output/<name_of_crossboard_files>')",
        default='./output/crossboard'
    )
    parser.add_argument(
        "--log-file",
        "-l",
        action="store_true",
        help="Store log at output folder (default: logs only to console)",
    )
    parser.add_argument("--overwrite", "-w", action="store_true", help="Overwrite output directory if it exists")
    parser.add_argument(
        "--no-save-dataframe",
        action="store_true",
        help="Load/build dataframe but do not write output CSV file",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip crossboard report generation",
    )
    args = parser.parse_args()

    config.plot_output_format = args.plot_format

    output_path = args.output_path
    if os.path.exists(output_path):
        if not args.overwrite:
            parser.error(f"Output directory already exists: {output_path}. Use --overwrite / -w to overwrite.")
        if not os.path.isdir(output_path):
            parser.error(f"Output path exists and is not a directory: {output_path}")
        shutil.rmtree(output_path)
        os.makedirs(output_path, exist_ok=True)
    else:
        os.makedirs(output_path, exist_ok=True)

    output_path = os.path.abspath(output_path)
    parent_output_dir = os.path.dirname(output_path) or "."
    bundle_name = f"{os.path.basename(output_path.rstrip(os.sep)) or 'crossboard'}.zip"
    bundle_path = os.path.join(output_path, bundle_name)

    with tempfile.TemporaryDirectory(prefix="crossboard_build_", dir=parent_output_dir) as staging_dir:
        staging_dir = os.path.abspath(staging_dir)

        if args.log_file:
            log_file_path = os.path.join(staging_dir, "crossboard.log")
            add_file_handler(log_file_path)
            logger.info("Logging to file: %s", log_file_path)

        started_at = datetime.now(timezone.utc)
        logger.info("Crossboard input path: %s", args.input_path)
        logger.info("Output path: %s", output_path)
        logger.info("Staging output path: %s", staging_dir)
        logger.info("Starting crossboard dataframe load at %s", started_at.isoformat())

        crossboard_df = CrossboardDataFrame()
        if os.path.isdir(args.input_path):
            source = "json"
            logger.info("Detected directory input. Loading board summaries from JSON files.")
            dataframe = crossboard_df.load_from_json_root(args.input_path)
        elif os.path.isfile(args.input_path):
            if args.input_path.lower().endswith(".csv"):
                source = "csv"
                logger.info("Detected CSV input file. Loading dataframe from CSV.")
                dataframe = crossboard_df.load_from_csv(args.input_path)
            else:
                parser.error(f"Input file must be a CSV file or a folder: {args.input_path}")
        else:
            parser.error(f"Input path does not exist: {args.input_path}")

        dataframe_path = os.path.join(staging_dir, "crossboard_dataframe.csv")
        if not args.no_save_dataframe:
            crossboard_df.save_to_csv(dataframe_path)
            logger.info("Saved crossboard dataframe CSV: %s", dataframe_path)
        else:
            logger.info("Skipping dataframe CSV save due to --no-save-dataframe")

        plotter = CrossboardPlotter(crossboard_dataframe=crossboard_df, output_path=staging_dir)
        for metric in ("a2p", "a2v"):
            plotter.generate_intercept_vs_slope_by_wavelength(metric=metric)
            plotter.generate_intercept_vs_slope_by_wavelength_gain(metric=metric)
            plotter.generate_slope_intercept_histograms_by_wavelength(metric=metric)
        plotter.generate_a2p_slope_diff_from_median_grid()
        plotter.generate_a2p_slope_pct_diff_from_median_grid()
        plotter.generate_a2p_robust_zscore_heatmap()
        ranking_paths = plotter.export_a2p_deviation_rankings(top_n=3)
        final_calification_paths = plotter.export_a2p_final_calification()
        plot_paths = plotter.plots

        summary = {
            "meta": {
                "input_path": args.input_path,
                "source": source,
                "output_path": output_path,
                "staging_output_path": staging_dir,
                "execution_date": started_at.isoformat(),
                "config": config.to_dict(),
                "status": "dataframe_loaded",
            },
            "dataframe": {
                "columns": DATAFRAME_COLUMNS,
                "rows": int(len(dataframe)),
                "boards_loaded": int(dataframe["board_id"].nunique()) if not dataframe.empty else 0,
                "csv_path": dataframe_path if not args.no_save_dataframe else None,
            },
            "plots": plot_paths,
            "analysis": {
                "a2p_board_deviation_rankings": ranking_paths,
                "a2p_board_final_calification": final_calification_paths,
            },
            "input_files_used": crossboard_df.input_files_used,
        }
        summary_path = os.path.join(staging_dir, config.summary_file_name)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info("Generated crossboard summary: %s", summary_path)
        if args.no_report:
            logger.info("Skipping crossboard report generation due to --no-report")
        else:
            logger.info("Starting crossboard report generation from summary: %s", summary_path)
            build_report(summary_path, staging_dir)
            logger.info("Crossboard report generation completed")

        _zip_directory(staging_dir, bundle_path)
        logger.info("Generated crossboard bundle: %s", bundle_path)
        _publish_crossboard_artifacts(staging_dir, output_path)
        logger.info("Published root crossboard artifacts to: %s", output_path)
        logger.info("Crossboard stage 1 completed")


if __name__ == "__main__":
    main()
