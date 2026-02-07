from abc import ABC, abstractmethod
import os

import pandas as pd
from matplotlib import pyplot as plt

from characterization.config import config
from characterization.helpers.file_manage import get_base_output_path

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

    def _gen_timeseries_plot(self):
        """Generate timeseries plot with dual axes for characterization data."""
        if self.df is None or self.df.empty:
            return
        fig_id = "timeseries"
        fig = plt.figure(figsize=(12, 10))

        # Top plot: ref_pd_mean and mean_adc vs time
        ax1 = plt.subplot2grid((5, 1), (0, 0), rowspan=2)
        ax1_twin = ax1.twinx()
        ax1.errorbar(self.df['datetime'], self.df['ref_pd_mean'], yerr=self.df['ref_pd_std'],
                     c='b', fmt='.', markersize=5, linewidth=1, label='Ref PD')
        ax1.set_ylabel('Ref PD (V)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        ax1_twin.errorbar(self.df['datetime'], self.df['mean_adc'], yerr=self.df['std_adc'],
                          c='r', fmt='.', markersize=5, linewidth=1, label=f'{self._pd_label()} (ADC)')
        ax1_twin.set_ylabel(f'{self._pd_label()} (ADC counts)', color='r')
        ax1_twin.tick_params(axis='y', labelcolor='r')

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc='lower right')
        ax1.set_title(f'{self._plot_label()} - Time Series')
        ax1.grid(True, alpha=0.3)

        # Middle plot: laser setpoints vs time
        ax2 = plt.subplot2grid((5, 1), (2, 0), rowspan=2)
        has_1064 = 'laser_sp_1064' in self.df.columns and self.df['laser_sp_1064'].notna().any()
        has_532 = 'laser_sp_532' in self.df.columns and self.df['laser_sp_532'].notna().any()

        if has_1064 and has_532:
            ax2.scatter(
                self.df['datetime'], self.df['laser_sp_1064'],
                c='m', label='1064nm laser setpoint (mW)', marker='.', s=10
            )
            ax2.set_ylabel('1064nm laser setpoint (mW)', color='m')
            ax2.tick_params(axis='y', labelcolor='m')

            ax2_twin = ax2.twinx()
            ax2_twin.scatter(
                self.df['datetime'], self.df['laser_sp_532'],
                c='c', label='532nm laser setpoint (mA)', marker='.', s=10
            )
            ax2_twin.set_ylabel('532nm laser setpoint (mA)', color='c')
            ax2_twin.tick_params(axis='y', labelcolor='c')

            h1, l1 = ax2.get_legend_handles_labels()
            h2, l2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(h1 + h2, l1 + l2, loc='lower right')
        elif has_1064 or has_532:
            if has_1064:
                ax2.scatter(
                    self.df['datetime'], self.df['laser_sp_1064'],
                    c='m', label='1064nm laser setpoint (mW)', marker='.', s=10
                )
                ax2.set_ylabel('1064nm laser setpoint (mW)', color='m')
                ax2.tick_params(axis='y', labelcolor='m')
            else:
                ax2.scatter(
                    self.df['datetime'], self.df['laser_sp_532'],
                    c='c', label='532nm laser setpoint (mA)', marker='.', s=10
                )
                ax2.set_ylabel('532nm laser setpoint (mA)', color='c')
                ax2.tick_params(axis='y', labelcolor='c')
            ax2.legend(loc='lower right')

        ax2.grid(True, alpha=0.3)

        # Bottom plot: Temperature and RH vs time
        ax3 = plt.subplot2grid((5, 1), (4, 0), rowspan=1)
        ax3_twin = ax3.twinx()
        ax3.plot(self.df['datetime'], self.df['temperature'], c='g', markersize=5, linewidth=1, label='Temperature')
        ax3.set_ylabel('Temperature (°C)', color='g')
        ax3.tick_params(axis='y', labelcolor='g')
        ax3_twin.plot(self.df['datetime'], self.df['RH'], c='orange', markersize=5, linewidth=1, label='Humidity')
        ax3_twin.set_ylabel('Humidity (%)', color='orange')
        ax3_twin.tick_params(axis='y', labelcolor='orange')
        ax3.set_xlabel('Time')

        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(h1 + h2, l1 + l2, loc='lower right')
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
