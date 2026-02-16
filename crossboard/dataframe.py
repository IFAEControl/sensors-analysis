from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from .helpers import get_logger

logger = get_logger()

DATAFRAME_COLUMNS = [
    "board_id",
    "photodiode_id",
    "timestamp",
    "wavelength",
    "a2p_slope",
    "a2p_intercept",
    "a2p_slope_err",
    "a2p_intercept_err",
    "a2v_slope",
    "a2v_intercept",
    "a2v_slope_err",
    "a2v_intercept_err",
]


class CrossboardDataFrame:
    def __init__(self):
        self.dataframe = pd.DataFrame(columns=DATAFRAME_COLUMNS)
        self.input_files_used: list[str] = []

    def load_from_json_root(self, crossboard_files_path: str) -> pd.DataFrame:
        root = Path(crossboard_files_path)
        if not root.exists():
            raise FileNotFoundError(f"Crossboard input path does not exist: {crossboard_files_path}")
        if not root.is_dir():
            raise ValueError(f"Crossboard input path must be a directory: {crossboard_files_path}")

        rows: list[dict[str, Any]] = []
        used_files: list[str] = []
        board_dirs = sorted(path for path in root.iterdir() if path.is_dir())

        for board_dir in board_dirs:
            board_id = board_dir.name
            summary_file = self._find_board_summary_file(board_dir)
            if summary_file is None:
                logger.warning("Skipping board %s: no JSON summary found", board_id)
                continue

            try:
                with open(summary_file, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Skipping board %s: cannot read %s (%s)", board_id, summary_file, exc)
                continue

            rows.extend(self._extract_records(board_id=board_id, payload=payload))
            used_files.append(str(summary_file))

        self.dataframe = pd.DataFrame(rows, columns=DATAFRAME_COLUMNS)
        self.input_files_used = used_files
        return self.dataframe

    def load_from_csv(self, csv_path: str) -> pd.DataFrame:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV input does not exist: {csv_path}")
        df = pd.read_csv(csv_path)
        missing = [col for col in DATAFRAME_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        self.dataframe = df[DATAFRAME_COLUMNS].copy()
        self.input_files_used = [csv_path]
        return self.dataframe

    def save_to_csv(self, csv_path: str) -> str:
        output_dir = os.path.dirname(csv_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        self.dataframe.to_csv(csv_path, index=False)
        return csv_path

    @staticmethod
    def _get_value_or_none(data: dict[str, Any], key: str) -> Any:
        value = data.get(key)
        return None if value is None else value

    @staticmethod
    def _extract_timestamp(payload: dict[str, Any]) -> int | str | None:
        acquisition_time = payload.get("acquisition_time") or {}
        timestamp = acquisition_time.get("min_ts")
        if timestamp is not None:
            return timestamp

        char_id = payload.get("characterization_id")
        if isinstance(char_id, str) and "_" in char_id:
            return char_id.split("_", 1)[0]
        return None

    def _extract_records(self, board_id: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        photodiodes = payload.get("photodiodes") or {}
        timestamp = self._extract_timestamp(payload)

        for photodiode_id, by_wavelength in photodiodes.items():
            if not isinstance(by_wavelength, dict):
                continue
            for wavelength, fit_data in by_wavelength.items():
                if not isinstance(fit_data, dict):
                    continue

                adc_to_power = fit_data.get("adc_to_power") or {}
                adc_to_vref = fit_data.get("adc_to_vrefV") or {}

                records.append(
                    {
                        "board_id": board_id,
                        "photodiode_id": photodiode_id,
                        "timestamp": timestamp,
                        "wavelength": wavelength,
                        "a2p_slope": self._get_value_or_none(adc_to_power, "slope"),
                        "a2p_intercept": self._get_value_or_none(adc_to_power, "intercept"),
                        "a2p_slope_err": self._get_value_or_none(adc_to_power, "slope_err"),
                        "a2p_intercept_err": self._get_value_or_none(adc_to_power, "intercept_err"),
                        "a2v_slope": self._get_value_or_none(adc_to_vref, "slope"),
                        "a2v_intercept": self._get_value_or_none(adc_to_vref, "intercept"),
                        "a2v_slope_err": adc_to_vref.get("slope_err", adc_to_vref.get("stderr")),
                        "a2v_intercept_err": adc_to_vref.get("intercept_err", adc_to_vref.get("intercept_stderr")),
                    }
                )
        return records

    @staticmethod
    def _find_board_summary_file(board_root: Path) -> Path | None:
        board_id = board_root.name
        candidates = sorted(
            path
            for path in board_root.rglob("*.json")
            if not path.name.endswith("_extended.json")
        )
        if not candidates:
            return None

        exact_name = f"{board_id}.json"
        exact_matches = [path for path in candidates if path.name == exact_name]
        if exact_matches:
            if len(exact_matches) > 1:
                logger.warning(
                    "Multiple '%s' files found under %s. Using latest modified: %s",
                    exact_name,
                    board_root,
                    max(exact_matches, key=lambda p: p.stat().st_mtime),
                )
            return max(exact_matches, key=lambda p: p.stat().st_mtime)

        contains_board = [path for path in candidates if board_id in path.stem]
        if contains_board:
            selected = max(contains_board, key=lambda p: p.stat().st_mtime)
            logger.warning(
                "No exact '%s' found under %s. Falling back to %s",
                exact_name,
                board_root,
                selected,
            )
            return selected

        selected = max(candidates, key=lambda p: p.stat().st_mtime)
        logger.warning(
            "No board-named JSON found under %s. Falling back to %s",
            board_root,
            selected,
        )
        return selected
