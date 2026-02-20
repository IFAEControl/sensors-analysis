from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from characterization.config import config
from characterization.helpers import get_logger

logger = get_logger()


@dataclass(frozen=True)
class FilesetSelection:
    wavelength: str
    selected_key: str | None
    candidates: tuple[str, ...]
    expected_key: str | None
    reason: str


def select_fileset_for_wavelength(
    fileset_keys: Iterable[str] | None,
    wavelength: str,
    sensor_id: str | None = None,
    expected_runs: Sequence[str] | None = None,
) -> FilesetSelection:
    keys = tuple(sorted({k for k in (fileset_keys or []) if isinstance(k, str)}))
    candidates = tuple(k for k in keys if k.startswith(f"{wavelength}_"))
    if not candidates:
        return FilesetSelection(
            wavelength=wavelength,
            selected_key=None,
            candidates=(),
            expected_key=None,
            reason="missing",
        )

    expected_key = None
    if sensor_id:
        sensor_cfg = config.sensor_config.get(sensor_id, {}) or {}
        cfg_runs = sensor_cfg.get("valid_setups", sensor_cfg.get("expected_runs", []))
        for run in cfg_runs or []:
            if isinstance(run, str) and run.startswith(f"{wavelength}_"):
                expected_key = run
                break
    for run in expected_runs or []:
        if isinstance(run, str) and run.startswith(f"{wavelength}_"):
            expected_key = run
            break

    if expected_key and expected_key in candidates:
        return FilesetSelection(
            wavelength=wavelength,
            selected_key=expected_key,
            candidates=candidates,
            expected_key=expected_key,
            reason="expected_match",
        )

    if expected_key and expected_key not in candidates:
        logger.warning(
            "Expected fileset %s for sensor %s not found among acquired candidates %s; using fallback selection.",
            expected_key,
            sensor_id,
            list(candidates),
        )

    if len(candidates) == 1:
        return FilesetSelection(
            wavelength=wavelength,
            selected_key=candidates[0],
            candidates=candidates,
            expected_key=expected_key,
            reason="single_candidate",
        )

    return FilesetSelection(
        wavelength=wavelength,
        selected_key=candidates[0],
        candidates=candidates,
        expected_key=expected_key,
        reason="lexicographic_fallback",
    )
