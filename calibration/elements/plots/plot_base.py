from abc import ABC, abstractmethod
import os

import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import to_rgba
from matplotlib.ticker import ScalarFormatter

from calibration.config import config

from calibration.helpers.file_manage import get_base_output_path

class BasePlots(ABC):
    """Abstract base class for analysis components."""

    def __init__(self, *args, **kwargs) -> None:
        self.plots = {}
        self._data_holder = None

    @property
    def colors(self) -> dict[str, str]:
        """Shared color palette for calibration plots."""
        return {
            'pm': '#1f77b4',
            'refpd': '#ff7f0e',
            'laser_1064': '#d62728',
            'laser_532': '#2ca02c',
            'ped_pm': '#6a4c93',
            'ped_refpd': '#b56576',
            # Aliases with explicit names used in reports/configs.
            'laser_setpoint_1064': '#d62728',
            'laser_setpoint_532': '#2ca02c',
            'pedestals_pm': '#6a4c93',
            'pedestals_refpd': '#b56576',
            'temperature': '#17becf',
            'humidity': '#8c564b',
            'samples': '#4c78a8',
            'samples_edge': '#2f4b7c',
            'linreg': '#9467bd',
            'compare_full': '#4c72b0',
            'compare_mean': '#dd8452',
            'compare_weighted': '#55a868',
            'text_muted': '#6e6e6e',
        }

    def alpha_color(self, color_key: str, alpha: float):
        """Return RGBA color from palette with custom transparency."""
        return to_rgba(self.colors[color_key], alpha)

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
    def ped_pm_col(self) -> str:
        """Column name for raw pedestal power meter data."""
        return self._data_holder.pedestal_pm_col

    @property
    def ped_refpd_col(self) -> str:
        """Column name for raw pedestal reference photodiode data."""
        return self._data_holder.pedestal_refpd_col

    @property
    def ped_pm_std_col(self) -> str:
        """Column name for raw pedestal power meter standard deviation data."""
        return self._data_holder.pedestal_pm_std_col

    @property
    def ped_refpd_std_col(self) -> str:
        """Column name for raw pedestal reference photodiode standard deviation data."""
        return self._data_holder.pedestal_refpd_std_col

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
                 ha='right', va='bottom', fontsize=8, color=self.colors['text_muted'])
        fig_path = os.path.join(self.output_path, f"{fig_filename or fig_id}.{plot_format}")
        plt.savefig(fig_path)
        self.add_plot_path(fig_id, fig_path)

    def _gen_temp_humidity_hists_plot(self):
        """Generate temperature and humidity plot for the calibration file data."""
        fig_id = "temperature_hist"
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['temperature'], color=self.colors['temperature'], alpha=0.7)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Frequency')
        plt.grid()
        plt.title(f'{self.level_label} - Temperatures histogram')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

        fig_id = "humidity_hist"
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['RH'], color=self.colors['humidity'], alpha=0.7)
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

        ax1.scatter(df['datetime'], df['samples'], c=self.colors['samples'], marker='.', s=20, label='PM Samples')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('PM Samples')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')
        self._format_datetime_axis(ax1)

        samples = df['samples'].dropna()
        if not samples.empty:
            min_s = int(samples.min())
            max_s = int(samples.max())
            bins = [x - 0.5 for x in range(min_s, max_s + 2)]
        else:
            bins = 1
        ax2.hist(samples, bins=bins, color=self.colors['samples'], edgecolor=self.colors['samples_edge'], linewidth=0.7, alpha=0.7)
        ax2.set_xlabel('PM Samples')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)

        self.savefig(fig, fig_id)
        plt.close(fig)

    def _format_datetime_axis(self, ax):
        """Format datetime x-axis to show only hour:minute labels."""
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

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
        ax1.errorbar(
            self.df_full['datetime'], self.df_full[self.refpd_col], yerr=self.df_full[self.refpd_std_col],
            c=self.colors['refpd'], ecolor=self.colors['refpd'],
            fmt='o', markersize=4, markerfacecolor='none', markeredgewidth=1.0,
            linewidth=1, label='Mean Ref PD'
        )
        ax1.set_ylabel('Ref PD (V)', color=self.colors['refpd'])
        ax1.tick_params(axis='y', labelcolor=self.colors['refpd'])

        ax1_twin.errorbar(
            self.df_full['datetime'], self.df_full[self.pm_col], yerr=self.df_full[self.pm_std_col],
            c=self.colors['pm'], ecolor=self.colors['pm'],
            fmt='x', markersize=4, markeredgewidth=1.0,
            linewidth=1, label='Mean pm'
        )
        ax1_twin.set_ylabel(f'Power Meter ({self.power_units})', color=self.colors['pm'])
        ax1_twin.ticklabel_format(style='sci', axis='y', scilimits=(-2,3))
        ax1_twin.tick_params(axis='y', labelcolor=self.colors['pm'])

        # single legend
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc='lower right')

        ax1.set_title(f'{self.level_label} - Time Series')
        ax1.grid(True, alpha=0.3)
        self._format_datetime_axis(ax1)


        # Middle plot: laser setpoints vs time
        ax2 = plt.subplot2grid((5, 1), (2, 0), rowspan=2)
        has_1064 = 'laser_sp_1064' in self.df_full.columns and self.df_full['laser_sp_1064'].notna().any()
        has_532 = 'laser_sp_532' in self.df_full.columns and self.df_full['laser_sp_532'].notna().any()

        if has_1064 and has_532:
            ax2.scatter(
                self.df_full['datetime'], self.df_full['laser_sp_1064'],
                c=self.colors['laser_1064'], label='1064nm laser setpoint (mW)', marker='.', s=10
            )
            ax2.set_ylabel('1064nm laser setpoint (mW)', color=self.colors['laser_1064'])
            ax2.tick_params(axis='y', labelcolor=self.colors['laser_1064'])

            ax2_twin = ax2.twinx()
            ax2_twin.scatter(
                self.df_full['datetime'], self.df_full['laser_sp_532'],
                c=self.colors['laser_532'], label='532nm laser setpoint (mV)', marker='.', s=10
            )
            ax2_twin.set_ylabel('532nm laser setpoint (mV)', color=self.colors['laser_532'])
            ax2_twin.tick_params(axis='y', labelcolor=self.colors['laser_532'])

            h1, l1 = ax2.get_legend_handles_labels()
            h2, l2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(h1 + h2, l1 + l2, loc='lower right')
        elif has_1064 or has_532:
            if has_1064:
                ax2.scatter(
                    self.df_full['datetime'], self.df_full['laser_sp_1064'],
                    c=self.colors['laser_1064'], label='1064nm laser setpoint (mW)', marker='.', s=10
                )
                ax2.set_ylabel('1064nm laser setpoint (mW)', color=self.colors['laser_1064'])
                ax2.tick_params(axis='y', labelcolor=self.colors['laser_1064'])
            else:
                ax2.scatter(
                    self.df_full['datetime'], self.df_full['laser_sp_532'],
                    c=self.colors['laser_532'], label='532nm laser setpoint (mV)', marker='.', s=10
                )
                ax2.set_ylabel('532nm laser setpoint (mV)', color=self.colors['laser_532'])
                ax2.tick_params(axis='y', labelcolor=self.colors['laser_532'])

            ax2.legend(loc='lower right')

        ax2.grid(True, alpha=0.3)
        self._format_datetime_axis(ax2)
        
        # Bottom plot: Temperature and RH vs time (1/6 height)
        ax3 = plt.subplot2grid((5, 1), (4, 0), rowspan=1)
        ax3_twin = ax3.twinx()
        
        ax3.plot(self.df_full['datetime'], self.df_full['temperature'], c=self.colors['temperature'], label='Temperature', markersize=5, linewidth=1)
        ax3.set_ylabel('Temperature (°C)', color=self.colors['temperature'])
        ax3.tick_params(axis='y', labelcolor=self.colors['temperature'])
        ax3_twin.plot(self.df_full['datetime'], self.df_full['RH'], c=self.colors['humidity'], label='Humidity', markersize=5, linewidth=1)
        ax3_twin.set_ylabel('Humidity (%)', color=self.colors['humidity'])
        ax3_twin.tick_params(axis='y', labelcolor=self.colors['humidity'])
        ax3.set_xlabel('Time')
        # single legend
        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(h1 + h2, l1 + l2, loc='lower right')

        ax3.grid(True, alpha=0.3)
        self._format_datetime_axis(ax3)
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
        dt = self._data_holder.df_pedestals['datetime'].copy()
        dt[0] = dt.iloc[0] - pd.Timedelta(minutes=100)
        dt[-1] = dt.iloc[-1] + pd.Timedelta(minutes=100)
        # ─────────────────────────────
        # Top plot: pm pedestals
        # ─────────────────────────────
        ax1.errorbar(
            self._data_holder.df_pedestals['datetime'], self._data_holder.df_pedestals[self.ped_pm_col],
            yerr=self._data_holder.df_pedestals[self.ped_pm_std_col],
            fmt='.', markersize=10, linewidth=1,
            label='pm Pedestals',
            color=self.colors['ped_pm'],
            ecolor=self.colors['ped_pm']
        )
        pm_stats = self._anal.pedestal_stats.pm
        if pm_stats.weighted:
            pm_mean = pm_stats.w_mean
            pm_std = pm_stats.w_stderr
            pm_label = 'PM weighted mean'
            pm_band_label = f'PM weighted {pm_mean:.2g} +/- {pm_std:.2g}'
        else:
            pm_mean = pm_stats.mean
            pm_std = pm_stats.std
            pm_label = 'PM mean'
            pm_band_label = f'PM mean {pm_mean:.2g} +/- {pm_std:.2g}'
        ax1.axhline(y=pm_mean, color=self.colors['ped_pm'], linestyle='--', label=pm_label)
        ax1.fill_between(
            dt,
            pm_mean - pm_std,
            pm_mean + pm_std,
            color=self.alpha_color('ped_pm', 0.2),
            label=pm_band_label
        )
        # Avoid combined exponent like "1e-8-1e-1" from mixed-scale data
        pm_formatter = ScalarFormatter(useMathText=True)
        pm_formatter.set_scientific(True)
        pm_formatter.set_useOffset(False)
        ax1.yaxis.set_major_formatter(pm_formatter)
        ax1.set_ylabel(f'Pedestals pm ({self.power_units})')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        self._format_datetime_axis(ax1)

        # ─────────────────────────────
        # Bottom plot: RefPD pedestals
        # ─────────────────────────────
        ax2.errorbar(
            self._data_holder.df_pedestals['datetime'], self._data_holder.df_pedestals[self.ped_refpd_col],
            yerr=self._data_holder.df_pedestals[self.ped_refpd_std_col],
            fmt='.', markersize=10, linewidth=1,
            label='RefPD Pedestals',
            color=self.colors['ped_refpd'],
            ecolor=self.colors['ped_refpd']
        )
        refpd_stats = self._anal.pedestal_stats.refpd
        if refpd_stats.weighted:
            refpd_label = 'RefPD weighted mean'
            refpd_band_label = 'RefPD weighted mean +/- stderr'
            refpd_mean = refpd_stats.w_mean
            refpd_std = refpd_stats.w_stderr
        else:
            refpd_label = 'RefPD mean'
            refpd_band_label = 'RefPD mean +/- std'
            refpd_mean = refpd_stats.mean
            refpd_std = refpd_stats.std
        ax2.axhline(y=refpd_mean, color=self.colors['ped_refpd'], linestyle='--', label=refpd_label)

        ax2.fill_between(
            dt,
            refpd_mean - refpd_std,
            refpd_mean + refpd_std,
            color=self.alpha_color('ped_refpd', 0.2),
            label=refpd_band_label
        )
        ax2.set_ylabel('Pedestals RefPD (V)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        dt = self._data_holder.df_pedestals['datetime'].copy()
        delta = (dt.iloc[-1] - dt.iloc[0]).total_seconds()/60  # delta in minutes
        dt[0] = dt.iloc[0] - pd.Timedelta(minutes=delta * 0.05)
        dt[-1] = dt.iloc[-1] + pd.Timedelta(minutes=delta * 0.05)
        ax2.set_xlim(dt.iloc[0], dt.iloc[-1])
        self._format_datetime_axis(ax2)

        self.savefig(fig, fig_id)
        plt.close(fig)
    
