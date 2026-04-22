from __future__ import annotations

import pandas as pd

from crossboard.dataframe import CrossboardDataFrame
from crossboard.plotter import CrossboardPlotter


def _make_crossboard_df(rows: list[dict]) -> CrossboardDataFrame:
    crossboard_df = CrossboardDataFrame()
    crossboard_df.dataframe = pd.DataFrame(rows)
    return crossboard_df


def test_plot_inputs_exclude_flagged_boards(tmp_path) -> None:
    rows = [
        {"board_id": "B1R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 100.0, "a2p_intercept": 10.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 1000.0, "a2v_intercept": 20.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B2R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 105.0, "a2p_intercept": 11.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 1005.0, "a2v_intercept": 21.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B3R0", "photodiode_id": "0.0", "timestamp": 1, "wavelength": "532", "gain": "1", "a2p_slope": 130.0, "a2p_intercept": 12.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 1010.0, "a2v_intercept": 22.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B1R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 200.0, "a2p_intercept": 13.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 1100.0, "a2v_intercept": 23.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B2R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 205.0, "a2p_intercept": 14.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 1105.0, "a2v_intercept": 24.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
        {"board_id": "B3R0", "photodiode_id": "0.1", "timestamp": 1, "wavelength": "1064", "gain": "1", "a2p_slope": 260.0, "a2p_intercept": 15.0, "a2p_slope_err": 0.0, "a2p_intercept_err": 0.0, "a2v_slope": 1110.0, "a2v_intercept": 25.0, "a2v_slope_err": 0.0, "a2v_intercept_err": 0.0},
    ]
    plotter = CrossboardPlotter(_make_crossboard_df(rows), str(tmp_path))

    source_df = plotter.df.dropna(subset=["board_id", "wavelength", "gain", "a2v_slope", "a2v_intercept"]).copy()
    filtered_df = plotter._exclude_flagged_boards(source_df)

    assert sorted(plotter._get_excluded_board_ids()) == ["B3R0"]
    assert sorted(filtered_df["board_id"].unique().tolist()) == ["B1R0", "B2R0"]
    assert "B3R0" not in filtered_df["board_id"].tolist()
