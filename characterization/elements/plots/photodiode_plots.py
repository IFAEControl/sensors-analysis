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

        self._draw_confidence_band(ax, mean, std, metric="ref_pd_mean", orientation="h")
        ax.errorbar(x, y, yerr=df['ref_pd_std'], color=self._c("ref_pd_mean"), fmt=self._m("ref_pd_mean"), markersize=5, linewidth=1, label='RefPD pedestals', zorder=20)

        ax.set_title("photodiode ref PD pedestals")
        ax.set_ylabel("RefPD (V)", color=self._c("ref_pd_mean"))
        ax.set_xlabel("Time" if 'datetime' in df.columns else "Index")
        ax.tick_params(axis='y', labelcolor=self._c("ref_pd_mean"))
        ax.grid(True)

        if include_temp and 'temperature' in df.columns:
            ax_temp = ax.twinx()
            ax_temp.plot(x, df['temperature'], color=self._c("temperature"), marker=self._m("temperature"), linestyle=self._ls("temperature"), linewidth=1.2, label='Temperature')
            ax_temp.set_ylabel("Temperature (°C)", color=self._c("temperature"))
            ax_temp.tick_params(axis='y', labelcolor=self._c("temperature"))
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
        self._draw_confidence_band(ax, mean, std, metric="ref_pd_mean", orientation="v")
        ax.hist(y, bins=40, color=self._c("ref_pd_mean"), label="RefPD pedestals", zorder=2)

        ax.set_title("photodiode ref PD pedestals histogram")
        ax.set_xlabel("RefPD (V)", color=self._c("ref_pd_mean"))
        ax.set_ylabel("Count")
        ax.tick_params(axis='x', labelcolor=self._c("ref_pd_mean"))
        ax.grid(True)
        ax.legend(loc='best')

        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
