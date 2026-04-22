from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DATE_RE = re.compile(r"(?P<day>\d{2})(?P<month>\d{2})(?P<year>\d{4})")


@dataclass(frozen=True)
class DatedFile:
    path: Path
    date: datetime


def _extract_date_from_name(path: Path) -> datetime | None:
    match = DATE_RE.search(path.name)
    if not match:
        return None
    day = int(match.group("day"))
    month = int(match.group("month"))
    year = int(match.group("year"))
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def _collect_dated_files(folder: Path, pattern: str) -> list[DatedFile]:
    out: list[DatedFile] = []
    for path in sorted(folder.glob(pattern)):
        if not path.is_file():
            continue
        file_date = _extract_date_from_name(path)
        if file_date is None:
            print(f"[skip] no DDMMYYYY date found in filename: {path.name}")
            continue
        out.append(DatedFile(path=path, date=file_date))
    return sorted(out, key=lambda item: (item.date, item.path.name))


def _build_calibration_command(args: argparse.Namespace, calibration_zip: Path) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "calibration.main",
        str(calibration_zip),
        "-o",
        str(args.output_folder),
        "-w",
    ]
    if args.plot_format:
        cmd.extend(["-f", args.plot_format])
    if args.no_plots:
        cmd.append("-n")
    if args.no_gen_report:
        cmd.append("--no-gen-report")
    if args.zip_it:
        cmd.append("-z")
    if args.log_file:
        cmd.append("-l")
    if args.do_not_sub_pedestals:
        cmd.append("-d")
    if args.do_not_replace_zero_pm_stds:
        cmd.append("-s")
    if args.use_first_ped_in_linreag:
        cmd.append("-p")
    if args.use_W_as_power_units:
        cmd.append("-u")
    return cmd


def _publish_reduced_summary(output_root: Path, calibration_zip: Path) -> Path:
    calib_id = calibration_zip.stem
    source = output_root / calib_id / f"{calib_id}.json"
    destination = output_root / f"{calib_id}.json"
    if not source.exists():
        raise FileNotFoundError(f"Reduced calibration summary not found at {source}")
    shutil.copy2(source, destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Batch-run calibration analysis for each calibration zip, "
            "processing files in chronological order based on DDMMYYYY in the filename."
        )
    )
    parser.add_argument("calibration_zip_folder", help="Folder containing calibration zip files")
    parser.add_argument(
        "--output-folder",
        "-o",
        type=Path,
        default=Path("calib-reports"),
        help="Root output folder for calibration reports (default: calib-reports)",
    )
    parser.add_argument("--plot-format", "-f", choices=["pdf", "svg", "png"], default="pdf", help="Plot file format")
    parser.add_argument("--log-file", "-l", action="store_true", help="Store a log file for each calibration run")
    parser.add_argument("--no-plots", "-n", action="store_true", help="Do not generate plots")
    parser.add_argument("--no-gen-report", action="store_true", help="Do not generate calibration reports")
    parser.add_argument("--zip-it", "-z", action="store_true", help="Zip each calibration output after analysis")
    parser.add_argument("--do-not-sub-pedestals", "-d", action="store_true", help="Do not subtract pedestals from data")
    parser.add_argument(
        "--do-not-replace-zero-pm-stds",
        "-s",
        action="store_true",
        help="Do not replace zero PM stds from data",
    )
    parser.add_argument(
        "--use-first-ped-in-linreag",
        "-p",
        action="store_true",
        help="Use first pedestal measurement in linear regression",
    )
    parser.add_argument("--use-W-as-power-units", "-u", action="store_true", help="Use W as power units instead of uW")
    args = parser.parse_args()

    execution_dt = datetime.now()
    calibration_folder = Path(args.calibration_zip_folder)
    output_root = args.output_folder
    output_root.mkdir(parents=True, exist_ok=True)

    if not calibration_folder.is_dir():
        parser.error(f"Calibration folder does not exist or is not a directory: {calibration_folder}")

    calibration_files = _collect_dated_files(calibration_folder, "*.zip")
    if not calibration_files:
        parser.error(f"No calibration .zip files with parsable DDMMYYYY date found in {calibration_folder}")

    print("Calibration files to process:")
    for calibration_file in calibration_files:
        print(f"  {calibration_file.path.name} ({calibration_file.date.strftime('%Y-%m-%d')})")

    log_path = output_root / f"batch_calib_analysis_log_{execution_dt.strftime('%Y%m%d_%H%M%S')}.md"
    with log_path.open("w", encoding="utf-8") as f:
        f.write("# Batch Calibration Analysis Log\n\n")
        f.write(f"- Execution date: {execution_dt.isoformat()}\n")
        f.write(f"- Calibration folder: `{calibration_folder}`\n")
        f.write(f"- Output folder: `{output_root}`\n\n")
        f.write("## Calibration Processing Order\n\n")
        f.write("| Calibration | Date |\n")
        f.write("|---|---:|\n")
        for calibration_file in calibration_files:
            f.write(f"| {calibration_file.path.name} | {calibration_file.date.strftime('%Y-%m-%d')} |\n")
        f.write("\n## Execution Results\n\n")

    for calibration_file in calibration_files:
        cmd = _build_calibration_command(args, calibration_file.path)
        print("\nRunning:", " ".join(cmd))
        result = subprocess.run(cmd, check=False)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"- `{calibration_file.path.name}`: exit code `{result.returncode}`\n")
            if result.returncode == 0:
                try:
                    published_path = _publish_reduced_summary(output_root, calibration_file.path)
                except FileNotFoundError as exc:
                    f.write(f"  - failed to publish reduced summary to output root: `{exc}`\n")
                    print(f"[error] {exc}")
                else:
                    f.write(f"  - published reduced summary: `{published_path.name}`\n")
        if result.returncode != 0:
            print(f"[error] calibration failed for {calibration_file.path.name} (exit={result.returncode})")

    print(f"\nSaved batch log: {log_path}")


if __name__ == "__main__":
    main()
