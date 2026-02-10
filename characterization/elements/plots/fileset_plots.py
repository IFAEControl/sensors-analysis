"""Fileset plots (same analysis as per file, but on concatenated data)."""

from typing import TYPE_CHECKING
import numpy as np
import matplotlib.pyplot as plt

from characterization.helpers import get_logger
from .plot_base import BasePlots

if TYPE_CHECKING:
    from ..fileset import Fileset

logger = get_logger()


class FilesetPlots(BasePlots):
    def __init__(self, fileset: 'Fileset'):
        super().__init__()
        self._data_holder: Fileset = fileset
        self.fs = fileset

    @property
    def laser_label(self) -> str:
        if self.fs.wavelength == '532':
            return '532nm laser setpoint (mA)'
        if self.fs.wavelength == '1064':
            return '1064nm laser setpoint (mW)'
        return 'Laser Parameter'

    @property
    def output_path(self) -> str:
        return self.fs.output_path if self.fs.output_path else '.'

    def generate_plots(self):
        df = self.fs.df
        if df is None or df.empty:
            logger.error("No analysis dataframe for fileset: %s", self.fs.label)
            return
        self._gen_timeseries_plot()
        self._gen_fit_slopes_intercepts_vs_run()
        self._gen_saturation_points_vs_run()
        self._gen_refpd_vs_laser_setpoint()
        self._gen_refpd_vs_dut()

        fig_id = "dut_vs_laser_setpoint"
        fig = plt.figure(figsize=(10, 6))
        colors = plt.cm.tab20.colors
        for idx, sweep in enumerate(self.fs.files):
            df_full = sweep.df_full
            color = colors[idx % len(colors)]
            label = f"run{sweep.run}"
            plt.errorbar(df_full['laser_setpoint'], df_full['mean_adc'], yerr=df_full['std_adc'],
                         fmt='.', markersize=6, linewidth=1, color=color, label=label)
        plt.ylabel(f'{self._pd_label()} (ADC counts)')
        plt.xlabel(self.laser_label)
        plt.grid()
        plt.title(f'{self.level_label} - DUT vs {self.laser_label}')
        plt.legend(loc='best', ncol=2, fontsize=8)
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_saturation_points_vs_run(self):
        fig_id = "saturation_points_vs_run"
        runs = []
        sat_counts = []

        for sweep in self.fs.files:
            runs.append(int(sweep.run))
            sat_counts.append(int(sweep.df_sat.shape[0]))

        if not runs:
            logger.warning("No runs for saturation plot in fileset %s", self.fs.label)
            return

        order = sorted(range(len(runs)), key=lambda i: runs[i])
        runs = [runs[i] for i in order]
        sat_counts = [sat_counts[i] for i in order]

        fig = plt.figure(figsize=(8, 4))
        plt.bar(runs, sat_counts, color="#0E6157", label='saturated points')
        plt.xlabel('Run number in set')
        plt.ylabel('Saturated points')
        plt.xticks(runs)
        plt.xlim([0.5, max(runs) + 0.5])
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_refpd_vs_laser_setpoint(self):
        fig_id = "refpd_vs_laser_setpoint"
        fig = plt.figure(figsize=(10, 6))
        colors = plt.cm.tab20.colors
        for idx, sweep in enumerate(self.fs.files):
            df_full = sweep.df_full
            color = colors[idx % len(colors)]
            label = f"run{sweep.run}"
            plt.errorbar(df_full['laser_setpoint'], df_full['ref_pd_mean'], yerr=df_full['ref_pd_std'],
                         fmt='.', markersize=6, linewidth=1, color=color, label=label)
        plt.ylabel('RefPD (V)')
        plt.xlabel(self.laser_label)
        plt.grid()
        plt.title(f'{self.level_label} - RefPD vs {self.laser_label}')
        plt.legend(loc='best', ncol=2, fontsize=8)
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_refpd_vs_dut(self):
        fig_id = "refpd_vs_dut"
        fig = plt.figure(figsize=(10, 6))
        colors = plt.cm.tab20.colors
        for idx, sweep in enumerate(self.fs.files):
            df_full = sweep.df_full
            color = colors[idx % len(colors)]
            label = f"run{sweep.run}"
            plt.errorbar(df_full['mean_adc'], df_full['ref_pd_mean'], yerr=df_full['ref_pd_std'],
                         fmt='.', markersize=6, linewidth=1, color=color, label=label)
        plt.axvspan(0, 4095, color='green', alpha=0.08, label='linear region')
        plt.axvspan(4095, 4300, color='magenta', alpha=0.08, label='saturation')
        if self.fs.anal.lr_refpd_vs_adc.linreg is not None:
            intercept = self.fs.anal.lr_refpd_vs_adc.intercept
            slope = self.fs.anal.lr_refpd_vs_adc.slope
            xline = np.linspace(0, 4095, 200)
            fit_label = f"fit: y={slope:.2e}x+{intercept:.2e}"
            plt.plot(xline, intercept + slope * xline, color='black', linewidth=2, label=fit_label)
        plt.ylabel('RefPD (V)')
        plt.xlabel(f'{self._pd_label()} (ADC counts)')
        plt.grid()
        plt.xlim(-50, 4200)
        plt.title(f'{self.level_label} - Ref PD vs DUT')
        plt.legend(loc='best', ncol=2, fontsize=8)
        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_fit_slopes_intercepts_vs_run(self):
        self._gen_fit_slopes_intercepts_vs_run_plot(orientation='vertical')
        self._gen_fit_slopes_intercepts_vs_run_plot(orientation='horizontal')

    def _gen_fit_slopes_intercepts_vs_run_plot(self, orientation: str = 'vertical'):
        fig_id = "fit_slopes_intercepts_vs_run" + ("_vert" if orientation == 'vertical' else "_horiz")

        runs = []
        slopes = []
        slopes_stderr = []
        intercepts = []
        intercepts_stderr = []

        for sweep in self.fs.files:
            lr = sweep.anal.lr_refpd_vs_adc
            if lr.linreg is None:
                continue
            runs.append(int(sweep.run))
            slopes.append(lr.slope)
            slopes_stderr.append(lr.stderr)
            intercepts.append(lr.intercept)
            intercepts_stderr.append(lr.intercept_stderr)

        if not runs:
            logger.warning("No per-run linreg data for fileset %s", self.fs.label)
            return

        order = sorted(range(len(runs)), key=lambda i: runs[i])
        runs = [runs[i] for i in order]
        slopes = [slopes[i] for i in order]
        slopes_stderr = [slopes_stderr[i] for i in order]
        intercepts = [intercepts[i] for i in order]
        intercepts_stderr = [intercepts_stderr[i] for i in order]

        if orientation == 'vertical':
            fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(8, 10), sharex=True)
        else:
            fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), sharex=True)

        # Slopes
        ax1.errorbar(runs, slopes, yerr=slopes_stderr, fmt='.', markersize=8, linewidth=1, label='Slopes')
        if self.fs.anal.lr_refpd_vs_adc.linreg is not None:
            m = self.fs.anal.lr_refpd_vs_adc.slope
            m_err = self.fs.anal.lr_refpd_vs_adc.stderr
            ax1.axhline(y=m, color='b', linestyle='--', label=f'slope = {m:.3e}')
            ax1.fill_between([min(runs) - 1, max(runs) + 1], m - m_err, m + m_err, color='b', alpha=0.2, label='slope ± std')
        ax1.set_xlabel('Run number in set')
        ax1.set_ylabel('Slope (V/adc count)')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best')

        # Intercepts
        ax2.errorbar(runs, intercepts, yerr=intercepts_stderr, fmt='.', markersize=8, linewidth=1, label='Intercepts')
        if self.fs.anal.lr_refpd_vs_adc.linreg is not None:
            b = self.fs.anal.lr_refpd_vs_adc.intercept
            b_err = self.fs.anal.lr_refpd_vs_adc.intercept_stderr
            ax2.axhline(y=b, color='m', linestyle='--', label=f'intercept = {b:.3e}')
            ax2.fill_between([min(runs) - 1, max(runs) + 1], b - b_err, b + b_err, color='m', alpha=0.2, label='intercept ± std')
        ax2.set_xlabel('Run number in set')
        ax2.set_ylabel('Intercept (V)')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')

        ax1.set_xticks(runs)
        ax2.set_xticks(runs)
        ax1.set_xlim([0.5, max(runs) + 0.5])
        ax2.set_xlim([0.5, max(runs) + 0.5])

        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useOffset=False)
        ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useOffset=False)

        fig.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
