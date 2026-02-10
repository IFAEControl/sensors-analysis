"""Characterization plots across photodiodes"""

from typing import TYPE_CHECKING

from characterization.helpers import get_logger
from characterization.config import config
from .plot_base import BasePlots
from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from ..characterization import Characterization

logger = get_logger()

class CharacterizationPlots(BasePlots):
    def __init__(self, characterization: 'Characterization'):
        super().__init__()
        self._data_holder: Characterization = characterization
        self.outpath = characterization.output_path

    @property
    def output_path(self) -> str:
        return self.outpath

    def generate_plots(self):
        if not config.generate_plots:
            return
        self._gen_saturation_points_by_filter()
        self._gen_run_linreg_summary(include_rp=True)
        self._gen_run_linreg_summary(include_rp=False)
        self._gen_refpd_pedestals_timeseries(include_temp=False)
        self._gen_refpd_pedestals_timeseries(include_temp=True)
        self._gen_refpd_pedestals_histogram()

    def _gen_saturation_points_by_filter(self):
        expected_runs = sorted({
            run
            for sensor_cfg in config.sensor_config.values()
            for run in sensor_cfg.get('expected_runs', [])
        })
        if not expected_runs:
            logger.warning("No expected runs found in configuration; skipping saturation plots.")
            return

        def sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except ValueError:
                return sensor_id

        sensors = sorted(config.sensor_config.keys(), key=sensor_sort_key)

        run_labels = expected_runs[:3]
        if len(expected_runs) > 3:
            logger.warning(
                "More than 3 wavelength/filter combinations found (%s). Plotting first 3: %s",
                len(expected_runs),
                run_labels
            )

        fig, axes = plt.subplots(nrows=len(run_labels), ncols=1, figsize=(12, 4 * len(run_labels)), sharex=True)
        if len(run_labels) == 1:
            axes = [axes]

        bar_color = "#2A9D8F"
        for ax, run_label in zip(axes, run_labels):
            counts = []
            for sensor_id in sensors:
                pdh = self._data_holder.photodiodes.get(sensor_id)
                if pdh is None:
                    counts.append(0)
                    continue
                fs = pdh.filesets.get(run_label)
                if fs is None:
                    counts.append(0)
                    continue
                stats = getattr(fs.anal, "_saturation_stats", {}) or {}
                if "num_saturated" in stats:
                    counts.append(int(stats["num_saturated"]))
                elif fs.df_sat is not None:
                    counts.append(int(fs.df_sat.shape[0]))
                else:
                    counts.append(0)

            ax.bar(sensors, counts, color=bar_color, label="Saturated points")
            ax.set_ylabel("Saturated points")
            ax.set_title(f"Saturation points - {run_label}")
            ax.grid(True, axis='y', alpha=0.3)
            ax.legend(loc='upper right')

        axes[-1].set_xlabel("Sensor")
        plt.setp(axes[-1].get_xticklabels(), rotation=45, ha='right')
        fig.suptitle(f"{self._plot_label()} - Saturation points by wavelength/filter", y=1.02)
        plt.tight_layout()
        self.savefig(fig, "saturation_points_by_filter")
        plt.close(fig)

    def _gen_run_linreg_summary(self, include_rp: bool = True):
        run_labels = sorted({
            run
            for sensor_cfg in config.sensor_config.values()
            for run in sensor_cfg.get('expected_runs', [])
        })
        if not run_labels:
            logger.warning("No wavelength/filter combinations found; skipping run linreg summary.")
            return

        def sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except ValueError:
                return sensor_id

        slope_color = "#6A4C93"
        intercept_color = "#F4A261"
        r_color = "#2A9D8F"
        p_color = "#8E9AAF"
        for run_label in run_labels:
            sensors = []
            slopes = []
            slope_errs = []
            intercepts = []
            intercept_errs = []
            r_values = []
            p_values = []

            for sensor_id, pdh in self._data_holder.photodiodes.items():
                fs = pdh.filesets.get(run_label)
                if fs is None or fs.anal.lr_refpd_vs_adc.linreg is None:
                    continue
                lr = fs.anal.lr_refpd_vs_adc
                sensors.append(sensor_id)
                slopes.append(float(lr.slope))
                slope_errs.append(float(lr.stderr))
                intercepts.append(float(lr.intercept))
                intercept_errs.append(float(lr.intercept_stderr))
                r_values.append(float(lr.r_value))
                p_values.append(float(lr.p_value))

            if not sensors:
                logger.warning("No sensors with linreg data for %s; skipping plot.", run_label)
                continue

            rows = sorted(
                zip(sensors, slopes, slope_errs, intercepts, intercept_errs, r_values, p_values),
                key=lambda row: sensor_sort_key(row[0])
            )
            sensors, slopes, slope_errs, intercepts, intercept_errs, r_values, p_values = map(list, zip(*rows))

            nrows = 3 if include_rp else 2
            fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(12, 4 * nrows), sharex=True)

            axes[0].errorbar(sensors, slopes, yerr=slope_errs, fmt='o', color=slope_color, label='Slope')
            axes[0].set_ylabel("Slope", color=slope_color)
            axes[0].tick_params(axis='y', labelcolor=slope_color)
            axes[0].grid(True, axis='y', alpha=0.3)
            axes[0].legend(loc='upper right')
            axes[0].set_title(f"Summary of linear regression values for {run_label.replace('_', ' - ')}")

            axes[1].errorbar(sensors, intercepts, yerr=intercept_errs, fmt='s', color=intercept_color, label='Intercept')
            axes[1].set_ylabel("Intercept", color=intercept_color)
            axes[1].tick_params(axis='y', labelcolor=intercept_color)
            axes[1].grid(True, axis='y', alpha=0.3)
            axes[1].legend(loc='upper right')

            if include_rp:
                ax_r = axes[2]
                ax_p = ax_r.twinx()
                ax_r.scatter(sensors, r_values, marker='o', color=r_color, label='r-value')
                ax_r.set_ylabel("r", color=r_color)
                ax_r.tick_params(axis='y', labelcolor=r_color)
                ax_r.grid(True, axis='y', alpha=0.3)

                ax_p.scatter(sensors, p_values, marker='s', color=p_color, label='p-value')
                ax_p.set_ylabel("p", color=p_color)
                ax_p.tick_params(axis='y', labelcolor=p_color)

                h1, l1 = ax_r.get_legend_handles_labels()
                h2, l2 = ax_p.get_legend_handles_labels()
                ax_r.legend(h1 + h2, l1 + l2, loc='upper right')

            axes[-1].set_xlabel("Sensor")
            plt.setp(axes[-1].get_xticklabels(), rotation=45, ha='right')
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            suffix = "" if include_rp else "_simp"
            self.savefig(fig, f"linreg_summary_{run_label}{suffix}")
            plt.close(fig)

    def _gen_refpd_pedestals_timeseries(self, include_temp: bool = False):
        df = self._data_holder.df_pedestals
        if df is None or df.empty:
            logger.warning("No pedestal data available for characterization ref_pd timeseries plot.")
            return

        fig_id = "refpd_pedestals_timeseries" + ("_temp" if include_temp else "")
        fig, ax = plt.subplots(figsize=(12, 6))

        if 'datetime' in df.columns:
            x = df['datetime']
        else:
            x = range(len(df))

        y = df['ref_pd_mean']
        mean = float(y.mean())
        std = float(y.std())
        ax.axhspan(mean - std, mean + std, color='#2A9D8F', alpha=0.15, label='mean ± std', zorder=0)
        ax.axhline(mean, color='#2A9D8F', linestyle='--', linewidth=1.5, label='mean', zorder=1)
        ax.errorbar(x, y, yerr=df['ref_pd_std'], color="#036358", fmt='.', markersize=5, linewidth=1, label='RefPD pedestals', zorder=20)

        ax.set_title("characterization ref PD pedestals")
        ax.set_ylabel("RefPD (V)")
        ax.set_xlabel("Time" if 'datetime' in df.columns else "Index")
        ax.grid(True, alpha=0.3)

        if include_temp and 'temperature' in df.columns:
            ax_temp = ax.twinx()
            ax_temp.plot(x, df['temperature'], color="#256AB9", linewidth=1.2, label='Temperature')
            ax_temp.set_ylabel("Temperature (°C)", color="#256AB9")
            ax_temp.tick_params(axis='y', labelcolor="#256AB9")
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax_temp.get_legend_handles_labels()
            ax.legend(h1 + h2, l1 + l2, loc='best')
        else:
            ax.legend(loc='best')

        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_refpd_pedestals_histogram(self):
        df = self._data_holder.df_pedestals
        if df is None or df.empty:
            logger.warning("No pedestal data available for characterization ref_pd histogram plot.")
            return

        fig_id = "refpd_pedestals_histogram"
        fig, ax = plt.subplots(figsize=(10, 6))

        y = df['ref_pd_mean']
        mean = float(y.mean())
        std = float(y.std())
        ax.axvspan(mean - std, mean + std, color="#2A9D8F", alpha=0.15, label="mean ± std", zorder=0)
        ax.axvline(mean, color="#2A9D8F", linestyle="--", linewidth=1.5, label="mean", zorder=0.5)
        ax.hist(y, bins=40, color="#6A4C93", alpha=0.7, label="RefPD pedestals", zorder=2)

        ax.set_title("characterization ref PD pedestals histogram")
        ax.set_xlabel("RefPD (V)")
        ax.set_ylabel("Count")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')

        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
