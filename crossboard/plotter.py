from __future__ import annotations

import os
from typing import Any

from matplotlib import pyplot as plt

from .config import config
from .dataframe import CrossboardDataFrame
from .helpers import get_logger

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
        cmap = plt.get_cmap("tab20", max(len(board_ids), 1))
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
                    edgecolors="black",
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
        for required in ("wavelength", slope_col, intercept_col):
            if required not in self.df.columns:
                raise ValueError(f"Missing required column for plotting: {required}")

        if self.df.empty:
            logger.warning("Crossboard dataframe is empty. No histogram plots generated.")
            return self.plots

        clean_df = self.df.dropna(subset=["wavelength", slope_col, intercept_col]).copy()
        if clean_df.empty:
            logger.warning("Crossboard dataframe has no valid rows for %s histograms.", metric)
            return self.plots

        wavelengths = sorted(clean_df["wavelength"].astype(str).unique(), key=self._sort_wavelength)
        for wavelength in wavelengths:
            subset = clean_df[clean_df["wavelength"].astype(str) == wavelength]
            if subset.empty:
                continue

            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(9, 8), sharex=False)

            axes[0].hist(subset[slope_col], bins=20, color="#2A9D8F", edgecolor="black", alpha=0.8)
            axes[0].set_title(f"{metric.upper()} slope histogram - wavelength {wavelength}")
            axes[0].set_xlabel(f"{metric.upper()} slope")
            axes[0].grid(True, axis="y", alpha=0.3)

            axes[1].hist(subset[intercept_col], bins=20, color="#E76F51", edgecolor="black", alpha=0.8)
            axes[1].set_title(f"{metric.upper()} intercept histogram - wavelength {wavelength}")
            axes[1].set_xlabel(f"{metric.upper()} intercept")
            axes[1].grid(True, axis="y", alpha=0.3)

            fig.tight_layout()
            fig_id = f"{metric}_histograms_{wavelength}"
            fig_path = os.path.join(self.output_path, f"{fig_id}.{config.plot_output_format}")
            fig.savefig(fig_path)
            plt.close(fig)
            self.plots[fig_id] = fig_path
            logger.info("Saved plot: %s", fig_path)

        return self.plots

    @staticmethod
    def _sort_wavelength(value: str):
        try:
            return (0, float(value))
        except ValueError:
            return (1, value)
