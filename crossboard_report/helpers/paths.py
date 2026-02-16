from __future__ import annotations

import os
import re
from dataclasses import dataclass

from .logger import get_logger

logger = get_logger()


@dataclass
class ReportPaths:
    root_path: str
    input_file: str
    output_path: str


_PATTERN = re.compile(r".*_summary\.json$")


def calc_paths(input_path: str, output_path: str | None) -> ReportPaths:
    if input_path is None or input_path.strip() == "":
        raise ValueError("Input path must be provided and cannot be empty.")

    if os.path.isdir(input_path):
        files = os.listdir(input_path)
        matches = sorted(f for f in files if _PATTERN.match(f))
        if not matches:
            raise FileNotFoundError(f"No crossboard summary file found in {input_path}")
        if len(matches) > 1:
            logger.warning("Multiple crossboard summary files found. Using %s", matches[0])
        input_file = os.path.join(input_path, matches[0])
        root_path = input_path
    elif input_path.endswith(".json"):
        input_file = input_path
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file does not exist: {input_file}")
        root_path = os.path.dirname(input_file)
    else:
        raise ValueError("Input path must be a directory or a JSON summary file.")

    if output_path is None:
        output_path = root_path
    else:
        os.makedirs(output_path, exist_ok=True)

    return ReportPaths(
        root_path=root_path,
        input_file=input_file,
        output_path=output_path,
    )
