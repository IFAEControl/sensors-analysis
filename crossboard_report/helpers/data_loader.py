from __future__ import annotations

import csv
import json
import os
from typing import Any


def load_summary(input_file: str) -> dict[str, Any]:
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_artifact_path(path_value: str | None, root_path: str) -> str:
    if not path_value:
        return ""
    if os.path.isabs(path_value):
        return path_value
    if os.path.exists(path_value):
        return path_value
    candidate = os.path.join(root_path, path_value)
    return candidate


def load_csv_rows(csv_path: str) -> list[dict[str, str]]:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def resolve_plot_path(summary: dict[str, Any], root_path: str, plot_key: str) -> str:
    plots = summary.get("plots", {}) or {}
    path = resolve_artifact_path(plots.get(plot_key), root_path)
    return _prefer_compatible_plot_asset(path)


def _prefer_compatible_plot_asset(path: str) -> str:
    if not path:
        return ""

    candidate = path
    stem, ext = os.path.splitext(candidate)

    # Prefer raster assets when available because some generated PDF plots do not
    # round-trip cleanly through the pdfrw -> reportlab embedding path.
    for alt_ext in (".png", ".jpg", ".jpeg"):
        alt_path = stem + alt_ext
        if os.path.exists(alt_path):
            return alt_path

    if os.path.exists(candidate):
        return candidate

    # If the referenced file is missing, try common sibling extensions before
    # returning the unresolved path so the report can still draw its placeholder.
    for alt_ext in (".png", ".jpg", ".jpeg", ".pdf", ".svg"):
        alt_path = stem + alt_ext
        if os.path.exists(alt_path):
            return alt_path

    return candidate


def load_final_calification_rows(summary: dict[str, Any], root_path: str) -> list[dict[str, str]]:
    analysis = summary.get("analysis", {}) or {}
    final_calification = analysis.get("a2p_board_final_calification", {}) or {}
    csv_path = resolve_artifact_path(final_calification.get("ranking_csv"), root_path)
    if not csv_path:
        csv_path = os.path.join(root_path, "a2p_board_final_calification.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Final calification CSV does not exist: {csv_path}")

    return load_csv_rows(csv_path)


def load_deviation_ranking_rows(summary: dict[str, Any], root_path: str) -> list[dict[str, str]]:
    analysis = summary.get("analysis", {}) or {}
    rankings = analysis.get("a2p_board_deviation_rankings", {}) or {}
    csv_path = resolve_artifact_path(rankings.get("ranking_csv"), root_path)
    if not csv_path:
        csv_path = os.path.join(root_path, "a2p_board_deviation_rankings.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Deviation ranking CSV does not exist: {csv_path}")
    return load_csv_rows(csv_path)
