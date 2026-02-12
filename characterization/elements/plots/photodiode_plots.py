"""Photodiode plots"""

from typing import TYPE_CHECKING
from matplotlib import pyplot as plt

from characterization.helpers import get_logger
from characterization.config import config
from .plot_base import BasePlots

if TYPE_CHECKING:
    from ..photodiode import Photodiode

logger = get_logger()

class PhotodiodePlots(BasePlots):
    def __init__(self, photodiode: 'Photodiode'):
        super().__init__()
        self._data_holder: Photodiode = photodiode

    @property
    def output_path(self) -> str:
        return self._data_holder.output_path if self._data_holder.output_path else '.'

    def generate_plots(self):
        self._gen_timeseries_plot()
        self._gen_refpd_pedestals_timeseries(include_temp=False)
        self._gen_refpd_pedestals_timeseries(include_temp=True)
        self._gen_refpd_pedestals_histogram()
        if config.generate_file_plots:
            fileplots = self.plots.setdefault('files', {})
            for cf in self._data_holder.files:
                cf.plotter.generate_plots()
                fileplots[cf.level_header] = cf.plotter.plots

        fileset_plots = self.plots.setdefault('filesets', {})
        for key, fs in self._data_holder.filesets.items():
            fs.generate_plots()
            fileset_plots[key] = fs.plotter.plots

    def _gen_refpd_pedestals_timeseries(self, include_temp: bool = False):
        df = self._data_holder.df_pedestals
        if df is None or df.empty:
            logger.warning("No pedestal data available for photodiode ref_pd timeseries plot.")
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

        ax.set_title("photodiode ref PD pedestals")
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
            logger.warning("No pedestal data available for photodiode ref_pd histogram plot.")
            return

        fig_id = "refpd_pedestals_histogram"
        fig, ax = plt.subplots(figsize=(10, 6))

        y = df['ref_pd_mean']
        mean = float(y.mean())
        std = float(y.std())
        ax.axvspan(mean - std, mean + std, color="#2A9D8F", alpha=0.15, label="mean ± std", zorder=0)
        ax.axvline(mean, color="#2A9D8F", linestyle="--", linewidth=1.5, label="mean", zorder=0.5)
        ax.hist(y, bins=40, color="#6A4C93", alpha=0.7, label="RefPD pedestals", zorder=2)

        ax.set_title("photodiode ref PD pedestals histogram")
        ax.set_xlabel("RefPD (V)")
        ax.set_ylabel("Count")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')

        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
