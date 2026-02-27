from abc import ABC, abstractmethod
import os

import pandas as pd
from matplotlib import pyplot as plt

from characterization.config import config
from characterization.helpers.file_manage import get_base_output_path
from .style_spec import BAND_ALPHA, MEAN_LINESTYLE, metric_style

class BasePlots(ABC):
    def __init__(self) -> None:
        self.plots = {}
        self._data_holder = None

    @property
    def dh(self):
        return self._data_holder

    @property
    def df(self) -> pd.DataFrame:
        return self._data_holder.df

    @property
    def df_pedestals(self) -> pd.DataFrame:
        return self._data_holder.df_pedestals

    @property
    def df_full(self) -> pd.DataFrame:
        return self._data_holder.df_full

    @property
    def level_label(self) -> str:
        return self._data_holder.level_header

    @property
    @abstractmethod
    def output_path(self) -> str:
        pass

    @abstractmethod
    def generate_plots(self):
        pass

    def add_plot_path(self, fig_id: str, fig_path: str):
        base_output_path = get_base_output_path()
        fig_path = os.path.relpath(fig_path, start=base_output_path)
        self.plots[fig_id] = fig_path

    def savefig(self, fig, fig_id: str, fig_filename: str | None = None):
        plot_format = config.plot_output_format
        fig.text(0.99, 0.01, self._plot_label(),
                 ha='right', va='bottom', fontsize=8, color='gray')
        fig_path = os.path.join(self.output_path, f"{fig_filename or fig_id}.{plot_format}")
        plt.savefig(fig_path)
        self.add_plot_path(fig_id, fig_path)

    def _plot_label(self) -> str:
        dh = self._data_holder
        if hasattr(dh, 'plot_label'):
            return dh.plot_label
        return str(dh.long_label)

    def _pd_label(self) -> str:
        dh = self._data_holder
        if hasattr(dh, 'sensor_id'):
            return f"PD{dh.sensor_id}"
        if hasattr(dh, 'dh_parent') and hasattr(dh.dh_parent, 'sensor_id'):
            return f"PD{dh.dh_parent.sensor_id}"
        return "PD"

    def _style(self, metric: str) -> dict[str, str]:
        return metric_style(metric)

    def _c(self, metric: str) -> str:
        return self._style(metric)["color"]

    def _m(self, metric: str) -> str:
        return self._style(metric)["marker"]

    def _ls(self, metric: str) -> str:
        return self._style(metric)["linestyle"]

    def _series_marker(self, series_idx: int, base_marker: str | None = None) -> str:
        if base_marker:
            markers = [base_marker,"1", "2", "3", "4", "o", "x", "s", "^", "d", "+", "v", "*", "P"]
        else:
            markers = ["1", "2", "3", "4", "o", "x", "s", "^", "d", "+", "v", "*", "P", "."]
        return markers[series_idx % len(markers)]

    def _apply_axis_metric_color(self, ax, metric: str, axis: str = "y"):
        color = self._c(metric)
        if axis == "x":
            ax.tick_params(axis="x", labelcolor=color)
            return
        ax.tick_params(axis="y", labelcolor=color)

    def _draw_confidence_band(self, ax, mean: float, std: float, metric: str, orientation: str = "h"):
        color = self._c(metric)
        if orientation == "v":
            ax.axvspan(mean - std, mean + std, color=color, alpha=BAND_ALPHA, label="mean ± std", zorder=0)
            ax.axvline(mean, color=color, linestyle=MEAN_LINESTYLE, linewidth=1.5, label="mean", zorder=1)
            return
        ax.axhspan(mean - std, mean + std, color=color, alpha=BAND_ALPHA, label="mean ± std", zorder=0)
        ax.axhline(mean, color=color, linestyle=MEAN_LINESTYLE, linewidth=1.5, label="mean", zorder=1)

    def _gen_timeseries_plot(self):
        """Generate timeseries plot with dual axes for characterization data."""
        if self.df_full is None or self.df_full.empty:
            return
        dt_min = self.df_full['datetime'].min()
        dt_max = self.df_full['datetime'].max()
        if pd.isna(dt_min) or pd.isna(dt_max):
            return
        dt_span = dt_max - dt_min
        if dt_span == pd.Timedelta(0):
            dt_span = pd.Timedelta(seconds=1)
        left_pad = dt_span * 0.01
        right_pad = dt_span * 0.2
        x_limits = (dt_min - left_pad, dt_max + right_pad)
        fig_id = "timeseries"
        fig = plt.figure(figsize=(12, 10))

        # Top plot: ref_pd_mean and mean_adc vs time
        ax1 = plt.subplot2grid((5, 1), (0, 0), rowspan=2)
        ax1_twin = ax1.twinx()
        ax1.errorbar(self.df_full['datetime'], self.df_full['ref_pd_mean'], yerr=self.df_full['ref_pd_std'],
                     c=self._c("ref_pd_mean"), fmt=self._m("ref_pd_mean"), markersize=5, linewidth=1, label='Ref PD')
        ax1.set_ylabel('Ref PD (V)', color=self._c("ref_pd_mean"))
        self._apply_axis_metric_color(ax1, "ref_pd_mean", axis="y")

        ax1_twin.errorbar(self.df_full['datetime'], self.df_full['mean_adc'], yerr=self.df_full['std_adc'],
                          c=self._c("mean_adc"), fmt=self._m("mean_adc"), markersize=5, linewidth=1, label=f'{self._pd_label()} (ADC)')
        ax1_twin.set_ylabel(f'{self._pd_label()} (ADC counts)', color=self._c("mean_adc"))
        self._apply_axis_metric_color(ax1_twin, "mean_adc", axis="y")

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc='upper right')
        ax1.set_title(f'{self._plot_label()} - Time Series')
        ax1.set_xlim(x_limits)
        ax1.grid(True)

        # Middle plot: laser setpoints vs time
        ax2 = plt.subplot2grid((5, 1), (2, 0), rowspan=2)
        has_1064 = 'laser_sp_1064' in self.df_full.columns and self.df_full['laser_sp_1064'].notna().any()
        has_532 = 'laser_sp_532' in self.df_full.columns and self.df_full['laser_sp_532'].notna().any()

        if has_1064 and has_532:
            ax2_twin = ax2.twinx()
            ax2_twin.scatter(
                self.df_full['datetime'], self.df_full['laser_sp_1064'],
                c=self._c("laser_sp_1064"), label='1064nm laser setpoint (mW)', marker=self._m("laser_sp_1064"), s=10
            )
            ax2_twin.set_ylabel('1064nm laser setpoint (mW)', color=self._c("laser_sp_1064"))
            self._apply_axis_metric_color(ax2_twin, "laser_sp_1064", axis="y")

            ax2.scatter(
                self.df_full['datetime'], self.df_full['laser_sp_532'],
                c=self._c("laser_sp_532"), label='532nm laser setpoint (mA)', marker=self._m("laser_sp_532"), s=10
            )
            ax2.set_ylabel('532nm laser setpoint (mA)', color=self._c("laser_sp_532"))
            self._apply_axis_metric_color(ax2, "laser_sp_532", axis="y")

            h1, l1 = ax2.get_legend_handles_labels()
            h2, l2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(h1 + h2, l1 + l2, loc='upper right')
        elif has_1064 or has_532:
            if has_1064:
                ax2.scatter(
                    self.df_full['datetime'], self.df_full['laser_sp_1064'],
                    c=self._c("laser_sp_1064"), label='1064nm laser setpoint (mW)', marker=self._m("laser_sp_1064"), s=10
                )
                ax2.set_ylabel('1064nm laser setpoint (mW)', color=self._c("laser_sp_1064"))
                self._apply_axis_metric_color(ax2, "laser_sp_1064", axis="y")
            else:
                ax2.scatter(
                    self.df_full['datetime'], self.df_full['laser_sp_532'],
                    c=self._c("laser_sp_532"), label='532nm laser setpoint (mA)', marker=self._m("laser_sp_532"), s=10
                )
                ax2.set_ylabel('532nm laser setpoint (mA)', color=self._c("laser_sp_532"))
                self._apply_axis_metric_color(ax2, "laser_sp_532", axis="y")
            ax2.legend(loc='upper right')

        ax2.set_xlim(x_limits)
        ax2.grid(True)

        # Bottom plot: Temperature and RH vs time
        ax3 = plt.subplot2grid((5, 1), (4, 0), rowspan=1)
        ax3_twin = ax3.twinx()
        ax3.plot(
            self.df_full['datetime'],
            self.df_full['temperature'],
            c=self._c("temperature"),
            marker=self._m("temperature"),
            linestyle=self._ls("temperature"),
            markersize=5,
            linewidth=1,
            label='Temperature',
        )
        ax3.set_ylabel('Temperature (°C)', color=self._c("temperature"))
        self._apply_axis_metric_color(ax3, "temperature", axis="y")
        ax3_twin.plot(
            self.df_full['datetime'],
            self.df_full['RH'],
            c=self._c("RH"),
            marker=self._m("RH"),
            linestyle=self._ls("RH"),
            markersize=5,
            linewidth=1,
            label='Humidity',
        )
        ax3_twin.set_ylabel('Humidity (%)', color=self._c("RH"))
        self._apply_axis_metric_color(ax3_twin, "RH", axis="y")
        ax3.set_xlabel('Time')

        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(h1 + h2, l1 + l2, loc='upper right')
        ax3.set_xlim(x_limits)
        ax3.grid(True)

        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
