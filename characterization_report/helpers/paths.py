from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from .logger import get_logger

logger = get_logger()

this_path = os.path.dirname(os.path.abspath(__file__))
default_logo_path = os.path.abspath(
    os.path.join(this_path, "..", "..", "calib_report", "logo", "IFAE_logo_white_SO.png")
)


@dataclass
class ReportPaths:
    input_file: str
    char_anal_files_path: str
    report_path: str
    output_path: str
    logo_path: str = default_logo_path


_PATTERN = re.compile(r".*_extended\.json$")


def _looks_like_characterization_summary(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False
    meta = data.get("meta", {})
    return bool(meta.get("charact_id"))


def _extract_outputs_path(input_file: str, fallback_root: str) -> str:
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        meta = data.get("meta", {})
        outputs_path = meta.get("characterization_outputs_path")
        if isinstance(outputs_path, str) and outputs_path.strip():
            return outputs_path
    except (OSError, json.JSONDecodeError):
        pass
    return os.path.join(fallback_root, "characterization_outputs")


def calc_paths(input_path: str, output_path: str | None) -> ReportPaths:
    if input_path is None or input_path.strip() == "":
        raise ValueError("Input path must be provided and cannot be empty.")

    if os.path.isdir(input_path):
        files = os.listdir(input_path)
        candidates = sorted(f for f in files if _PATTERN.match(f))
        matches = [f for f in candidates if _looks_like_characterization_summary(os.path.join(input_path, f))]
        if not matches:
            raise FileNotFoundError(
                f"No characterization extended summary file found in {input_path}"
            )
        if len(matches) > 1:
            logger.warning("Multiple characterization summary files found. Using %s", matches[0])
        else:
            logger.info("Using characterization summary file: %s", matches[0])

        input_file = os.path.join(input_path, matches[0])
        report_root = input_path
    elif input_path.endswith(".json"):
        input_file = input_path
        if not _looks_like_characterization_summary(input_file):
            raise ValueError(f"Input json does not look like a characterization summary: {input_file}")
        report_root = os.path.dirname(input_path)
    else:
        raise ValueError("Input path must be a directory or a .json file.")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    char_anal_files_path = _extract_outputs_path(input_file, report_root)
    if not os.path.exists(char_anal_files_path):
        raise FileNotFoundError(
            f"Characterization outputs path does not exist: {char_anal_files_path}"
        )

    if output_path is None:
        output_path = report_root
    else:
        os.makedirs(output_path, exist_ok=True)

    return ReportPaths(
        input_file=input_file,
        char_anal_files_path=char_anal_files_path,
        report_path="",
        output_path=output_path,
        logo_path=default_logo_path,
    )
