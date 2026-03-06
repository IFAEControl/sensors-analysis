import argparse
import re
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


def _extract_board_id(path: Path) -> str:
    stem = path.stem
    if "_" in stem:
        return stem.split("_", 1)[1]
    return stem


def _collect_dated_files(folder: Path, pattern: str) -> list[DatedFile]:
    out: list[DatedFile] = []
    for p in sorted(folder.glob(pattern)):
        if not p.is_file():
            continue
        file_date = _extract_date_from_name(p)
        if file_date is None:
            print(f"[skip] no DDMMYYYY date found in filename: {p.name}")
            continue
        out.append(DatedFile(path=p, date=file_date))
    return out


def _find_previous_calibration(char_date: datetime, calibrations: list[DatedFile]) -> DatedFile | None:
    candidates = [c for c in calibrations if c.date <= char_date]
    if not candidates:
        return None
    return max(candidates, key=lambda c: c.date)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Batch-run characterization analysis for each characterization zip, "
            "using the nearest previous calibration by date parsed from filename (DDMMYYYY)."
        )
    )
    parser.add_argument("characterization_zip_folder", help="Folder containing characterization zip files")
    parser.add_argument("calibration_reports_folder", help="Folder containing calibration output files (JSON)")
    parser.add_argument(
        "--output-folder",
        "-o",
        default="charact-reports",
        help="Root output folder for characterization reports (default: charact-reports)",
    )
    args = parser.parse_args()

    char_folder = Path(args.characterization_zip_folder)
    calib_folder = Path(args.calibration_reports_folder)
    output_root = Path(args.output_folder)

    if not char_folder.is_dir():
        parser.error(f"Characterization folder does not exist or is not a directory: {char_folder}")
    if not calib_folder.is_dir():
        parser.error(f"Calibration folder does not exist or is not a directory: {calib_folder}")

    characterization_files = _collect_dated_files(char_folder, "*.zip")
    calibration_files = _collect_dated_files(calib_folder, "*.json")

    if not characterization_files:
        parser.error(f"No characterization .zip files with parsable DDMMYYYY date found in {char_folder}")
    if not calibration_files:
        parser.error(f"No calibration .json files with parsable DDMMYYYY date found in {calib_folder}")

    relations: list[tuple[DatedFile, DatedFile, str]] = []
    skipped: list[DatedFile] = []

    for char_file in characterization_files:
        calib = _find_previous_calibration(char_file.date, calibration_files)
        if calib is None:
            skipped.append(char_file)
            continue
        board_id = _extract_board_id(char_file.path)
        relations.append((char_file, calib, board_id))

    print("Characterization -> Calibration relations:")
    for char_file, calib_file, board_id in relations:
        print(
            f"  {char_file.path.name} ({char_file.date.strftime('%Y-%m-%d')})"
            f"  ->  {calib_file.path.name} ({calib_file.date.strftime('%Y-%m-%d')})"
            f"  [board={board_id}]"
        )
    for char_file in skipped:
        print(
            f"  [skip] {char_file.path.name} ({char_file.date.strftime('%Y-%m-%d')})"
            "  ->  no previous calibration found"
        )

    for char_file, calib_file, board_id in relations:
        run_output = output_root / board_id
        run_output.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            "-m",
            "characterization.main",
            str(char_file.path),
            str(calib_file.path),
            "-wze",
            "-o",
            str(run_output),
        ]
        print("\nRunning:", " ".join(cmd))
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"[error] characterization failed for {char_file.path.name} (exit={result.returncode})")


if __name__ == "__main__":
    main()
