from __future__ import annotations

import json

import pandas as pd

from crossboard.dataframe import CrossboardDataFrame
from crossboard.plotter import CrossboardPlotter


def _make_crossboard_df(rows: list[dict]) -> CrossboardDataFrame:
    crossboard_df = CrossboardDataFrame()
    crossboard_df.dataframe = pd.DataFrame(rows)
    return crossboard_df


def test_export_a2p_final_calification_excludes_boards_above_threshold(tmp_path) -> None:
    rows = [
        {"board_id": "B1R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 100.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B2R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 105.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B3R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 130.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B1R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 200.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B2R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 205.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B3R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 260.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
    ]
    plotter = CrossboardPlotter(_make_crossboard_df(rows), str(tmp_path))

    paths = plotter.export_a2p_final_calification()

    ranking_df = pd.read_csv(paths["ranking_csv"])
    excluded_df = pd.read_csv(paths["excluded_csv"])
    with open(paths["ranking_json"], "r", encoding="utf-8") as f:
        ranking_payload = json.load(f)

    assert ranking_df["board_id"].tolist() == ["B2R0", "B1R0"]
    assert ranking_df["rank"].tolist() == [1, 2]
    assert excluded_df["board_id"].tolist() == ["B3R0"]
    assert excluded_df.iloc[0]["status"] == "excluded"
    assert "1064_1" in excluded_df.iloc[0]["excluded_combos"]
    assert ranking_payload["meta"]["excluded_board_count"] == 1
    assert ranking_payload["meta"]["exclusion_threshold_abs_dev_pct"] == 10.0


def test_export_a2p_final_calification_writes_empty_ranking_when_all_boards_are_excluded(tmp_path) -> None:
    rows = [
        {"board_id": "B1R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 100.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B2R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 150.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B1R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 100.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B2R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 150.0, "a2p_intercept": 0.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 0.0, "a2v_intercept": 0.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
    ]
    plotter = CrossboardPlotter(_make_crossboard_df(rows), str(tmp_path))

    paths = plotter.export_a2p_final_calification()

    ranking_df = pd.read_csv(paths["ranking_csv"])
    excluded_df = pd.read_csv(paths["excluded_csv"])

    assert ranking_df.empty
    assert excluded_df["board_id"].tolist() == ["B1R0", "B2R0"]
