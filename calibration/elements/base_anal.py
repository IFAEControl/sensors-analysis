from abc import ABC, abstractmethod
import os
from venv import logger

from matplotlib import pyplot as plt

from calibration.helpers.filepaths import get_base_output_path

class BaseAnal(ABC):
    """Abstract base class for analysis components."""

    def __init__(self, *args, **kwargs) -> None:
        self.plots = {}

    @property
    @abstractmethod
    def anal_label(self) -> str:
        """Label for the analysis."""
        pass

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
    @abstractmethod
    def df(self):
        """DataFrame containing the data to be analyzed."""
        pass

    @abstractmethod
    def analyze(self):
        """Perform the analysis."""
        pass
    @abstractmethod
    def generate_plots(self):
        """Generate plots for the analysis."""
        pass
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert analysis results to a dictionary."""
        pass

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

    def _gen_temp_humidity_hists_plot(self):
        """Generate temperature and humidity plot for the calibration file data."""
        fig_id = "temperature_hist"
        fig_path = os.path.join(self.output_path, fig_id + '.png')
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['Temp'], color='blue', alpha=0.7)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Frequency')
        plt.grid()
        plt.title(f'{self.anal_label} - Temperatures histogram')
        plt.tight_layout()
        plt.savefig(fig_path)  # Save the current plot
        plt.close(fig)
        self.add_plot_path(fig_id, fig_path)

        fig_id = "humidity_hist"
        fig_path = os.path.join(self.output_path, fig_id + '.png')
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['RH'], color='blue', alpha=0.7)
        plt.xlabel('Humidity (%)')
        plt.ylabel('Frequency')
        plt.grid()
        plt.title(f'{self.anal_label} - Humidity histogram')
        plt.tight_layout()
        plt.savefig(fig_path)  # Save the current plot
        plt.close(fig)
        self.add_plot_path(fig_id, fig_path)

    def _gen_timeseries_plot(self):
        """Generate timeseries plot with dual axes for calibration file data."""
        fig_id = "timeseries"
        fig_path = os.path.join(self.output_path, fig_id + '.png')
        fig = plt.figure(figsize=(12, 10))

        # Top plot: meanRefPD and meanPM vs time (2/3 height)
        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=3)
        ax1_twin = ax1.twinx()
        # ax1.plot(self.df['datetime'], self.df['meanRefPD'], 'b-', label='Mean Ref PD', linewidth=2)
        ax1.errorbar(self.df['datetime'], self.df['meanRefPD'], yerr=self.df['stdRefPD'], c='b', fmt='.', markersize=5, linewidth=1, label='Mean Ref PD')
        ax1.set_ylabel('Mean Ref PD (V)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        ax1_twin.errorbar(self.df['datetime'], self.df['meanPM'], yerr=self.df['stdPM'], c='r', fmt='.', markersize=5, linewidth=1, label='Mean PM')
        ax1_twin.set_ylabel('Mean Optical Power (W)', color='r')
        ax1_twin.tick_params(axis='y', labelcolor='r')

        # single legend
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc='lower right')

        ax1.set_title(f'{self.anal_label} - Time Series')
        ax1.grid(True, alpha=0.3)


        # Middle plot: L vs time (2/6 height)\n        
        ax2 = plt.subplot2grid((6, 1), (3, 0), rowspan=2)
        ax2.scatter(self.df['datetime'], self.df['L'], c='m', label=self.anal_label, marker='.', s=10)
        ax2.set_ylabel(self.laser_label, color='m')
        ax2.tick_params(axis='y', labelcolor='m')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3)
        
        # Bottom plot: Temperature and RH vs time (1/6 height)
        ax3 = plt.subplot2grid((6, 1), (5, 0))
        ax3_twin = ax3.twinx()
        
        ax3.plot(self.df['datetime'], self.df['Temp'], c='g', label='Temperature', markersize=5, linewidth=1)
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
        plt.savefig(fig_path)
        plt.close(fig)
        self.add_plot_path(fig_id, fig_path)    