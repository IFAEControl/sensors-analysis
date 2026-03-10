from __future__ import annotations

import os
import math
import json
from typing import Any

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from .config import config
from .dataframe import CrossboardDataFrame
from .helpers import get_logger
from .style_spec import PLOT_STYLE

logger = get_logger()


class CrossboardPlotter:
    """Generate crossboard plots from a loaded CrossboardDataFrame."""

    def __init__(self, crossboard_dataframe: CrossboardDataFrame, output_path: str):
        self.crossboard_dataframe = crossboard_dataframe
        self.output_path = output_path
        self.plots: dict[str, str] = {}
        os.makedirs(self.output_path, exist_ok=True)

    @property
    def df(self):
        return self.crossboard_dataframe.dataframe

    def generate_intercept_vs_slope_by_wavelength(self, metric: str = "a2p") -> dict[str, str]:
        slope_col = f"{metric}_slope"
        intercept_col = f"{metric}_intercept"
        for required in ("board_id", "wavelength", slope_col, intercept_col):
            if required not in self.df.columns:
                raise ValueError(f"Missing required column for plotting: {required}")

        if self.df.empty:
            logger.warning("Crossboard dataframe is empty. No plots generated.")
            return self.plots

        clean_df = self.df.dropna(subset=["board_id", "wavelength", slope_col, intercept_col]).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for %s intercept/slope plot.", metric)
            return self.plots

        wavelengths = sorted(clean_df["wavelength"].astype(str).unique(), key=self._sort_wavelength)
        board_ids = sorted(clean_df["board_id"].astype(str).unique())
        cmap = plt.get_cmap(PLOT_STYLE["board_cmap"], max(len(board_ids), 1))
        board_color_map: dict[str, Any] = {board_id: cmap(idx) for idx, board_id in enumerate(board_ids)}

        for wavelength in wavelengths:
            subset = clean_df[clean_df["wavelength"].astype(str) == wavelength]
            if subset.empty:
                continue

            fig, ax = plt.subplots(figsize=(10, 7))
            for board_id in board_ids:
                points = subset[subset["board_id"].astype(str) == board_id]
                if points.empty:
                    continue
                ax.scatter(
                    points[intercept_col],
                    points[slope_col],
                    s=50,
                    alpha=0.85,
                    color=board_color_map[board_id],
                    edgecolors=PLOT_STYLE["scatter_edge"],
                    linewidths=0.3,
                    label=board_id,
                )

            ax.set_title(f"{metric.upper()} slope vs intercept - wavelength {wavelength}")
            ax.set_xlabel(f"{metric.upper()} intercept")
            ax.set_ylabel(f"{metric.upper()} slope")
            ax.grid(True, alpha=0.3)
            ax.legend(
                title="board_id",
                loc="lower left",
                bbox_to_anchor=(0.01, 0.01),
                fontsize=8,
                title_fontsize=9,
            )

            fig.tight_layout()
            fig_id = f"{metric}_slope_vs_intercept_{wavelength}"
            fig_path = os.path.join(self.output_path, f"{fig_id}.{config.plot_output_format}")
            fig.savefig(fig_path)
            plt.close(fig)
            self.plots[fig_id] = fig_path
            logger.info("Saved plot: %s", fig_path)

        return self.plots

    def generate_slope_intercept_histograms_by_wavelength(self, metric: str = "a2p") -> dict[str, str]:
        slope_col = f"{metric}_slope"
        intercept_col = f"{metric}_intercept"
        for required in ("wavelength", "gain", slope_col, intercept_col):
            if required not in self.df.columns:
                raise ValueError(f"Missing required column for plotting: {required}")

        if self.df.empty:
            logger.warning("Crossboard dataframe is empty. No histogram plots generated.")
            return self.plots

        clean_df = self.df.dropna(subset=["wavelength", "gain", slope_col, intercept_col]).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for %s histograms.", metric)
            return self.plots

        combos = (
            clean_df.assign(
                wavelength_s=clean_df["wavelength"].astype(str),
                gain_s=clean_df["gain"].astype(str),
            )[["wavelength_s", "gain_s"]]
            .drop_duplicates()
            .sort_values(by=["wavelength_s", "gain_s"], key=lambda s: s.map(self._sort_wavelength) if s.name == "wavelength_s" else s)
        )
        for _, combo in combos.iterrows():
            wavelength = combo["wavelength_s"]
            gain = combo["gain_s"]
            subset = clean_df[
                (clean_df["wavelength"].astype(str) == wavelength)
                & (clean_df["gain"].astype(str) == gain)
            ]
            if subset.empty:
                continue

            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(9, 8), sharex=False)

            axes[0].hist(
                subset[slope_col],
                bins=20,
                color=PLOT_STYLE["hist_slope"],
                edgecolor=PLOT_STYLE["scatter_edge"],
                alpha=0.8,
            )
            axes[0].set_title(f"{metric.upper()} slope histogram - wavelength {wavelength} - gain {gain}")
            axes[0].set_xlabel(f"{metric.upper()} slope")
            axes[0].grid(True, axis="y", alpha=0.3)

            axes[1].hist(
                subset[intercept_col],
                bins=20,
                color=PLOT_STYLE["hist_intercept"],
                edgecolor=PLOT_STYLE["scatter_edge"],
                alpha=0.8,
            )
            axes[1].set_title(f"{metric.upper()} intercept histogram - wavelength {wavelength} - gain {gain}")
            axes[1].set_xlabel(f"{metric.upper()} intercept")
            axes[1].grid(True, axis="y", alpha=0.3)

            fig.tight_layout()
            fig_id = f"{metric}_histograms_{wavelength}_{gain}"
            fig_path = os.path.join(self.output_path, f"{fig_id}.{config.plot_output_format}")
            fig.savefig(fig_path)
            plt.close(fig)
            self.plots[fig_id] = fig_path
            logger.info("Saved plot: %s", fig_path)

        return self.plots

    def generate_intercept_vs_slope_by_wavelength_gain(self, metric: str = "a2p") -> dict[str, str]:
        slope_col = f"{metric}_slope"
        intercept_col = f"{metric}_intercept"
        for required in ("board_id", "wavelength", "gain", slope_col, intercept_col):
            if required not in self.df.columns:
                raise ValueError(f"Missing required column for plotting: {required}")

        if self.df.empty:
            logger.warning("Crossboard dataframe is empty. No plots generated.")
            return self.plots

        clean_df = self.df.dropna(subset=["board_id", "wavelength", "gain", slope_col, intercept_col]).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for %s intercept/slope by gain plot.", metric)
            return self.plots

        combos = (
            clean_df.assign(
                wavelength_s=clean_df["wavelength"].astype(str),
                gain_s=clean_df["gain"].astype(str),
            )[["wavelength_s", "gain_s"]]
            .drop_duplicates()
            .sort_values(by=["wavelength_s", "gain_s"], key=lambda s: s.map(self._sort_wavelength) if s.name == "wavelength_s" else s)
        )
        board_ids = sorted(clean_df["board_id"].astype(str).unique())
        cmap = plt.get_cmap(PLOT_STYLE["board_cmap"], max(len(board_ids), 1))
        board_color_map: dict[str, Any] = {board_id: cmap(idx) for idx, board_id in enumerate(board_ids)}

        for _, combo in combos.iterrows():
            wavelength = combo["wavelength_s"]
            gain = combo["gain_s"]
            subset = clean_df[
                (clean_df["wavelength"].astype(str) == wavelength)
                & (clean_df["gain"].astype(str) == gain)
            ]
            if subset.empty:
                continue

            fig, ax = plt.subplots(figsize=(10, 7))
            for board_id in board_ids:
                points = subset[subset["board_id"].astype(str) == board_id]
                if points.empty:
                    continue
                ax.scatter(
                    points[intercept_col],
                    points[slope_col],
                    s=50,
                    alpha=0.85,
                    color=board_color_map[board_id],
                    edgecolors=PLOT_STYLE["scatter_edge"],
                    linewidths=0.3,
                    label=board_id,
                )

            ax.set_title(f"{metric.upper()} slope vs intercept - wavelength {wavelength} - gain {gain}")
            ax.set_xlabel(f"{metric.upper()} intercept")
            ax.set_ylabel(f"{metric.upper()} slope")
            ax.grid(True, alpha=0.3)
            ax.legend(
                title="board_id",
                loc="lower left",
                bbox_to_anchor=(0.01, 0.01),
                fontsize=8,
                title_fontsize=9,
            )

            fig.tight_layout()
            fig_id = f"{metric}_slope_vs_intercept_{wavelength}_{gain}"
            fig_path = os.path.join(self.output_path, f"{fig_id}.{config.plot_output_format}")
            fig.savefig(fig_path)
            plt.close(fig)
            self.plots[fig_id] = fig_path
            logger.info("Saved plot: %s", fig_path)

        return self.plots

    def generate_a2p_slope_diff_from_median_grid(self) -> dict[str, str]:
        slope_col = "a2p_slope"
        for required in ("board_id", "photodiode_id", "wavelength", "gain", slope_col):
            if required not in self.df.columns:
                raise ValueError(f"Missing required column for plotting: {required}")

        if self.df.empty:
            logger.warning("Crossboard dataframe is empty. No composed median-diff plot generated.")
            return self.plots

        clean_df = self.df.dropna(subset=["board_id", "photodiode_id", "wavelength", "gain", slope_col]).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for a2p slope median-diff plot.")
            return self.plots

        combos = (
            clean_df.assign(
                wavelength_s=clean_df["wavelength"].astype(str),
                gain_s=clean_df["gain"].astype(str),
            )[["wavelength_s", "gain_s"]]
            .drop_duplicates()
            .sort_values(by=["wavelength_s", "gain_s"], key=lambda s: s.map(self._sort_wavelength) if s.name == "wavelength_s" else s)
        )
        if combos.empty:
            return self.plots

        for _, combo in combos.iterrows():
            wavelength = combo["wavelength_s"]
            gain = combo["gain_s"]
            subset = clean_df[
                (clean_df["wavelength"].astype(str) == wavelength)
                & (clean_df["gain"].astype(str) == gain)
            ].copy()
            if subset.empty:
                continue

            slopes_all = subset[slope_col].astype(float).values
            median = float(np.median(slopes_all))
            abs_dev = np.abs(slopes_all - median)
            p75 = float(np.percentile(abs_dev, 75))

            board_ids = sorted(subset["board_id"].astype(str).unique())
            boards_by_col: dict[int, list[str]] = {0: [], 1: [], 2: []}
            other_boards: list[str] = []
            for board_id in board_ids:
                suffix = str(board_id)[-1:]
                if suffix == "0":
                    boards_by_col[0].append(board_id)
                elif suffix == "1":
                    boards_by_col[1].append(board_id)
                elif suffix == "2":
                    boards_by_col[2].append(board_id)
                else:
                    other_boards.append(board_id)
            # Keep non 0/1/2 boards visible by appending them to the first column.
            boards_by_col[0].extend(other_boards)

            ncols = 3
            nrows = max(len(boards_by_col[0]), len(boards_by_col[1]), len(boards_by_col[2]), 1)
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6 * ncols, 4.5 * nrows), sharey=False)
            axes_arr = np.array(axes).reshape(-1)
            used_axes: set[int] = set()

            for col_idx in range(ncols):
                for row_idx, board_id in enumerate(boards_by_col[col_idx]):
                    ax_idx = row_idx * ncols + col_idx
                    ax = axes_arr[ax_idx]
                    used_axes.add(ax_idx)
                    board_points = subset[subset["board_id"].astype(str) == board_id].copy()
                    board_points = board_points.sort_values(by=["photodiode_id"]).reset_index(drop=True)
                    x = np.arange(len(board_points))

                    ax.axhline(
                        median,
                        linestyle="--",
                        linewidth=1.5,
                        color=PLOT_STYLE["median_line"],
                        label=f"Median ({median:.3e})",
                    )
                    ax.fill_between(
                        [-0.5, len(board_points) - 0.5],
                        median - p75,
                        median + p75,
                        color=PLOT_STYLE["band_up_to_p75"],
                        alpha=1.0,
                        label=f"Up to P75 (±{p75:.3e})",
                    )
                    ax.scatter(
                        x,
                        board_points[slope_col].astype(float).values,
                        s=36,
                        alpha=0.9,
                        color=PLOT_STYLE["board_point"],
                        edgecolors=PLOT_STYLE["scatter_edge"],
                        linewidths=0.25,
                        label=f"Board {board_id}",
                    )

                    labels = [str(v) for v in board_points["photodiode_id"].tolist()]
                    ax.set_xticks(x)
                    ax.set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
                    ax.set_xlim(-0.5, len(board_points) - 0.5)
                    ax.set_title(f"Board {board_id}", fontsize=10)
                    ax.set_xlabel("Photodiode ID")
                    ax.set_ylabel("A2P slope")
                    ax.grid(True, axis="y", alpha=0.25)
                    ax.legend(loc="best", fontsize=7, title="Board ID", title_fontsize=8)

            for idx, ax in enumerate(axes_arr):
                if idx not in used_axes:
                    ax.set_visible(False)

            fig.suptitle(f"A2P slope distribution vs median percentiles - wavelength {wavelength} - gain {gain}", y=1.01)
            fig.tight_layout()
            fig_id = f"a2p_slope_median_std_by_board_{wavelength}_{gain}"
            fig_path = os.path.join(self.output_path, f"{fig_id}.{config.plot_output_format}")
            fig.savefig(fig_path)
            plt.close(fig)
            self.plots[fig_id] = fig_path
            logger.info("Saved plot: %s", fig_path)
        return self.plots

    def generate_a2p_slope_pct_diff_from_median_grid(self) -> dict[str, str]:
        slope_col = "a2p_slope"
        for required in ("board_id", "photodiode_id", "wavelength", "gain", slope_col):
            if required not in self.df.columns:
                raise ValueError(f"Missing required column for plotting: {required}")

        if self.df.empty:
            logger.warning("Crossboard dataframe is empty. No composed median-percent-diff plot generated.")
            return self.plots

        clean_df = self.df.dropna(subset=["board_id", "photodiode_id", "wavelength", "gain", slope_col]).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for a2p slope median-percent-diff plot.")
            return self.plots

        combos = (
            clean_df.assign(
                wavelength_s=clean_df["wavelength"].astype(str),
                gain_s=clean_df["gain"].astype(str),
            )[["wavelength_s", "gain_s"]]
            .drop_duplicates()
            .sort_values(by=["wavelength_s", "gain_s"], key=lambda s: s.map(self._sort_wavelength) if s.name == "wavelength_s" else s)
        )
        if combos.empty:
            return self.plots

        for _, combo in combos.iterrows():
            wavelength = combo["wavelength_s"]
            gain = combo["gain_s"]
            subset = clean_df[
                (clean_df["wavelength"].astype(str) == wavelength)
                & (clean_df["gain"].astype(str) == gain)
            ].copy()
            if subset.empty:
                continue

            slopes_all = subset[slope_col].astype(float).values
            median = float(np.median(slopes_all))
            if np.isclose(median, 0.0):
                logger.warning(
                    "Skipping a2p slope median-percent-diff plot for wavelength %s gain %s because median is 0.",
                    wavelength,
                    gain,
                )
                continue

            subset["slope_diff_pct"] = ((subset[slope_col].astype(float) - median) / median) * 100.0
            pct_values = subset["slope_diff_pct"].astype(float).values
            p75_pct = float(np.percentile(np.abs(pct_values), 75))

            board_ids = sorted(subset["board_id"].astype(str).unique())
            boards_by_col: dict[int, list[str]] = {0: [], 1: [], 2: []}
            other_boards: list[str] = []
            for board_id in board_ids:
                suffix = str(board_id)[-1:]
                if suffix == "0":
                    boards_by_col[0].append(board_id)
                elif suffix == "1":
                    boards_by_col[1].append(board_id)
                elif suffix == "2":
                    boards_by_col[2].append(board_id)
                else:
                    other_boards.append(board_id)
            # Keep non 0/1/2 boards visible by appending them to the first column.
            boards_by_col[0].extend(other_boards)

            ncols = 3
            nrows = max(len(boards_by_col[0]), len(boards_by_col[1]), len(boards_by_col[2]), 1)
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6 * ncols, 4.5 * nrows), sharey=False)
            axes_arr = np.array(axes).reshape(-1)
            used_axes: set[int] = set()

            for col_idx in range(ncols):
                for row_idx, board_id in enumerate(boards_by_col[col_idx]):
                    ax_idx = row_idx * ncols + col_idx
                    ax = axes_arr[ax_idx]
                    used_axes.add(ax_idx)
                    board_points = subset[subset["board_id"].astype(str) == board_id].copy()
                    board_points = board_points.sort_values(by=["photodiode_id"]).reset_index(drop=True)
                    x = np.arange(len(board_points))

                    ax.axhline(
                        0.0,
                        linestyle="--",
                        linewidth=1.5,
                        color=PLOT_STYLE["median_line"],
                        label="Median diff (0.00%)",
                    )
                    ax.fill_between(
                        [-0.5, len(board_points) - 0.5],
                        -p75_pct,
                        p75_pct,
                        color=PLOT_STYLE["band_up_to_p75"],
                        alpha=1.0,
                        label=f"Up to P75 (±{p75_pct:.2f}%)",
                    )
                    slope_diff_vals = board_points["slope_diff_pct"].astype(float).values
                    ax.scatter(
                        x,
                        slope_diff_vals,
                        s=36,
                        alpha=0.9,
                        color=PLOT_STYLE["board_point"],
                        edgecolors=PLOT_STYLE["scatter_edge"],
                        linewidths=0.25,
                        label=f"Board {board_id}",
                    )

                    # Mark out-of-range points with red arrows at the plot edge.
                    for x_i, y_i in zip(x, slope_diff_vals):
                        if y_i > 5.0:
                            ax.annotate(
                                "",
                                xy=(x_i, 4.95),
                                xytext=(x_i, 4.2),
                                arrowprops=dict(arrowstyle="-|>", color="red", lw=1.6),
                                zorder=40,
                            )
                        elif y_i < -5.0:
                            ax.annotate(
                                "",
                                xy=(x_i, -4.95),
                                xytext=(x_i, -4.2),
                                arrowprops=dict(arrowstyle="-|>", color="red", lw=1.6),
                                zorder=40,
                            )

                    labels = [str(v) for v in board_points["photodiode_id"].tolist()]
                    ax.set_xticks(x)
                    ax.set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
                    ax.set_xlim(-0.5, len(board_points) - 0.5)
                    ax.set_title(f"Board {board_id}", fontsize=10)
                    ax.set_xlabel("Photodiode ID")
                    ax.set_ylabel("A2P slope diff from median (%)")
                    ax.set_ylim(-5.0, 5.0)
                    ax.grid(True, axis="y", alpha=0.25)
                    ax.legend(loc="best", fontsize=7, title="Board ID", title_fontsize=8)

            for idx, ax in enumerate(axes_arr):
                if idx not in used_axes:
                    ax.set_visible(False)

            fig.suptitle(
                f"A2P slope % diff vs median percentiles - wavelength {wavelength} - gain {gain}",
                y=1.01,
            )
            fig.tight_layout()
            fig_id = f"a2p_slope_pct_diff_median_std_by_board_{wavelength}_{gain}"
            fig_path = os.path.join(self.output_path, f"{fig_id}.{config.plot_output_format}")
            fig.savefig(fig_path)
            plt.close(fig)
            self.plots[fig_id] = fig_path
            logger.info("Saved plot: %s", fig_path)
        return self.plots

    def generate_a2p_robust_zscore_heatmap(self) -> dict[str, str]:
        required = ("board_id", "wavelength", "gain", "a2p_slope")
        for col in required:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column for plotting: {col}")

        clean_df = self.df.dropna(subset=list(required)).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for a2p robust z-score heatmap.")
            return self.plots

        clean_df["combo"] = clean_df["wavelength"].astype(str) + "_" + clean_df["gain"].astype(str)
        board_combo = (
            clean_df.groupby(["board_id", "combo"], as_index=False)["a2p_slope"]
            .mean()
            .rename(columns={"a2p_slope": "board_mean_slope"})
        )

        combos = sorted(board_combo["combo"].astype(str).unique(), key=lambda c: self._combo_sort_key(c))
        boards = sorted(board_combo["board_id"].astype(str).unique())
        pivot = (
            board_combo.assign(board_id=board_combo["board_id"].astype(str))
            .pivot(index="board_id", columns="combo", values="board_mean_slope")
            .reindex(index=boards, columns=combos)
        )

        zmat = pd.DataFrame(index=pivot.index, columns=pivot.columns, dtype=float)
        for combo in combos:
            col = pivot[combo].astype(float)
            valid = col.dropna()
            if valid.empty:
                continue
            median = float(np.median(valid.values))
            mad = float(np.median(np.abs(valid.values - median)))
            robust_sigma = 1.4826 * mad
            if robust_sigma <= 0.0:
                z = col.apply(lambda _: 0.0 if pd.notna(_) else np.nan)
            else:
                z = (col - median) / robust_sigma
            zmat[combo] = z

        fig, ax = plt.subplots(figsize=(max(8, len(combos) * 1.2), max(5, len(boards) * 0.6)))
        arr = zmat.to_numpy(dtype=float)
        arr_plot = np.where(np.isnan(arr), 0.0, arr)
        vmax = max(3.0, float(np.nanmax(np.abs(arr))) if np.isfinite(np.nanmax(np.abs(arr))) else 3.0)
        im = ax.imshow(arr_plot, cmap=PLOT_STYLE["heatmap_cmap"], vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_title("A2P robust z-score heatmap (board mean slope)")
        ax.set_xlabel("Wavelength + Gain")
        ax.set_ylabel("Board ID")
        ax.set_xticks(np.arange(len(combos)))
        ax.set_xticklabels(combos, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(np.arange(len(boards)))
        ax.set_yticklabels(boards, fontsize=8)
        cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cbar.set_label("Robust z-score")
        fig.tight_layout()

        fig_id = "a2p_robust_zscore_heatmap"
        fig_path = os.path.join(self.output_path, f"{fig_id}.{config.plot_output_format}")
        fig.savefig(fig_path)
        plt.close(fig)
        self.plots[fig_id] = fig_path
        logger.info("Saved plot: %s", fig_path)
        return self.plots

    def export_a2p_deviation_rankings(self, top_n: int = 3) -> dict[str, str]:
        required = ("board_id", "wavelength", "gain", "a2p_slope")
        for col in required:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column for ranking: {col}")

        clean_df = self.df.dropna(subset=list(required)).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for a2p rankings.")
            return {}

        clean_df["combo"] = clean_df["wavelength"].astype(str) + "_" + clean_df["gain"].astype(str)
        board_combo = (
            clean_df.groupby(["combo", "board_id"], as_index=False)["a2p_slope"]
            .mean()
            .rename(columns={"a2p_slope": "board_mean_slope"})
        )

        rows: list[dict[str, Any]] = []
        summary: dict[str, Any] = {}
        for combo in sorted(board_combo["combo"].astype(str).unique(), key=self._combo_sort_key):
            part = board_combo[board_combo["combo"].astype(str) == combo].copy()
            if part.empty:
                continue
            median = float(np.median(part["board_mean_slope"].astype(float).values))
            part["abs_dev_pct"] = np.where(
                median == 0.0,
                0.0,
                np.abs((part["board_mean_slope"].astype(float) - median) / median) * 100.0,
            )
            part = part.sort_values(by="abs_dev_pct", ascending=False).reset_index(drop=True)
            for _, r in part.iterrows():
                rows.append(
                    {
                        "combo": combo,
                        "board_id": str(r["board_id"]),
                        "board_mean_slope": float(r["board_mean_slope"]),
                        "median_board_slope": median,
                        "abs_dev_pct": float(r["abs_dev_pct"]),
                    }
                )
            top = part.head(top_n)
            bottom = part.tail(top_n).sort_values(by="abs_dev_pct", ascending=True)
            summary[combo] = {
                "top_abs_deviation": [
                    {"board_id": str(r["board_id"]), "abs_dev_pct": float(r["abs_dev_pct"])}
                    for _, r in top.iterrows()
                ],
                "bottom_abs_deviation": [
                    {"board_id": str(r["board_id"]), "abs_dev_pct": float(r["abs_dev_pct"])}
                    for _, r in bottom.iterrows()
                ],
            }

        rankings_df = pd.DataFrame(rows)
        csv_path = os.path.join(self.output_path, "a2p_board_deviation_rankings.csv")
        json_path = os.path.join(self.output_path, "a2p_board_deviation_rankings.json")
        rankings_df.to_csv(csv_path, index=False)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "meta": {"top_n": int(top_n), "metric": "a2p_slope", "method": "board_mean_vs_combo_median"},
                    "by_combo": summary,
                },
                f,
                indent=2,
            )
        logger.info("Saved ranking CSV: %s", csv_path)
        logger.info("Saved ranking JSON: %s", json_path)
        return {"ranking_csv": csv_path, "ranking_json": json_path}

    @staticmethod
    def _sort_wavelength(value: str):
        try:
            return (0, float(value))
        except ValueError:
            return (1, value)

    @staticmethod
    def _combo_sort_key(value: str):
        parts = str(value).split("_", 1)
        wl = parts[0] if parts else str(value)
        gain = parts[1] if len(parts) > 1 else ""
        try:
            return (0, float(wl), gain)
        except ValueError:
            return (1, wl, gain)
