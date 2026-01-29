import os

from typing import TYPE_CHECKING

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import linregress

from calibration.helpers import get_logger
from calibration.config import config
from .plot_base import BasePlots
from ..helpers import CalibLinReg

if TYPE_CHECKING:
    from ..calibration import Calibration
    from ..calib_file import CalibFile
    from ..calib_fileset import FileSet

logger = get_logger()

class FileSetPlots(BasePlots):
    """Class to do the plots for a set of calibration files."""

    def __init__(self, file_set: FileSet):
        super().__init__()
        self._data_holder: FileSet = file_set
        # analysis results holder
        self._anal = file_set.anal

    @property
    def level_label(self):
        return self._data_holder.level_header

    @property
    def laser_label(self):
        return self._data_holder.files[0].laser_label if self._data_holder.files else "Unknown"

    @property
    def output_path(self):
        """Output path for the file set analysis."""
        return self._data_holder.output_path
    
    def generate_plots(self):
        if not self._anal.analyzed:
            logger.warning("FileSetPlot: FileSet %s not analyzed yet. Can't generate plots.", self.level_label)
            return
        fileplots = self.plots.setdefault('files', {})
        for calfile in self._data_holder.files:
            calfile.plotter.generate_plots()
            fileplots[calfile.level_header] = calfile.plotter.plots

        
        self._gen_temp_humidity_hists_plot()
        self._gen_timeseries_plot()

        self._gen_plot_conv_factor_slope_method_comparison()
        self._gen_plot_conv_factor_intercept_method_comparison()
        self._gen_plot_slopes_vs_temperature()
        self._gen_plot_slopes_intercepts_vs_index()
        self._gen_plot_pmvsRefPD()
        self._gen_plot_pmvsRefPD_all_calfiles()
        self._gen_plots_vs_laser_setting()
        self._gen_pedestals_hist_plot()
        self._gen_mean_pedestals_plot()
        self._gen_pedestals_timeseries_plot()
        logger.info("Plots for dataset %s generated", self.level_label)

    # Anal results
        # self.slopes = []
        # self.slopes_std = []
        # self.intercepts = []
        # self.intercepts_std = []
        # self.mean_temp = []
        # self.mean_rh = []
        
        # self.lr_mean: MeanStats | None = None
        # self.lr_refpd_vs_pm: CalibLinReg | None = None

    def _gen_plot_conv_factor_slope_method_comparison(self):
        # Comparison of the three methods to obtain the conversion factor slope (uW[W]/V)
        nfiles = len(self._data_holder.files)
        res = self._anal.lr_refpd_vs_pm

        fig_id = "ConvFactorSlopes_Comparison"

        fig, (ax1, ax2, ax3) = plt.subplots(
            nrows=3, ncols=1, figsize=(10, 9), sharex=True, constrained_layout=True
        )

        x = list(range(len(self._anal.slopes)))

        # Common formatting + errorbars on every axis
        for ax in (ax1, ax2, ax3):
            ax.errorbar(
                x, self._anal.slopes, yerr=self._anal.slopes_std,
                fmt='.', markersize=10, linewidth=1,
                label='run linear regression slope'
            )
            ax.grid(True, alpha=0.3)
            ax.set_xlim([-1, nfiles])

        # ─────────────────────────────
        # 1) Full dataset linreg
        # ─────────────────────────────
        ax1.axhline(y=res.slope, color='red', linestyle='--', label='Full dataset linreg')
        ax1.fill_between(
            range(-1, nfiles + 1),
            (res.slope - res.stderr),
            (res.slope + res.stderr),
            color='red', alpha=0.3
        )
        ax1.set_ylabel(f'Conv Factor Slope ({self.power_units}/V)')
        ax1.legend()

        # ─────────────────────────────
        # 2) Mean of slopes
        # ─────────────────────────────
        mean_slope = self._anal.lr_slopes_mean.mean
        std_slope = self._anal.lr_slopes_mean.std

        ax2.axhline(y=mean_slope, color='purple', linestyle='--', label='Mean of slopes')
        ax2.fill_between(
            range(-1, nfiles + 1),
            (mean_slope - std_slope),
            (mean_slope + std_slope),
            color='purple', alpha=0.2
        )
        ax2.set_ylabel(f'Conv Factor Slope ({self.power_units}/V)')
        ax2.legend()

        # ─────────────────────────────
        # 3) Weighted mean of slopes
        # ─────────────────────────────
        w_mean = self._anal.lr_slopes_mean.w_mean
        w_stderr = self._anal.lr_slopes_mean.w_stderr
        ax3.axhline(y=w_mean, color='cyan', linestyle='--', label='Weighted mean of slopes')
        ax3.fill_between(
            range(-1, nfiles + 1),
            (w_mean - w_stderr),
            (w_mean + w_stderr),
            color='cyan', alpha=0.2
        )
        ax3.set_ylabel(f'Conv Factor Slope ({self.power_units}/V)')
        ax3.legend()

        # X-axis only on bottom subplot
        ax3.set_xlabel('Run Index')
        ax3.set_xticks(range(len(self._data_holder.files)))  # run index labels

        # Title on the figure
        fig.suptitle(f'Conv Factor Slope Comparison for {self.level_label}', y=1.02)

        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_plot_conv_factor_intercept_method_comparison(self):
        # Comparison of the two methods to obtain the conversion factor intercept 
        nfiles = len(self._data_holder.files)
        res = self._anal.lr_refpd_vs_pm

        fig_id = "ConvFactorIntercepts_Comparison"

        fig, (ax1, ax2, ax3) = plt.subplots(
            nrows=3, ncols=1, figsize=(10, 9), sharex=True, constrained_layout=True
        )

        x = list(range(len(self._anal.intercepts)))

        # Common formatting + errorbars on every axis
        for ax in (ax1, ax2, ax3):
            ax.errorbar(
                x, self._anal.intercepts, yerr=self._anal.intercepts_std,
                fmt='.', markersize=10, linewidth=1,
                label='run linear regression intercept'
            )
            ax.grid(True, alpha=0.3)
            ax.set_xlim([-1, nfiles])

        # ─────────────────────────────
        # 1) Full dataset linreg
        # ─────────────────────────────
        
        ax1.axhline(y=res.intercept, color='red', linestyle='--', label='full dataset linreg')
        ax1.fill_between(
            range(-1, nfiles + 1),
            (res.intercept - res.intercept_stderr),
            (res.intercept + res.intercept_stderr),
            color='red', alpha=0.3
        )
        ax1.set_ylabel(f'Conv Factor Intercept ({self.power_units})')
        ax1.legend()

        # ─────────────────────────────
        # 2) Mean of intercepts
        # ─────────────────────────────
        
        mean_intercepts = self._anal.lr_intercepts_mean.mean
        std_intercepts = self._anal.lr_intercepts_mean.std

        ax2.axhline(y=mean_intercepts, color='purple', linestyle='--', label='Mean of intercepts')
        ax2.fill_between(
            range(-1, nfiles + 1),
            (mean_intercepts - std_intercepts),
            (mean_intercepts + std_intercepts),
            color='purple', alpha=0.2
        )
        ax2.set_ylabel(f'Conv Factor Intercept ({self.power_units})')
        ax2.legend()

        # ─────────────────────────────
        # 3) Weighted mean of intercepts
        # ─────────────────────────────
        w_mean = self._anal.lr_intercepts_mean.w_mean
        w_stderr = self._anal.lr_intercepts_mean.w_stderr
        ax3.axhline(y=w_mean, color='cyan', linestyle='--', label='Weighted mean of intercepts')
        ax3.fill_between(
            range(-1, nfiles + 1),
            (w_mean - w_stderr),
            (w_mean + w_stderr),
            color='cyan', alpha=0.2
        )
        ax3.set_ylabel(f'Conv Factor Intercept ({self.power_units})')
        ax3.legend()

        # X-axis only on bottom subplot
        ax3.set_xlabel('Run Index')
        ax3.set_xticks(range(len(self._data_holder.files)))  # run index labels

        # Title on the figure
        fig.suptitle(f'Conv Factor Intercept Comparison for {self.level_label}', y=1.02)

        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_plot_slopes_vs_temperature(self):
        # Plot dels slopes per la pm en funció de la temperatura mitja de cada fitxer, no cal fer regressió lineal perque
        # totes han de tenir el mateix valor.
        fig_id = 'pmVsRefPD_fitSlope_vs_Temperature'
        fig = plt.figure(figsize=(10, 6))
        plt.grid()
        plt.errorbar(self._anal.mean_temp, self._anal.slopes,yerr=self._anal.slopes_std,
                     fmt='.', markersize=10, linewidth=1)
        plt.axhline(y=self._anal.lr_slopes_mean.mean, color='r', linestyle='-',
                    label=f'mean slope value={self._anal.lr_slopes_mean.mean:.3e}')
        plt.legend()
        plt.ylabel('ref PD vs pm slopes')
        plt.xlabel('Mean temperature (Cº)')
        plt.title(f'{self.level_label} - {self.power_units}/V fit slopes')
        plt.tight_layout(rect=(0, 0, 1, 0.98))
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_plot_slopes_intercepts_vs_index(self):
        # Plot dels slopes i intercepts per la pm en funció de l'índex del fitxer, no cal fer regressió lineal perque
        # totes han de tenir el mateix valor.

        fig_id = 'pmVsRefPD_fitSlopes_and_Intercepts_vs_Run'
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), sharex=True)

        # Slopes
        w_mean = self._anal.lr_slopes_mean.w_mean
        w_stderr = self._anal.lr_slopes_mean.w_stderr
        ax1.grid(True)
        ax1.errorbar(
            range(len(self._anal.slopes)),
            self._anal.slopes,
            yerr=self._anal.slopes_std,
            fmt='.', markersize=10, linewidth=1,
            label='Slopes'
        )
        ax1.axhline(
            y=w_mean,
            color='r', linestyle='-',
            label=f'mean slope = {w_mean:.3e}'
        )
        ax1.fill_between(
            range(-1, len(self._anal.slopes)+1),
            (w_mean - w_stderr),
            (w_mean + w_stderr),
            color='r', alpha=0.2
        )
        ax1.set_xlabel('File index in set')
        ax1.set_ylabel(f'Slope ({self.power_units}/V)')
        ax1.set_title('Fit slopes')
        ax1.legend()

        # Intercepts
        ax2.grid(True)
        ax2.errorbar(
            range(len(self._anal.intercepts)),
            self._anal.intercepts,
            yerr=self._anal.intercepts_std,
            fmt='.', markersize=10, linewidth=1,
            label='Intercepts'
        )
        w_mean = self._anal.lr_intercepts_mean.w_mean
        w_stderr = self._anal.lr_intercepts_mean.w_stderr
        ax2.axhline(
            y=w_mean,
            color='g', linestyle='-',
            label=f'mean intercept = {w_mean:.3e}'
        )
        ax2.fill_between(
            range(-1, len(self._anal.intercepts)+1),
            (w_mean - w_stderr),
            (w_mean + w_stderr),
            color='r', alpha=0.2
        )
        ax2.set_xlabel('Run number in set')
        ax2.set_ylabel(f'Intercept ({self.power_units})')
        ax2.set_title('Fit intercepts')
        ax2.legend()

        # force integer ticks on x-axis
        # ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
        # ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.set_xticks(range(len(self._anal.slopes)))
        ax2.set_xticks(range(len(self._anal.intercepts)))
        ax1.set_xlim([-1, len(self._anal.slopes)])
        ax2.set_xlim([-1, len(self._anal.intercepts)])

        fig.suptitle(f'{self.level_label} - {self.power_units}/V fit slopes and intercepts')
        plt.tight_layout(rect=(0, 0, 1, 0.98))
        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_plot_pmvsRefPD_all_calfiles(self):

        fig_id = "pm_vs_RefPD_runs"

        n_files = len(self._data_holder.files)

        fig = plt.figure(
            figsize=(12, 7),
            constrained_layout=True
        )

        gs = GridSpec(
            nrows=4, ncols=n_files,
            height_ratios=[3, 3, 3, 1],
            figure=fig
        )

        # Store colors per file
        colors = {}

        # ─────────────────────────────
        # Top plot (main)
        # ─────────────────────────────
        ax_top = fig.add_subplot(gs[0:3, :])
        ax_top.grid(True, alpha=0.4)

        for calfile in self._data_holder.files:
            intercept = calfile.anal.lr_refpd_vs_pm.intercept
            slope = calfile.anal.lr_refpd_vs_pm.slope

            # Errorbar → grab color
            eb = ax_top.errorbar(
                calfile._df[self.refpd_col],
                calfile._df[self.pm_col],
                yerr=calfile._df[self.pm_std_col],
                fmt='.', markersize=8, linewidth=1,
                label=calfile.file_label
            )

            color = eb[0].get_color()
            colors[calfile.file_label] = color

            ax_top.plot(
                calfile._df[self.refpd_col],
                intercept + slope * calfile._df[self.refpd_col],
                linewidth=1,
                color=color,
                label=f'{calfile.file_info["run"]}: '
                    f'int={intercept:.2e}, slope={slope:.2e}'
            )

        ax_top.set_ylabel(f'Power meter ({self.power_units})')
        ax_top.set_xlabel('ref PD (V)')
        ax_top.set_title(f'{self.level_label} - pm vs RefPD')

        ax_top.legend(
            fontsize=8,
            ncol=2,
            frameon=False,
            handlelength=2
        )

        # ─────────────────────────────
        # Bottom row (diagnostic plots)
        # ─────────────────────────────
        for i, calfile in enumerate(self._data_holder.files):
            ax = fig.add_subplot(gs[3, i], sharex=ax_top, sharey=ax_top)
            ax.grid(True, alpha=0.3)

            color = colors[calfile.file_label]

            ax.errorbar(
                calfile._df[self.refpd_col],
                calfile._df[self.pm_col],
                yerr=calfile._df[self.pm_std_col],
                fmt='.', markersize=4, linewidth=0.8,
                color=color
            )

            ax.set_title(calfile.file_label, fontsize=8, pad=2)
            ax.tick_params(labelsize=7)

            if i != 0:
                ax.set_ylabel('')
                ax.tick_params(labelleft=False)

            ax.set_xlabel('')

        fig.supxlabel('ref PD (V)', fontsize=10)

        # fig.subplots_adjust(
        #     left=0.06,
        #     right=0.995,
        #     top=0.93,
        #     bottom=0.08
        # )

        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_plot_pmvsRefPD(self):

        fig_id = "pm_vs_RefPD"

        n_files = len(self._data_holder.files)

        fig = plt.figure(
            figsize=(12, 7),
            constrained_layout=True
        )

        gs = GridSpec(
            nrows=4, ncols=n_files,
            height_ratios=[3, 3, 3, 1],
            figure=fig
        )

        # Store colors per file
        colors = {}

        # ─────────────────────────────
        # Top plot (main)
        # ─────────────────────────────
        ax_top = fig.add_subplot(gs[0:3, :])
        ax_top.grid(True, alpha=0.4)

        for calfile in self._data_holder.files:
            intercept = calfile.anal.lr_refpd_vs_pm.intercept
            slope = calfile.anal.lr_refpd_vs_pm.slope

            # Errorbar → grab color
            eb = ax_top.errorbar(
                calfile._df[self.refpd_col],
                calfile._df[self.pm_col],
                yerr=calfile._df[self.pm_std_col],
                fmt='x', markersize=4, linewidth=1,
                label=calfile.file_label
            )

            color = eb[0].get_color()
            colors[calfile.file_label] = color

        intercept = self.dh.anal.lr_refpd_vs_pm.intercept
        slope = self.dh.anal.lr_refpd_vs_pm.slope
        x = np.array(ax_top.get_xlim())
        ax_top.plot(
            x,
            intercept + slope * x,
            linewidth=1,
            label=f'{self.dh.level_header}: '
                f'int={intercept:.2e}, slope={slope:.2e}'
        )

        ax_top.set_ylabel(f'Power meter ({self.power_units})')
        ax_top.set_xlabel('ref PD (V)')
        ax_top.set_title(f'{self.level_label} - pm vs RefPD')

        ax_top.legend(
            fontsize=8,
            ncol=2,
            frameon=False,
            handlelength=2
        )

        # ─────────────────────────────
        # Bottom row (diagnostic plots)
        # ─────────────────────────────
        for i, calfile in enumerate(self._data_holder.files):
            ax = fig.add_subplot(gs[3, i], sharex=ax_top, sharey=ax_top)
            ax.grid(True, alpha=0.3)

            color = colors[calfile.file_label]

            ax.errorbar(
                calfile._df[self.refpd_col],
                calfile._df[self.pm_col],
                yerr=calfile._df[self.pm_std_col],
                fmt='.', markersize=4, linewidth=0.8,
                color=color
            )

            ax.set_title(calfile.file_label, fontsize=8, pad=2)
            ax.tick_params(labelsize=7)

            if i != 0:
                ax.set_ylabel('')
                ax.tick_params(labelleft=False)

            ax.set_xlabel('')

        fig.supxlabel('ref PD (V)', fontsize=10)

        # fig.subplots_adjust(
        #     left=0.06,
        #     right=0.995,
        #     top=0.93,
        #     bottom=0.08
        # )

        self.savefig(fig, fig_id)
        plt.close(fig)
    
    def _gen_plots_vs_laser_setting(self):
        """Generate plots vs laser setting for the set of calibration files"""
        fig_id = "pm_vs_LaserSetting"
        fig = plt.figure(figsize=(10, 6))
        plt.grid()
        for calfile in self._data_holder.files:
            plt.errorbar(calfile.df['laser_setpoint'], calfile.df[self.pm_col], yerr=calfile.df[self.pm_std_col],
                         fmt='.', markersize=10, linewidth=1, label=calfile.file_label)
        plt.ylabel(f'Power meter ({self.power_units})')
        plt.xlabel(self.laser_label)
        plt.title(f'{self.level_label} - pm vs Laser setting')
        plt.legend()
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        self.savefig(fig, fig_id)
        plt.close(fig)

        fig_id = "RefPD_vs_LaserSetting"
        fig = plt.figure(figsize=(10, 6))
        plt.grid()
        for calfile in self._data_holder.files:
            plt.errorbar(calfile.df['laser_setpoint'], calfile.df[self.refpd_col], yerr=calfile.df[self.refpd_std_col],
                         fmt='.', markersize=10, linewidth=1, label=calfile.file_label)
        plt.ylabel('ref PD (V)')
        plt.xlabel(self.laser_label)
        plt.title(f'{self.level_label} - RefPD vs Laser setting')
        plt.legend()
        plt.tight_layout(rect=(0, 0, 1, 0.98))
        self.savefig(fig, fig_id)
        plt.close(fig)
    
    def _gen_pedestals_hist_plot(self):
        """Generate histogram plot of pedestal values for the set of calibration files"""
        fig_id = "Pedestals_Histogram"

        fig, (ax1, ax2) = plt.subplots(
            nrows=1, ncols=2, figsize=(12, 6), sharey=True
        )

        # Concatenate pedestal data
        # Pedestals do not use zeroed data
        df_pm_ped = pd.concat(
            [calfile.df_pedestals['pm_mean'] for calfile in self._data_holder.files]
        )
        df_refpd_ped = pd.concat(
            [calfile.df_pedestals['ref_pd_mean'] for calfile in self._data_holder.files]
        )

        # ─────────────────────────────
        # Left plot: pm pedestals
        # ─────────────────────────────
        ax1.grid(True, alpha=0.3)
        ax1.hist(
            df_pm_ped,
            color='violet',
            alpha=0.7,
            label='pm Pedestals'
        )
        ax1.set_xlabel(f'Pedestal Mean pm ({self.power_units})')
        ax1.set_ylabel('Frequency')
        ax1.set_title('pm pedestals')
        ax1.legend()

        # ─────────────────────────────
        # Right plot: RefPD pedestals
        # ─────────────────────────────
        ax2.grid(True, alpha=0.3)
        ax2.hist(
            df_refpd_ped,
            color='orange',
            alpha=0.7,
            label='RefPD Pedestals'
        )
        ax2.set_xlabel('Pedestal Mean RefPD (V)')
        ax2.set_title('RefPD pedestals')
        ax2.legend()

        # ─────────────────────────────
        fig.suptitle(f'{self.level_label} - Histogram of pedestal values', fontsize=14)
        plt.tight_layout(rect=(0, 0, 1, 0.98))
        self.savefig(fig, fig_id)
        plt.close(fig)
    
    def _gen_mean_pedestals_plot(self):
        """Generate pedestal plot for the set of calibration files"""
        fig_id = "Pedestals_vs_runindex"

        fig, (ax1, ax2) = plt.subplots(
            nrows=2, ncols=1,
            figsize=(10, 6),
            sharex=True,
            constrained_layout=True
        )

        x = range(len(self.df_pedestals))

        # ─────────────────────────────
        # Top plot: pm pedestals
        # ─────────────────────────────
        # pedestals do not use zeroed data
        ax1.errorbar(
            x, self.df_pedestals['pm_mean'], yerr=self.df_pedestals['pm_std'],
            fmt='.', markersize=10, linewidth=1,
            label='PM Pedestals'
        )

        mean = self._anal.pedestal_stats.pm.mean
        std = self._anal.pedestal_stats.pm.std
        samples = self._anal.pedestal_stats.pm.samples
        ax1.axhline(y=mean, color='orange', linestyle='--', label='PM mean of Pedestal')
        ax1.fill_between(range(-1, samples+1), mean-std, mean+std, color='orange', alpha=0.3, label='pm mean +/- std')
        ax1.set_ylabel(f'Pedestals PM ({self.power_units})')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # ─────────────────────────────
        # Bottom plot: RefPD pedestals
        # ─────────────────────────────
        ax2.errorbar(
            x, self.df_pedestals['ref_pd_mean'], yerr=self.df_pedestals['ref_pd_std'],
            fmt='.', markersize=10, linewidth=1,
            label='RefPD Pedestals'
        )
        mean = self._anal.pedestal_stats.refpd.mean
        std = self._anal.pedestal_stats.refpd.std
        samples = self._anal.pedestal_stats.refpd.samples
        ax2.axhline(y=mean, color='purple', linestyle='--', label='RefPD Mean of Pedestals')
        ax2.fill_between(range(-1, samples+1), mean-std, mean+std, color='red', alpha=0.3, label='RefPD mean +/- std')
        ax2.set_ylabel('Pedestals RefPD (V)')
        ax2.set_xlabel('Run index')
        ax2.set_xticks(range(len(self._data_holder.files)))
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-1, len(self._data_holder.files)])
        ax2.legend()

        self.savefig(fig, fig_id)
        plt.close(fig)

    def _gen_pedestals_timeseries_plot(self):
        """Generate pedestal plot for the set of calibration files"""
        fig_id = "Pedestals_timeseries"

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
