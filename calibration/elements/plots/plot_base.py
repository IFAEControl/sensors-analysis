from abc import ABC, abstractmethod
import os
from venv import logger

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter

from calibration.config import config

from calibration.helpers.file_manage import get_base_output_path

class BasePlots(ABC):
    """Abstract base class for analysis components."""

    def __init__(self, *args, **kwargs) -> None:
        self.plots = {}
        self._data_holder = None

    @property
    def _anal(self):
        """Shortcut to analysis component."""
        return self._data_holder.anal
    
    @property
    def dh(self):
        """Shortcut to data holder."""
        return self._data_holder

    @property
    def refpd_col(self) -> str:
        """Column name for reference photodiode data."""
        return self._data_holder.refpd_col
    @property
    def pm_col(self) -> str:
        """Column name for power meter data."""
        return self._data_holder.pm_col
    
    @property
    def refpd_std_col(self) -> str:
        """Column name for reference photodiode standard deviation data."""
        return self._data_holder.refpd_std_col
    @property
    def pm_std_col(self) -> str:
        """Column name for power meter standard deviation data."""
        return self._data_holder.pm_std_col

    @property
    def level_label(self) -> str:
        """Label for the data holder level."""
        return self._data_holder.level_header
    

    @property
    @abstractmethod
    def laser_label(self) -> str:
        """Label for the laser parameter."""
        pass

    @property
    @abstractmethod
    def output_path(self) -> str:
        """Output path for storing analysis results and plots."""
        pass
    

    @property
    def df(self) -> pd.DataFrame:
        """DataFrame containing the data to be analyzed."""
        return self._data_holder.df
    
    @property
    def df_pedestals(self) -> pd.DataFrame:
        """DataFrame containing the pedestal data to be analyzed."""
        return self._data_holder.df_pedestals
    
    @property
    def df_full(self) -> pd.DataFrame:
        """DataFrame containing the full data to be analyzed."""
        return self._data_holder.df_full


    @abstractmethod
    def generate_plots(self):
        """Generate plots for the analysis."""
        pass


    @property
    def power_units(self) -> str:
        """Return the units used for power measurements."""
        return 'uW' if config.use_uW_as_power_units else 'W'
    
    def add_plot_path(self, fig_id: str, fig_path: str):
        """Add a plot to the summary dictionary.

        Args:
            fig_id (str): Identifier for the figure.
            fig_path (str): Path to the saved figure.
        """
        # user provides a path, where we create a folder to sustain everything
        base_output_path = get_base_output_path()
        fig_path = os.path.relpath(fig_path, start=base_output_path)
        self.plots[fig_id] = fig_path
    
    def savefig(self, fig, fig_id: str, fig_filename: str|None = None):
        """Save current plt matplotlib figure to the output path and register it.
        Save format is set globally in file_manage module.
        Args:
            fig_id (str): Identifier for the figure.
            fig_filename (str, optional): Filename for the figure. If None, uses fig_id. Defaults to None.
        """
        plot_format = config.plot_output_format  # Get the plot format from the config module
        fig.text(0.99, 0.01, f'{self._data_holder.long_label}', 
                 ha='right', va='bottom', fontsize=8, color='gray')
        fig_path = os.path.join(self.output_path, f"{fig_filename or fig_id}.{plot_format}")
        plt.savefig(fig_path)
        self.add_plot_path(fig_id, fig_path)

    def _gen_temp_humidity_hists_plot(self):
        """Generate temperature and humidity plot for the calibration file data."""
        fig_id = "temperature_hist"
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['temperature'], color='blue', alpha=0.7)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Frequency')
        plt.grid()
        plt.title(f'{self.level_label} - Temperatures histogram')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

        fig_id = "humidity_hist"
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['RH'], color='blue', alpha=0.7)
        plt.xlabel('Humidity (%)')
        plt.ylabel('Frequency')
        plt.grid()
        plt.title(f'{self.level_label} - Humidity histogram')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_samples_plot(self, df: pd.DataFrame, fig_id: str):
        """Generate samples timeseries and histogram plot using provided DataFrame."""
        fig, (ax1, ax2) = plt.subplots(
            nrows=2, ncols=1,
            figsize=(10, 8),
            constrained_layout=True
        )

        ax1.scatter(df['datetime'], df['samples'], c='teal', marker='.', s=20, label='PM Samples')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('PM Samples')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')

        samples = df['samples'].dropna()
        if not samples.empty:
            min_s = int(samples.min())
            max_s = int(samples.max())
            bins = [x - 0.5 for x in range(min_s, max_s + 2)]
        else:
            bins = 1
        ax2.hist(samples, bins=bins, color='teal', edgecolor='darkslategray', linewidth=0.7, alpha=0.7)
        ax2.set_xlabel('PM Samples')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)

        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_pm_samples_plot_full(self):
        """Generate samples plot using df_full."""
        fig_id = "pm_samples_full"
        self._gen_samples_plot(self.df_full, fig_id)

    def _gen_pm_samples_plot_pedestals(self):
        """Generate samples plot using df_pedestals."""
        fig_id = "pm_samples_pedestals"
        self._gen_samples_plot(self.df_pedestals, fig_id)

    def _gen_timeseries_plot(self):
        """Generate timeseries plot with dual axes for calibration file data."""
        fig_id = "timeseries"
        fig = plt.figure(figsize=(12, 10))

        # Top plot: ref_pd_mean and pm_mean vs time (2/3 height)
        ax1 = plt.subplot2grid((5, 1), (0, 0), rowspan=2)
        ax1_twin = ax1.twinx()
        # ax1.plot(self.df['datetime'], self.df['ref_pd_mean'], 'b-', label='Mean Ref PD', linewidth=2)
        ax1.errorbar(self.df['datetime'], self.df[self.refpd_col], yerr=self.df[self.refpd_std_col], c='b', fmt='.', markersize=5, linewidth=1, label='Mean Ref PD')
        ax1.set_ylabel('Ref PD (V)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        ax1_twin.errorbar(self.df['datetime'], self.df[self.pm_col], yerr=self.df[self.pm_std_col], c='r', fmt='.', markersize=5, linewidth=1, label='Mean pm')
        ax1_twin.set_ylabel(f'Power Meter ({self.power_units})', color='r')
        ax1_twin.ticklabel_format(style='sci', axis='y', scilimits=(-2,3))
        ax1_twin.tick_params(axis='y', labelcolor='r')

        # single legend
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc='lower right')

        ax1.set_title(f'{self.level_label} - Time Series')
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
                c='c', label='532nm laser setpoint (mV)', marker='.', s=10
            )
            ax2_twin.set_ylabel('532nm laser setpoint (mV)', color='c')
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
                    c='c', label='532nm laser setpoint (mV)', marker='.', s=10
                )
                ax2.set_ylabel('532nm laser setpoint (mV)', color='c')
                ax2.tick_params(axis='y', labelcolor='c')

            ax2.legend(loc='lower right')

        ax2.grid(True, alpha=0.3)
        
        # Bottom plot: Temperature and RH vs time (1/6 height)
        ax3 = plt.subplot2grid((5, 1), (4, 0), rowspan=1)
        ax3_twin = ax3.twinx()
        
        ax3.plot(self.df['datetime'], self.df['temperature'], c='g', label='Temperature', markersize=5, linewidth=1)
        ax3.set_ylabel('Temperature (°C)', color='g')
        ax3.tick_params(axis='y', labelcolor='g')
        ax3_twin.plot(self.df['datetime'], self.df['RH'], c='orange', label='Humidity', markersize=5, linewidth=1)
        ax3_twin.set_ylabel('Humidity (%)', color='orange')
        ax3_twin.tick_params(axis='y', labelcolor='orange')
        ax3.set_xlabel('Time')
        # single legend
        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(h1 + h2, l1 + l2, loc='lower right')

        ax3.grid(True, alpha=0.3)
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_pedestals_timeseries_plot(self):
        """Generate pedestal plot for the set of calibration files"""
        fig_id = "pedestals_timeseries"

        fig, (ax1, ax2) = plt.subplots(
            nrows=2, ncols=1,
            figsize=(10, 6),
            sharex=True,
            constrained_layout=True
        )

        x = range(len(self._data_holder.df_pedestals))

        # ─────────────────────────────
        # Top plot: pm pedestals
        # ─────────────────────────────
        ax1.errorbar(
            self._data_holder.df_pedestals['datetime'], self._data_holder.df_pedestals['pm_mean'],
            yerr=self._data_holder.df_pedestals['pm_std'],
            fmt='.', markersize=10, linewidth=1,
            label='pm Pedestals'
        )
        # Avoid combined exponent like "1e-8-1e-1" from mixed-scale data
        pm_formatter = ScalarFormatter(useMathText=True)
        pm_formatter.set_scientific(True)
        pm_formatter.set_useOffset(False)
        ax1.yaxis.set_major_formatter(pm_formatter)
        ax1.set_ylabel(f'Pedestals pm ({self.power_units})')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # ─────────────────────────────
        # Bottom plot: RefPD pedestals
        # ─────────────────────────────
        ax2.errorbar(
            self._data_holder.df_pedestals['datetime'], self._data_holder.df_pedestals["ref_pd_mean"],
            yerr=self._data_holder.df_pedestals["ref_pd_std"],
            fmt='.', markersize=10, linewidth=1,
            label='RefPD Pedestals'
        )
        ax2.set_ylabel('Pedestals RefPD (V)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        self.savefig(fig, fig_id)
        plt.close(fig)
    
