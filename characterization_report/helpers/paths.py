from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from .data_holders import ReportData

from .logger import get_logger
from ..config import config

logger = get_logger()

this_path = os.path.dirname(os.path.abspath(__file__))
default_logo_path = os.path.abspath(
    os.path.join(this_path, "..", "..", "calib_report", "logo", "IFAE_logo_white_SO.png")
)


@dataclass
class ReportPaths:
    root_path: str
    input_file: str
    char_plots_path: str
    report_path: str
    output_path: str
    logo_path: str = default_logo_path


_PATTERN = re.compile(r".*_extended\.json$")


def _looks_like_characterization_summary(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data = ReportData.from_dict(data) # Validate structure with ReportData
    except (OSError, json.JSONDecodeError):
        return False
    
    return data.meta.charact_id


def calc_plot_path(plot_path_in_json: str) -> str:
    if not config.paths.char_plots_path:
        raise ValueError("char_plots_path cannot be empty")
    if not plot_path_in_json:
        raise ValueError("plot_path_in_json cannot be empty")
    if os.path.isabs(plot_path_in_json):
        return plot_path_in_json
    return os.path.join(config.paths.char_plots_path, plot_path_in_json)


def _extract_plots_path(input_file: str, fallback_root: str) -> str:
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            data = ReportData.from_dict(data) # Validate structure with ReportData
        plots_path = data.meta.plots_path
        if isinstance(plots_path, str) and plots_path.strip():
            return plots_path
    except (OSError, json.JSONDecodeError):
        pass
    return os.path.join(fallback_root, "plots")


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
        root_path = input_path
    elif input_path.endswith("_extended.json"):
        input_file = input_path
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file does not exist: {input_file}")
        if not _looks_like_characterization_summary(input_file):
            raise ValueError(f"Input json does not look like a characterization summary: {input_file}")
        root_path = os.path.dirname(input_file)
    else:
        raise ValueError("Input path must be a directory or a *_extended.json file.")

    plots_path = _extract_plots_path(input_file, root_path)
    if not os.path.exists(plots_path):
        raise FileNotFoundError(
            f"Plots path does not exist: {plots_path}"
        )

    if output_path is None:
        output_path = root_path
    else:
        os.makedirs(output_path, exist_ok=True)

    return ReportPaths(
        root_path=root_path,
        input_file=input_file,
        char_plots_path=plots_path,
        report_path="",
        output_path=output_path,
        logo_path=default_logo_path,
    )
