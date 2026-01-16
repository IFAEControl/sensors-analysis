import os

from typing import TYPE_CHECKING

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import linregress

from calibration.helpers import get_logger
from .base_anal import BaseAnal
from .data_holders import CalibLinReg

if TYPE_CHECKING:
    from .calibration import Calibration
    from .calib_file import CalibFile

logger = get_logger()


class FileSet:
    """Class to represent a set of calibration files with the same wavelength and filter wheel"""

    def __init__(self, wave_length: str, filter_wheel: str, calibration: Calibration | None = None):
        self.wl = wave_length
        self.fw = filter_wheel
        self.cal = calibration
        self.files: list['CalibFile'] = []
        self.anal = FileSetAnalysis(self)
        self.output_path = os.path.join(
            calibration.output_path,
            f"{self.wl}_{self.fw}"
        )
        self._concat_df: pd.DataFrame | None = None
        self._concat_ped_df: pd.DataFrame | None = None

    @property
    def concat_df(self):
        """Concatenated DataFrame of all calibration files in the set."""
        if self._concat_df is None:
            self._concat_df = pd.concat(
                [calfile.df for calfile in self.files if calfile.df is not None], ignore_index=True)
        return self._concat_df

    @property
    def concat_pedestal_df(self):
        """Concatenated DataFrame of all calibration files in the set."""
        if self._concat_ped_df is None:
            self._concat_ped_df = pd.concat(
                [calfile.df_pedestal for calfile in self.files if calfile.df_pedestal is not None], ignore_index=True)
        return self._concat_ped_df

    def add_calib_file(self, calib_file: 'CalibFile'):
        """Add a calibration file to the set."""
        if calib_file.wavelength != self.wl or calib_file.filter_wheel != self.fw:
            logger.error(
                "Calibration file wavelength or filter wheel does not match the set.")
            return
        self.files.append(calib_file)
        calib_file.set_file_set(self)

    def analyze(self):
        """Analyze the set of calibration files."""
        os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()

    def to_dict(self):
        """Convert file set data to dictionary."""
        return {
            'wave_length': self.wl,
            'filter_wheel': self.fw,
            'analysis': self.anal.to_dict(),
            'files': {cf.meta['filename']: cf.to_dict() for cf in self.files}
        }


