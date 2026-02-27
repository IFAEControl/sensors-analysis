"""Characterization plots across photodiodes"""

from typing import TYPE_CHECKING

from characterization.helpers import get_logger
from characterization.helpers.fileset_selector import select_fileset_for_wavelength
from characterization.config import config
from .plot_base import BasePlots
from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from ..characterization import Characterization

logger = get_logger()

class CharacterizationPlots(BasePlots):
    def __init__(self, characterization: 'Characterization'):
        super().__init__()
        self._data_holder: Characterization = characterization
        self.outpath = characterization.output_path

    @property
    def output_path(self) -> str:
        return self.outpath

    def generate_plots(self):
        if not config.generate_plots:
            return
        self._gen_saturation_points_by_filter()
        self._gen_refpd_vs_adc_linregs(include_rp=True)
        self._gen_refpd_vs_adc_linregs(include_rp=False)
        self._gen_power_vs_adc_linregs(include_extra=False)
        self._gen_refpd_pedestals_timeseries(include_temp=False)
        self._gen_refpd_pedestals_timeseries(include_temp=True)
        self._gen_refpd_pedestals_histogram()

    def _gen_saturation_points_by_filter(self):
        valid_setups = sorted({
            run
            for sensor_cfg in config.sensor_config.values()
            for run in sensor_cfg.get('valid_setups', [])
        })
        if not valid_setups:
            logger.warning("No expected runs found in configuration; skipping saturation plots.")
            return

        def sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except ValueError:
                return sensor_id

        sensors = sorted(config.sensor_config.keys(), key=sensor_sort_key)

        run_labels = valid_setups[:3]
        if len(valid_setups) > 3:
            logger.warning(
                "More than 3 wavelength/filter combinations found (%s). Plotting first 3: %s",
                len(valid_setups),
                run_labels
            )

        fig, axes = plt.subplots(nrows=len(run_labels), ncols=1, figsize=(12, 4 * len(run_labels)), sharex=True)
        if len(run_labels) == 1:
            axes = [axes]

        for ax, run_label in zip(axes, run_labels):
            counts = []
            for sensor_id in sensors:
                pdh = self._data_holder.photodiodes.get(sensor_id)
                if pdh is None:
                    counts.append(0)
                    continue
                fs = pdh.filesets.get(run_label)
                if fs is None:
                    counts.append(0)
                    continue
                stats = getattr(fs.anal, "_saturation_stats", {}) or {}
                if "num_saturated" in stats:
                    counts.append(int(stats["num_saturated"]))
                elif fs.df_sat is not None:
                    counts.append(int(fs.df_sat.shape[0]))
                else:
                    counts.append(0)

            ax.bar(sensors, counts, color=self._c("saturation_points"), label="Saturated points")
            ax.set_ylabel("Saturated points", color=self._c("saturation_points"))
            ax.tick_params(axis='y', labelcolor=self._c("saturation_points"))
            ax.set_title(f"Saturation points - {run_label}")
            ax.grid(True, axis='y')
            ax.legend(loc='upper right')

        axes[-1].set_xlabel("Sensor")
        plt.setp(axes[-1].get_xticklabels(), rotation=45, ha='right')
        fig.suptitle(f"{self._plot_label()} - Saturation points by wavelength/filter", y=1.02)
        plt.tight_layout()
        self.savefig(fig, "saturation_points_by_filter")
        plt.close(fig)

    def _gen_refpd_vs_adc_linregs(self, include_rp: bool = True):
        run_labels = sorted({
            run
            for sensor_cfg in config.sensor_config.values()
            for run in sensor_cfg.get('valid_setups', [])
        })
        if not run_labels:
            logger.warning("No wavelength/filter combinations found; skipping run linreg summary.")
            return
        wavelength_labels = sorted({run.split('_', 1)[0] for run in run_labels})

        def sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except ValueError:
                return sensor_id

        for wavelength_label in wavelength_labels:
            sensors = []
            sensor_labels = []
            slopes = []
            slope_errs = []
            intercepts = []
            intercept_errs = []
            r_values = []
            p_values = []

            for sensor_id, pdh in self._data_holder.photodiodes.items():
                cfg_key, fs = self._select_fileset_for_wavelength(
                    sensor_id=sensor_id,
                    filesets=pdh.filesets,
                    wavelength=wavelength_label,
                )
                if cfg_key is None or fs is None:
                    continue
                if fs.anal.lr_refpd_vs_adc.linreg is None:
                    continue

                filter_wheel = cfg_key.split('_', 1)[1] if '_' in cfg_key else ''
                lr = fs.anal.lr_refpd_vs_adc
                sensors.append(sensor_id)
                sensor_labels.append(f"{sensor_id} ({filter_wheel})" if filter_wheel else str(sensor_id))
                slopes.append(float(lr.slope))
                slope_errs.append(float(lr.stderr))
                intercepts.append(float(lr.intercept))
                intercept_errs.append(float(lr.intercept_stderr))
                r_values.append(float(lr.r_value))
                p_values.append(float(lr.p_value))

            if not sensors:
                logger.warning("No sensors with linreg data for wavelength %s; skipping plot.", wavelength_label)
                continue

            rows = sorted(
                zip(sensors, sensor_labels, slopes, slope_errs, intercepts, intercept_errs, r_values, p_values),
                key=lambda row: sensor_sort_key(row[0])
            )
            sensors, sensor_labels, slopes, slope_errs, intercepts, intercept_errs, r_values, p_values = map(list, zip(*rows))

            nrows = 3 if include_rp else 2
            fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(12, 4 * nrows), sharex=True)
            x = list(range(len(sensor_labels)))

            axes[0].errorbar(x, slopes, yerr=slope_errs, fmt=self._m("linreg_slope"), color=self._c("linreg_slope"), label='Slope')
            axes[0].set_ylabel("Slope (V/#adc)", color=self._c("linreg_slope"))
            axes[0].tick_params(axis='y', labelcolor=self._c("linreg_slope"))
            axes[0].grid(True, axis='y')
            axes[0].legend(loc='upper right')
            axes[0].set_title(f"V RefPD vs Adc counts for {wavelength_label}")

            axes[1].errorbar(x, intercepts, yerr=intercept_errs, fmt=self._m("linreg_intercept"), color=self._c("linreg_intercept"), label='Intercept')
            axes[1].set_ylabel("Intercept (V)", color=self._c("linreg_intercept"))
            axes[1].tick_params(axis='y', labelcolor=self._c("linreg_intercept"))
            axes[1].grid(True, axis='y')
            axes[1].legend(loc='upper right')

            if include_rp:
                ax_r = axes[2]
                ax_p = ax_r.twinx()
                ax_r.scatter(x, r_values, marker=self._m("linreg_r_value"), color=self._c("linreg_r_value"), label='r-value')
                ax_r.set_ylabel("r", color=self._c("linreg_r_value"))
                ax_r.tick_params(axis='y', labelcolor=self._c("linreg_r_value"))
                ax_r.grid(True, axis='y')

                ax_p.scatter(x, p_values, marker=self._m("linreg_p_value"), color=self._c("linreg_p_value"), label='p-value')
                ax_p.set_ylabel("p", color=self._c("linreg_p_value"))
                ax_p.tick_params(axis='y', labelcolor=self._c("linreg_p_value"))

                h1, l1 = ax_r.get_legend_handles_labels()
                h2, l2 = ax_p.get_legend_handles_labels()
                ax_r.legend(h1 + h2, l1 + l2, loc='upper right')

            axes[-1].set_xlabel("Sensor")
            axes[-1].set_xticks(x)
            axes[-1].set_xticklabels(sensor_labels)
            plt.setp(axes[-1].get_xticklabels(), rotation=45, ha='right')
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            suffix = "" if include_rp else "_simp"
            self.savefig(fig, f"refpd_vs_adc_linregs_{wavelength_label}{suffix}")
            plt.close(fig)

    def _gen_power_vs_adc_linregs(self, include_extra: bool = True):
        run_labels = sorted({
            run
            for sensor_cfg in config.sensor_config.values()
            for run in sensor_cfg.get('valid_setups', [])
        })
        if not run_labels:
            logger.warning("No wavelength/filter combinations found; skipping power vs adc linreg summary.")
            return
        wavelength_labels = sorted({run.split('_', 1)[0] for run in run_labels})

        def sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except ValueError:
                return sensor_id

        power_unit = self._data_holder.calibration_info.get('power_unit') or 'power'
        for wavelength_label in wavelength_labels:
            sensors = []
            sensor_labels = []
            slopes = []
            slope_errs = []
            intercepts = []
            intercept_errs = []

            for sensor_id, pdh in self._data_holder.photodiodes.items():
                cfg_key, fs = self._select_fileset_for_wavelength(
                    sensor_id=sensor_id,
                    filesets=pdh.filesets,
                    wavelength=wavelength_label,
                )
                if cfg_key is None or fs is None:
                    continue
                conv = fs.anal.adc_to_power
                if not isinstance(conv, dict):
                    continue

                filter_wheel = cfg_key.split('_', 1)[1] if '_' in cfg_key else ''
                sensors.append(sensor_id)
                sensor_labels.append(f"{sensor_id} ({filter_wheel})" if filter_wheel else str(sensor_id))
                slopes.append(float(conv.get('slope', 0.0)))
                slope_errs.append(float(conv.get('slope_err', 0.0)))
                intercepts.append(float(conv.get('intercept', 0.0)))
                intercept_errs.append(float(conv.get('intercept_err', 0.0)))

            if not sensors:
                logger.warning("No sensors with power-vs-adc conversion data for wavelength %s; skipping plot.", wavelength_label)
                continue

            rows = sorted(
                zip(sensors, sensor_labels, slopes, slope_errs, intercepts, intercept_errs),
                key=lambda row: sensor_sort_key(row[0])
            )
            sensors, sensor_labels, slopes, slope_errs, intercepts, intercept_errs = map(list, zip(*rows))

            nrows = 3 if include_extra else 2
            fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(12, 4 * nrows), sharex=True)
            x = list(range(len(sensor_labels)))

            axes[0].errorbar(x, slopes, yerr=slope_errs, fmt=self._m("power_slope"), color=self._c("power_slope"), label='Slope')
            axes[0].set_ylabel(f"Slope ({power_unit}/#adc)", color=self._c("power_slope"))
            axes[0].tick_params(axis='y', labelcolor=self._c("power_slope"))
            axes[0].grid(True, axis='y')
            axes[0].legend(loc='upper right')
            axes[0].set_title(f"Power vs Adc counts for {wavelength_label}")

            axes[1].errorbar(x, intercepts, yerr=intercept_errs, fmt=self._m("power_intercept"), color=self._c("power_intercept"), label='Intercept')
            axes[1].set_ylabel(f"Intercept ({power_unit})", color=self._c("power_intercept"))
            axes[1].tick_params(axis='y', labelcolor=self._c("power_intercept"))
            axes[1].grid(True, axis='y')
            axes[1].legend(loc='upper right')

            if include_extra:
                ax_err = axes[2]
                ax_err2 = ax_err.twinx()
                ax_err.scatter(x, slope_errs, marker=self._m("power_slope_err"), color=self._c("power_slope_err"), label='slope_err')
                ax_err.set_ylabel(f"slope_err ({power_unit}/#adc)", color=self._c("power_slope_err"))
                ax_err.tick_params(axis='y', labelcolor=self._c("power_slope_err"))
                ax_err.grid(True, axis='y')

                ax_err2.scatter(x, intercept_errs, marker=self._m("power_intercept_err"), color=self._c("power_intercept_err"), label='intercept_err')
                ax_err2.set_ylabel(f"intercept_err ({power_unit})", color=self._c("power_intercept_err"))
                ax_err2.tick_params(axis='y', labelcolor=self._c("power_intercept_err"))

                h1, l1 = ax_err.get_legend_handles_labels()
                h2, l2 = ax_err2.get_legend_handles_labels()
                ax_err.legend(h1 + h2, l1 + l2, loc='upper right')

            axes[-1].set_xlabel("Sensor")
            axes[-1].set_xticks(x)
            axes[-1].set_xticklabels(sensor_labels)
            plt.setp(axes[-1].get_xticklabels(), rotation=45, ha='right')
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            suffix = "" if include_extra else "_simp"
            self.savefig(fig, f"power_vs_adc_linregs_{wavelength_label}{suffix}")
            plt.close(fig)

    def _select_fileset_for_wavelength(self, sensor_id: str, filesets: dict, wavelength: str):
        selection = select_fileset_for_wavelength(
            fileset_keys=filesets.keys(),
            wavelength=wavelength,
            sensor_id=sensor_id,
        )
        if selection.selected_key is None:
            return None, None
        if len(selection.candidates) > 1 and selection.reason != "expected_match":
            logger.warning(
                "Ambiguous %s filesets for photodiode %s; candidates=%s; selected=%s (reason=%s)",
                wavelength,
                sensor_id,
                list(selection.candidates),
                selection.selected_key,
                selection.reason,
            )
        return selection.selected_key, filesets.get(selection.selected_key)

    def _gen_refpd_pedestals_timeseries(self, include_temp: bool = False):
        df = self._data_holder.df_pedestals
        if df is None or df.empty:
            logger.warning("No pedestal data available for characterization ref_pd timeseries plot.")
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

        ax.set_title("characterization ref PD pedestals")
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
            logger.warning("No pedestal data available for characterization ref_pd histogram plot.")
            return

        fig_id = "refpd_pedestals_histogram"
        fig, ax = plt.subplots(figsize=(10, 6))

        y = df['ref_pd_mean']
        mean = float(y.mean())
        std = float(y.std())
        self._draw_confidence_band(ax, mean, std, metric="ref_pd_mean", orientation="v")
        ax.hist(y, bins=40, color=self._c("ref_pd_mean"), label="RefPD pedestals", zorder=2)

        ax.set_title("characterization ref PD pedestals histogram")
        ax.set_xlabel("RefPD (V)")
        ax.set_ylabel("Count")
        ax.tick_params(axis='x', labelcolor=self._c("ref_pd_mean"))
        ax.grid(True)
        ax.legend(loc='best')

        plt.tight_layout()
        self.savefig(fig, fig_id)
        plt.close(fig)