class FileSetAnalysis(BaseAnal):
    """Class to analyze a set of calibration files."""

    def __init__(self, file_set: FileSet):
        self.fs = file_set
        self.plots = {}
        self.results = {}

        self.slopes = []
        self.slopes_std = []
        self.intercepts = []
        self.intercepts_std = []
        self.mean_temp = []
        self.mean_rh = []
        self.mean_pedestal_pd = []
        self.mean_pedestal_pd_std = []
        self.mean_pedestal_pm = []
        self.mean_pedestal_pm_std = []
        self.df_concat: pd.DataFrame | None = None

        self.linreg_full_dataset_pm_vs_refpd: CalibLinReg | None = None

    @property
    def anal_label(self):
        return f"{self.fs.wl}_{self.fs.fw}"

    @property
    def laser_label(self):
        return self.fs.files[0].laser_label if self.fs.files else "Unknown"

    @property
    def df(self):
        """Concatenated DataFrame of all calibration files in the set."""
        # This has to be set like this so we can use the base class methods that use self.df
        # mostly for plotting time series
        # It will be used also to:
        #  - calculate histograms of temperature and humidity
        #  - calculate linear regressions across the set of files
        return self.fs.concat_df

    @property
    def output_path(self):
        """Output path for the file set analysis."""
        return self.fs.output_path

    def analyze(self):
        """Analyze the set of calibration files."""
        for calfile in self.fs.files:
            calfile.analyze()
            calfile.generate_plots()
            logger.info("Analyzed calibration file: %s",
                        calfile.meta['filename'])

        self.analyze_mean_of_lin_regs()
        self.analyze_weighted_mean_of_lin_regs()
        self.analyze_full_data_set()
        self.analyze_pedestals()
        self.generate_plots()
    
    def analyze_pedestals(self):
        for calfile in self.fs.files:
            self.mean_pedestal_pd.append(calfile.df_pedestal['meanRefPD'].mean())
            self.mean_pedestal_pd_std.append(calfile.df_pedestal['meanRefPD'].std())
            self.mean_pedestal_pm.append(calfile.df_pedestal['meanPM'].mean())
            self.mean_pedestal_pm_std.append(calfile.df_pedestal['meanPM'].std())
        self.mean_pedestal_pd = np.array(self.mean_pedestal_pd)
        self.mean_pedestal_pm = np.array(self.mean_pedestal_pm)

        self.results['pedestals'] = {
            'run_means': {
                'RefPD': self.mean_pedestal_pd.mean(),
                'RefPD_std': self.mean_pedestal_pd.std(),
                'PM': self.mean_pedestal_pm.mean(),
                'PM_std': self.mean_pedestal_pm.std()
            },
            'full_set':{
                'RefPD': self.fs.concat_pedestal_df['meanRefPD'].mean(),
                'PM': self.fs.concat_pedestal_df['meanPM'].mean(),
                'RefPD_std': self.fs.concat_pedestal_df['meanRefPD'].std(),
                'PM_std': self.fs.concat_pedestal_df['meanPM'].std()
            }
        }


    def analyze_full_data_set(self):
        """Analyze the full concatenated data set of the file set."""
        linreg = linregress(self.df['meanRefPD'], self.df['meanPM'])
        self.linreg_full_dataset_pm_vs_refpd = CalibLinReg(
            'meanRefPD', 'meanPM', linreg)
        self.results['full_dataset_linreg'] = self.linreg_full_dataset_pm_vs_refpd.to_dict()

    def analyze_weighted_mean_of_lin_regs(self):
        """Analyze weighted mean of linear regressions of the calibration files"""
        # has to be executed after analyze_mean_of_lin_regs
        weights = 1 / self.slopes_std**2
        weighted_mean = np.sum(weights * self.slopes) / np.sum(weights)
        weighted_mean_error = np.sqrt(1 / np.sum(weights))
        weighted_variance = np.sum(weights * (self.slopes - weighted_mean)**2) / np.sum(weights)
        weighted_std_dev = np.sqrt(weighted_variance)
        intervariability = np.std(self.slopes, ddof=1)  # Standard deviation (sample)
        combined_sigma = np.sqrt(weighted_std_dev**2+intervariability**2)

        # ToDo: oks, but what about the intercept?
        self.results['weighted_linreg_means'] = {
            'slope': weighted_mean,
            'slope_error': weighted_mean_error,
            'weighted_std_dev': weighted_std_dev,
            'intervariability': intervariability,
            'combined_sigma': combined_sigma
        }


    def analyze_mean_of_lin_regs(self):
        """Analyze linear regressions across the set of calibration files."""
        for calfile in self.fs.files:
            self.slopes.append(calfile.anal.linreg_refPD_vs_meanPM.slope)
            self.slopes_std.append(calfile.anal.linreg_refPD_vs_meanPM.stderr)
            self.intercepts.append(
                calfile.anal.linreg_refPD_vs_meanPM.intercept)
            self.intercepts_std.append(
                calfile.anal.linreg_refPD_vs_meanPM.intercept_stderr)
            self.mean_temp.append(calfile.df['Temp'].mean())
            self.mean_rh.append(calfile.df['RH'].mean())
        self.slopes = np.array(self.slopes)
        self.slopes_std = np.array(self.slopes_std)
        self.intercepts = np.array(self.intercepts)
        self.intercepts_std = np.array(self.intercepts_std)

        self.results['linreg_means'] = {
            'slope': self.slopes.mean(),
            'slope_std': self.slopes.std(),
            'intercept': self.intercepts.mean(),
            'intercept_std': self.intercepts.std(),
            'slope_dispersion': (self.slopes.max() - self.slopes.min())/self.slopes.max()*100
        }

    def _gen_plot_conv_factor_slope_method_comparison(self):
        # Comparison of the three methods to obtain the conversion factor slope (W/V)
        nfiles = len(self.fs.files)
        res = self.linreg_full_dataset_pm_vs_refpd
        weighted = self.results['weighted_linreg_means']

        fig_id = "ConvFactorSlopes_Comparison"
        opath = os.path.join(self.output_path, fig_id + '.png')

        fig, (ax1, ax2, ax3) = plt.subplots(
            nrows=3, ncols=1, figsize=(10, 9), sharex=True, constrained_layout=True
        )

        x = list(range(len(self.slopes)))

        # Common formatting + errorbars on every axis
        for ax in (ax1, ax2, ax3):
            ax.errorbar(
                x, self.slopes, yerr=self.slopes_std,
                fmt='.', markersize=10, linewidth=1,
                label='run linear regression slope'
            )
            ax.grid(True, alpha=0.3)
            ax.set_xlim([-1, nfiles])

        # ─────────────────────────────
        # 1) Full dataset linreg
        # ─────────────────────────────
        ax1.axhline(y=res.slope, color='red', linestyle='--', label='full dataset linreg')
        ax1.fill_between(
            range(-1, nfiles + 1),
            (res.slope - res.stderr),
            (res.slope + res.stderr),
            color='red', alpha=0.3
        )
        ax1.set_ylabel('Conv Factor Slope (W/V)')
        ax1.legend()

        # ─────────────────────────────
        # 2) Mean of slopes
        # ─────────────────────────────
        mean_slope = self.slopes.mean()
        std_slope = self.slopes.std()

        ax2.axhline(y=mean_slope, color='purple', linestyle='--', label='Mean of slopes')
        ax2.fill_between(
            range(-1, nfiles + 1),
            (mean_slope - std_slope),
            (mean_slope + std_slope),
            color='purple', alpha=0.2
        )
        ax2.set_ylabel('Conv Factor Slope (W/V)')
        ax2.legend()

        # ─────────────────────────────
        # 3) Weighted mean of slopes
        # ─────────────────────────────
        ax3.axhline(y=weighted['slope'], color='cyan', linestyle='--', label='Weighted mean of slopes')
        ax3.fill_between(
            range(-1, nfiles + 1),
            (weighted['slope'] - weighted['slope_error']),
            (weighted['slope'] + weighted['slope_error']),
            color='cyan', alpha=0.2
        )
        ax3.set_ylabel('Conv Factor Slope (W/V)')
        ax3.legend()

        # X-axis only on bottom subplot
        ax3.set_xlabel('Run Index')
        ax3.set_xticks(range(len(self.fs.files)))  # run index labels

        # Title on the figure
        fig.suptitle(f'Conv Factor Slope Comparison for {self.anal_label}', y=1.02)

        plt.savefig(opath, dpi=150)
        self.plots[fig_id] = opath
        plt.close(fig)

    def _gen_plot_conv_factor_intercept_method_comparison(self):
        # Comparison of the two methods to obtain the conversion factor intercept (W)
        nfiles = len(self.fs.files)
        res = self.linreg_full_dataset_pm_vs_refpd
        weighted = self.results['weighted_linreg_means']

        fig_id = "ConvFactorIntercepts_Comparison"
        opath = os.path.join(self.output_path, fig_id + '.png')

        fig, (ax1, ax2) = plt.subplots(
            nrows=2, ncols=1, figsize=(10, 9), sharex=True, constrained_layout=True
        )

        x = list(range(len(self.slopes)))

        # Common formatting + errorbars on every axis
        for ax in (ax1, ax2):
            ax.errorbar(
                x, self.intercepts, yerr=self.intercepts_std,
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
        ax1.set_ylabel('Conv Factor Intercept (W)')
        ax1.legend()

        # ─────────────────────────────
        # 2) Mean of intercepts
        # ─────────────────────────────
        mean_intercepts = self.intercepts.mean()
        std_intercepts = self.intercepts.std()

        ax2.axhline(y=mean_intercepts, color='purple', linestyle='--', label='Mean of intercepts')
        ax2.fill_between(
            range(-1, nfiles + 1),
            (mean_intercepts - std_intercepts),
            (mean_intercepts + std_intercepts),
            color='purple', alpha=0.2
        )
        ax2.set_ylabel('Conv Factor Intercept (W)')
        ax2.legend()

        # X-axis only on bottom subplot
        ax2.set_xlabel('Run Index')
        ax2.set_xticks(range(len(self.fs.files)))  # run index labels

        # Title on the figure
        fig.suptitle(f'Conv Factor Intercept Comparison for {self.anal_label}', y=1.02)

        plt.savefig(opath, dpi=150)
        plt.close(fig)
        self.plots[fig_id] = opath

    def _gen_plot_slopes_vs_temperature(self):
        # Plot dels slopes per la PM en funció de la temperatura mitja de cada fitxer, no cal fer regressió lineal perque
        # totes han de tenir el mateix valor.
        opath = os.path.join(self.output_path,
                             'PMVsRefPD_fitSlope_vs_Temperature.png')
        fig = plt.figure(figsize=(10, 6))
        plt.grid()
        plt.errorbar(self.mean_temp, self.slopes,
                     fmt='.', markersize=10, linewidth=1)
        plt.axhline(y=np.mean(self.slopes), color='r', linestyle='-',
                    label=f'mean slope value={self.slopes.mean():.3e}')
        plt.legend()
        plt.ylabel('ref PD vs PM slopes')
        plt.xlabel('Mean temperature (Cº)')
        plt.title(f'{self.anal_label} - W/V fit slopes')
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.savefig(opath)  # Display the current figure
        self.plots['W/V_slopes_vs_Temp'] = opath
        plt.close(fig)

    def _gen_plot_slopes_intercepts_vs_index(self):
        # Plot dels slopes i intercepts per la PM en funció de l'índex del fitxer, no cal fer regressió lineal perque
        # totes han de tenir el mateix valor.
        opath = os.path.join(self.output_path, 'PMVsRefPD_fitSlopes_and_Intercepts_vs_Run.png')

        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), sharex=True)

        # Slopes
        ax1.grid(True)
        ax1.errorbar(
            range(len(self.slopes)),
            self.slopes,
            yerr=self.slopes_std,
            fmt='.', markersize=10, linewidth=1,
            label='Slopes'
        )
        ax1.axhline(
            y=np.mean(self.slopes),
            color='r', linestyle='-',
            label=f'mean slope = {self.slopes.mean():.3e}'
        )
        ax1.set_xlabel('File index in set')
        ax1.set_ylabel('Slope (W/V)')
        ax1.set_title('Fit slopes')
        ax1.legend()

        # Intercepts
        ax2.grid(True)
        ax2.errorbar(
            range(len(self.intercepts)),
            self.intercepts,
            yerr=self.intercepts_std,
            fmt='.', markersize=10, linewidth=1,
            label='Intercepts'
        )
        ax2.axhline(
            y=np.mean(self.intercepts),
            color='g', linestyle='-',
            label=f'mean intercept = {self.intercepts.mean():.3e}'
        )
        ax2.set_xlabel('Run number in set')
        ax2.set_ylabel('Intercept (W)')
        ax2.set_title('Fit intercepts')
        ax2.legend()

        # force integer ticks on x-axis
        # ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
        # ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.set_xticks(range(len(self.slopes)))
        ax2.set_xticks(range(len(self.intercepts)))

        fig.suptitle(f'{self.anal_label} - W/V fit slopes and intercepts')
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.savefig(opath)
        plt.close(fig)

    def _gen_plot_PMvsRefPD_all_calfiles(self):

        fig_id = "PM_vs_RefPD"
        opath = os.path.join(self.output_path, fig_id + ".png")

        n_files = len(self.fs.files)

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

        for calfile in self.fs.files:
            intercept = calfile.anal.linreg_refPD_vs_meanPM.intercept
            slope = calfile.anal.linreg_refPD_vs_meanPM.slope

            # Errorbar → grab color
            eb = ax_top.errorbar(
                calfile.df['meanRefPD'],
                calfile.df['meanPM'],
                yerr=calfile.df['stdPM'],
                fmt='.', markersize=8, linewidth=1,
                label=calfile.file_label
            )

            color = eb[0].get_color()
            colors[calfile.file_label] = color

            ax_top.plot(
                calfile.df['meanRefPD'],
                intercept + slope * calfile.df['meanRefPD'],
                linewidth=1,
                color=color,
                label=f'{calfile.meta["run"]}: '
                    f'int={intercept:.2e}, slope={slope:.2e}'
            )

        ax_top.set_ylabel('Power meter (W)')
        ax_top.set_title(f'{self.anal_label} - PM vs RefPD')

        ax_top.legend(
            fontsize=8,
            ncol=2,
            frameon=False,
            handlelength=2
        )

        # ─────────────────────────────
        # Bottom row (diagnostic plots)
        # ─────────────────────────────
        for i, calfile in enumerate(self.fs.files):
            ax = fig.add_subplot(gs[3, i], sharex=ax_top, sharey=ax_top)
            ax.grid(True, alpha=0.3)

            color = colors[calfile.file_label]

            ax.errorbar(
                calfile.df['meanRefPD'],
                calfile.df['meanPM'],
                yerr=calfile.df['stdPM'],
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

        plt.savefig(opath, dpi=150)
        self.plots[fig_id] = opath
        plt.close(fig)
    
    def _gen_plots_vs_laser_setting(self):
        """Generate plots vs laser setting for the set of calibration files"""
        fig_id = "PM_vs_LaserSetting"
        opath = os.path.join(self.output_path, fig_id + ".png")
        fig = plt.figure(figsize=(10, 6))
        plt.grid()
        for calfile in self.fs.files:
            plt.errorbar(calfile.df['L'], calfile.df['meanPM'], yerr=calfile.df['stdPM'],
                         fmt='.', markersize=10, linewidth=1, label=calfile.file_label)
        plt.ylabel('Power meter (W)')
        plt.xlabel(self.laser_label)
        plt.title(f'{self.anal_label} - PM vs Laser setting')
        plt.legend()
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.savefig(opath)  # Save the current figure
        self.plots[fig_id] = opath
        plt.close(fig)

        fig_id = "RefPD_vs_LaserSetting"
        opath = os.path.join(self.output_path, fig_id + ".png")
        fig = plt.figure(figsize=(10, 6))
        plt.grid()
        for calfile in self.fs.files:
            plt.errorbar(calfile.df['L'], calfile.df['meanRefPD'], yerr=calfile.df['stdRefPD'],
                         fmt='.', markersize=10, linewidth=1, label=calfile.file_label)
        plt.ylabel('ref PD (V)')
        plt.xlabel(self.laser_label)
        plt.title(f'{self.anal_label} - RefPD vs Laser setting')
        plt.legend()
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.savefig(opath)  # Save the current figure
        self.plots[fig_id] = opath
        plt.close(fig)
    
    def _gen_pedestals_hist_plot(self):
        """Generate histogram plot of pedestal values for the set of calibration files"""
        fig_id = "Pedestals_Histogram"
        opath = os.path.join(self.output_path, fig_id + ".png")

        fig, (ax1, ax2) = plt.subplots(
            nrows=1, ncols=2, figsize=(12, 6), sharey=True
        )

        # Concatenate pedestal data
        df_pm_ped = pd.concat(
            [calfile.df_pedestal['meanPM'] for calfile in self.fs.files]
        )
        df_refpd_ped = pd.concat(
            [calfile.df_pedestal['meanRefPD'] for calfile in self.fs.files]
        )

        # ─────────────────────────────
        # Left plot: PM pedestals
        # ─────────────────────────────
        ax1.grid(True, alpha=0.3)
        ax1.hist(
            df_pm_ped,
            color='violet',
            alpha=0.7,
            label='PM Pedestals'
        )
        ax1.set_xlabel('Pedestal Mean PM (W)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('PM pedestals')
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
        fig.suptitle(f'{self.anal_label} - Histogram of pedestal values', fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.savefig(opath)
        self.plots[fig_id] = opath
        plt.close(fig)
    
    def _gen_mean_pedestals_plot(self):
        """Generate pedestal plot for the set of calibration files"""
        fig_id = "Pedestals_mean_vs_runindex"
        opath = os.path.join(self.output_path, fig_id + ".png")

        fig, (ax1, ax2) = plt.subplots(
            nrows=2, ncols=1,
            figsize=(10, 6),
            sharex=True,
            constrained_layout=True
        )

        x = range(len(self.mean_pedestal_pm))

        # ─────────────────────────────
        # Top plot: PM pedestals
        # ─────────────────────────────
        ax1.errorbar(
            x, self.mean_pedestal_pm, yerr=self.mean_pedestal_pm_std,
            fmt='.', markersize=10, linewidth=1,
            label='PM Pedestals'
        )
        mean = self.mean_pedestal_pm.mean()
        std = self.mean_pedestal_pm.std()
        samples = len(self.mean_pedestal_pm)
        ax1.axhline(y=mean, color='orange', linestyle='--', label='PM Mean of Runs Mean Pedestal')
        ax1.fill_between(range(-1, samples+1), mean-std, mean+std, color='orange', alpha=0.3, label='PM mean +/- std')
        ax1.set_ylabel('Pedestals PM (W)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # ─────────────────────────────
        # Bottom plot: RefPD pedestals
        # ─────────────────────────────
        ax2.errorbar(
            x, self.mean_pedestal_pd, yerr=self.mean_pedestal_pd_std,
            fmt='.', markersize=10, linewidth=1,
            label='RefPD Pedestals'
        )
        mean = self.mean_pedestal_pd.mean()
        std = self.mean_pedestal_pd.std()
        samples = len(self.mean_pedestal_pd)
        ax2.axhline(y=mean, color='purple', linestyle='--', label='RefPD Mean of Runs Mean Pedestal')
        ax2.fill_between(range(-1, samples+1), mean-std, mean+std, color='red', alpha=0.3, label='RefPD mean +/- std')
        ax2.set_ylabel('Pedestals RefPD (V)')
        ax2.set_xlabel('Run index')
        ax2.set_xticks(range(len(self.fs.files)))
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([-1, len(self.fs.files)])
        ax2.legend()


        plt.savefig(opath, dpi=150)
        self.plots[fig_id] = opath
        plt.close(fig)

    def _gen_pedestals_timeseries_plot(self):
        """Generate pedestal plot for the set of calibration files"""
        fig_id = "Pedestals_timeseries"
        opath = os.path.join(self.output_path, fig_id + ".png")

        fig, (ax1, ax2) = plt.subplots(
            nrows=2, ncols=1,
            figsize=(10, 6),
            sharex=True,
            constrained_layout=True
        )

        x = range(len(self.fs.concat_pedestal_df))

        # ─────────────────────────────
        # Top plot: PM pedestals
        # ─────────────────────────────
        ax1.errorbar(
            self.fs.concat_pedestal_df['datetime'], self.fs.concat_pedestal_df['meanPM'],
            yerr=self.fs.concat_pedestal_df['stdPM'],
            fmt='.', markersize=10, linewidth=1,
            label='PM Pedestals'
        )
        ax1.set_ylabel('Pedestals PM (W)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # ─────────────────────────────
        # Bottom plot: RefPD pedestals
        # ─────────────────────────────
        ax2.errorbar(
            self.fs.concat_pedestal_df['datetime'], self.fs.concat_pedestal_df['meanRefPD'],
            yerr=self.fs.concat_pedestal_df['stdRefPD'],
            fmt='.', markersize=10, linewidth=1,
            label='RefPD Pedestals'
        )
        ax2.set_ylabel('Pedestals RefPD (V)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.savefig(opath, dpi=150)
        self.plots[fig_id] = opath
        plt.close(fig)
    

    def generate_plots(self):
        """Generate plots for the set of calibration files"""
        self._gen_temp_humidity_hists_plot()
        self._gen_timeseries_plot()
        self._gen_plot_slopes_vs_temperature()
        self._gen_plot_slopes_intercepts_vs_index()

        self._gen_plots_vs_laser_setting()
        self._gen_plot_PMvsRefPD_all_calfiles()
        self._gen_pedestals_hist_plot()

        self._gen_plot_conv_factor_slope_method_comparison()
        self._gen_plot_conv_factor_intercept_method_comparison()

        self._gen_mean_pedestals_plot()
        self._gen_pedestals_timeseries_plot()

        logger.info("Plot for dataset %s generated", self.anal_label)

    def to_dict(self):
        """Convert file set analysis results to dictionary."""
        return {
            'results': self.results,
            'plots': self.plots,

        }
