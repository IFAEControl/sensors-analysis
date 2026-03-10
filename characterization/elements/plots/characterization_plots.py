"""Characterization plots across photodiodes"""

from typing import TYPE_CHECKING
import numpy as np
from matplotlib.patches import Rectangle

from characterization.helpers import get_logger
from characterization.helpers.fileset_selector import select_fileset_for_wavelength
from characterization.config import config, simulation_values
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
        self._gen_relative_slope_deviation_by_gain_and_wavelength()
        self._gen_voltage_slope_vs_intercept_by_wavelength()
        self._gen_power_slope_vs_intercept_by_wavelength()
        self._gen_power_range_rectangles_by_wavelength()
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

    def _collect_linreg_rows_by_group(self) -> dict[str, list[dict]]:
        grouped: dict[str, list[dict]] = {}
        for sensor_id, pdh in self._data_holder.photodiodes.items():
            gain = str(config.sensor_config.get(sensor_id, {}).get("gain", "UNK"))
            for cfg_key, fs in pdh.filesets.items():
                lr = fs.anal.lr_refpd_vs_adc
                if lr is None or lr.linreg is None:
                    continue
                grouped.setdefault(cfg_key, [])
                parts = cfg_key.split("_", 1)
                wavelength = parts[0] if parts else cfg_key
                filter_group = parts[1] if len(parts) > 1 else "UNK"
                grouped[cfg_key].append(
                    {
                        "sensor_id": sensor_id,
                        "gain": gain,
                        "wavelength": wavelength,
                        "filter_group": filter_group,
                        "slope": float(lr.slope),
                        "intercept": float(lr.intercept),
                    }
                )
        return grouped

    def _gen_relative_slope_deviation_by_gain_and_wavelength(self):
        grouped = self._collect_linreg_rows_by_group()
        if not grouped:
            logger.warning("No linreg data available for relative slope deviation plot.")
            return

        def sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except ValueError:
                return sensor_id

        by_wavelength_gain: dict[str, dict[str, list[dict]]] = {}
        for rows in grouped.values():
            for row in rows:
                wl = row["wavelength"]
                gain = row["gain"]
                by_wavelength_gain.setdefault(wl, {})
                by_wavelength_gain[wl].setdefault(gain, [])
                by_wavelength_gain[wl][gain].append(row)

        for wavelength, gain_rows in sorted(by_wavelength_gain.items()):
            gain_keys = sorted(gain_rows.keys())
            fig, axes = plt.subplots(nrows=len(gain_keys), ncols=1, figsize=(12, 4 * len(gain_keys)), sharex=False)
            if len(gain_keys) == 1:
                axes = [axes]

            for ax, gain in zip(axes, gain_keys):
                rows = sorted(gain_rows[gain], key=lambda r: sensor_sort_key(r["sensor_id"]))
                slopes = [r["slope"] for r in rows]
                slope_median = float(np.median(slopes))
                x_labels = [r["sensor_id"] for r in rows]
                x = list(range(len(rows)))
                y = [
                    0.0 if slope_median == 0.0 else ((r["slope"] - slope_median) / slope_median) * 100.0
                    for r in rows
                ]

                ax.bar(x, y, color=self._c("linreg_slope"), label=f"{gain} slope relative deviation")
                ax.axhline(0.0, color=self._c("fit_line"), linestyle=self._ls("fit_line"), linewidth=1.2)
                ax.set_title(f"{wavelength} - {gain}")
                ax.set_ylabel("Slope dev (%)", color=self._c("linreg_slope"))
                ax.tick_params(axis='y', labelcolor=self._c("linreg_slope"))
                ax.set_xticks(x)
                ax.set_xticklabels(x_labels)
                ax.grid(True, axis='y')
                ax.legend(loc='upper right')
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

            axes[-1].set_xlabel("Sensor")
            plt.tight_layout()
            self.savefig(fig, f"relative_slope_deviation_by_gain_{wavelength}")
            plt.close(fig)

    def _collect_linreg_scatter_points(self) -> dict[str, dict[str, list[dict]]]:
        grouped = self._collect_linreg_rows_by_group()
        out: dict[str, dict[str, list[dict]]] = {}
        for cfg_key, rows in grouped.items():
            parts = cfg_key.split("_", 1)
            wavelength = parts[0] if parts else cfg_key
            filter_group = parts[1] if len(parts) > 1 else "UNK"
            out.setdefault(wavelength, {})
            out[wavelength].setdefault(filter_group, [])
            for row in rows:
                sensor_id = row["sensor_id"]
                pdh = self._data_holder.photodiodes.get(sensor_id)
                fs = pdh.filesets.get(cfg_key) if pdh is not None else None
                if fs is None:
                    continue
                conv = fs.anal.adc_to_power if isinstance(fs.anal.adc_to_power, dict) else {}
                out[wavelength][filter_group].append(
                    {
                        "sensor_id": sensor_id,
                        "slope_v": float(row["slope"]),
                        "intercept_v": float(row["intercept"]),
                        "slope_power": float(conv.get("slope")) if conv.get("slope") is not None else None,
                        "intercept_power": float(conv.get("intercept")) if conv.get("intercept") is not None else None,
                    }
                )
        return out

    def _gen_voltage_slope_vs_intercept_by_wavelength(self):
        by_wavelength_filter = self._collect_linreg_scatter_points()
        if not by_wavelength_filter:
            logger.warning("No linreg data available for voltage slope-vs-intercept plots.")
            return

        for wavelength, filter_rows in sorted(by_wavelength_filter.items()):
            fig, ax = plt.subplots(figsize=(10, 6))
            plotted_any = False
            for idx, (filter_group, rows) in enumerate(sorted(filter_rows.items())):
                if not rows:
                    continue
                x_intercept = [r["intercept_v"] for r in rows]
                y_slope = [r["slope_v"] for r in rows]
                color = self._c("filter_fw4") if filter_group == "FW4" else self._c("filter_fw5")
                marker = self._series_marker(idx, base_marker=self._m("linreg_slope"))
                ax.scatter(x_intercept, y_slope, color=color, marker=marker, label=filter_group)
                plotted_any = True

            if not plotted_any:
                plt.close(fig)
                continue

            ax.set_title(f"Slope vs intercept (voltage) - {wavelength}")
            ax.set_xlabel("Intercept (V)", color=self._c("linreg_intercept"))
            ax.set_ylabel("Slope (V/#adc)", color=self._c("linreg_slope"))
            ax.tick_params(axis='x', labelcolor=self._c("linreg_intercept"))
            ax.tick_params(axis='y', labelcolor=self._c("linreg_slope"))
            ax.grid(True)
            ax.legend(loc='best', title="Filter group")

            plt.tight_layout()
            self.savefig(fig, f"linreg_voltage_slope_vs_intercept_{wavelength}")
            plt.close(fig)

    def _gen_power_slope_vs_intercept_by_wavelength(self):
        by_wavelength_filter = self._collect_linreg_scatter_points()
        if not by_wavelength_filter:
            logger.warning("No linreg data available for power slope-vs-intercept plots.")
            return
        power_unit = self._data_holder.calibration_info.get("power_unit") or "power"

        for wavelength, filter_rows in sorted(by_wavelength_filter.items()):
            fig, ax = plt.subplots(figsize=(10, 6))
            plotted_any = False
            for idx, (filter_group, rows) in enumerate(sorted(filter_rows.items())):
                rows_with_power = [
                    r for r in rows
                    if r["slope_power"] is not None and r["intercept_power"] is not None
                ]
                if not rows_with_power:
                    continue
                x_intercept = [r["intercept_power"] for r in rows_with_power]
                y_slope = [r["slope_power"] for r in rows_with_power]
                color = self._c("filter_fw4") if filter_group == "FW4" else self._c("filter_fw5")
                marker = self._series_marker(idx, base_marker=self._m("power_slope"))
                ax.scatter(x_intercept, y_slope, color=color, marker=marker, label=filter_group)
                plotted_any = True

            if not plotted_any:
                plt.close(fig)
                continue

            ax.set_title(f"Slope vs intercept (power) - {wavelength}")
            ax.set_xlabel(f"Intercept ({power_unit})", color=self._c("power_intercept"))
            ax.set_ylabel(f"Slope ({power_unit}/#adc)", color=self._c("power_slope"))
            ax.tick_params(axis='x', labelcolor=self._c("power_intercept"))
            ax.tick_params(axis='y', labelcolor=self._c("power_slope"))
            ax.grid(True)
            ax.legend(loc='best', title="Filter group")

            plt.tight_layout()
            self.savefig(fig, f"linreg_power_slope_vs_intercept_{wavelength}")
            plt.close(fig)

    @staticmethod
    def _compute_power_range_from_conversion(conv: dict | None, adc_min: int = 0, adc_max: int = 4095) -> dict | None:
        if not isinstance(conv, dict):
            return None
        slope = conv.get("slope")
        intercept = conv.get("intercept")
        if slope is None or intercept is None:
            return None
        slope_f = float(slope)
        intercept_f = float(intercept)
        adc_min_f = float(adc_min)
        adc_max_f = float(adc_max)
        power_at_adc_min = slope_f * adc_min_f + intercept_f
        power_at_adc_max = slope_f * adc_max_f + intercept_f
        power_low = min(power_at_adc_min, power_at_adc_max)
        power_high = max(power_at_adc_min, power_at_adc_max)
        return {
            "adc_min": int(adc_min),
            "adc_max": int(adc_max),
            "power_at_adc_min": float(power_at_adc_min),
            "power_at_adc_max": float(power_at_adc_max),
            "power_low": float(power_low),
            "power_high": float(power_high),
            "power_span": float(power_high - power_low),
        }

    def _gen_power_range_rectangles_by_wavelength(self):
        run_labels = sorted({
            run
            for sensor_cfg in config.sensor_config.values()
            for run in sensor_cfg.get('valid_setups', [])
        })
        if not run_labels:
            logger.warning("No wavelength/filter combinations found; skipping power-range plot.")
            return
        wavelength_labels = sorted({run.split('_', 1)[0] for run in run_labels})
        power_unit = self._data_holder.calibration_info.get("power_unit") or "power"
        sim_unit_scale = 1e6 if str(power_unit).lower() in {"uw", "µw"} else 1.0

        def sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except ValueError:
                return sensor_id

        def parse_ring_angle(sensor_id: str) -> tuple[int | None, int | None]:
            sid = str(sensor_id)
            if "." not in sid:
                return None, None
            left, right = sid.split(".", 1)
            try:
                return int(left), int(right)
            except ValueError:
                return None, None

        sim_values = simulation_values or {}

        def should_show_simulation_overlay(wavelength_value: str) -> bool:
            wl = str(wavelength_value).strip()
            if wl.startswith("1064"):
                return True
            try:
                return np.isclose(float(wl), 1064.0)
            except ValueError:
                return False

        def simulation_entry_for_ring(ring_idx: int) -> dict | None:
            candidates = {int(ring_idx)}
            for sim_entry in sim_values.values():
                if not isinstance(sim_entry, dict):
                    continue
                sim_ring = sim_entry.get("ring")
                if sim_ring is None:
                    continue
                try:
                    if int(sim_ring) in candidates:
                        return sim_entry
                except (TypeError, ValueError):
                    continue
            return None

        for wavelength_label in wavelength_labels:
            rows = []
            show_simulation_overlay = should_show_simulation_overlay(wavelength_label)
            for sensor_id, pdh in self._data_holder.photodiodes.items():
                cfg_key, fs = self._select_fileset_for_wavelength(
                    sensor_id=sensor_id,
                    filesets=pdh.filesets,
                    wavelength=wavelength_label,
                )
                if cfg_key is None or fs is None:
                    continue
                conv = fs.anal.adc_to_power if isinstance(fs.anal.adc_to_power, dict) else None
                if conv is None:
                    continue
                range_info = conv.get("power_range")
                if not isinstance(range_info, dict):
                    range_info = self._compute_power_range_from_conversion(conv)
                if not isinstance(range_info, dict):
                    continue

                filter_wheel = cfg_key.split('_', 1)[1] if '_' in cfg_key else 'UNK'
                rows.append(
                    {
                        "sensor_id": sensor_id,
                        "ring": parse_ring_angle(sensor_id)[0],
                        "angle": parse_ring_angle(sensor_id)[1],
                        "filter_wheel": filter_wheel,
                        "label": f"{sensor_id} ({filter_wheel})",
                        "power_at_adc_min": float(range_info["power_at_adc_min"]),
                        "power_at_adc_max": float(range_info["power_at_adc_max"]),
                        "power_low": float(range_info["power_low"]),
                        "power_high": float(range_info["power_high"]),
                    }
                )

            if not rows:
                logger.warning("No sensors with adc_to_power ranges for wavelength %s; skipping plot.", wavelength_label)
                continue

            rows = sorted(
                rows,
                key=lambda r: (
                    10**9 if r["ring"] is None else r["ring"],
                    10**9 if r["angle"] is None else r["angle"],
                    sensor_sort_key(r["sensor_id"]),
                ),
            )
            x = np.arange(len(rows), dtype=float)
            rect_width = 0.68
            fig, ax = plt.subplots(figsize=(12, 6))

            y_min = min(r["power_low"] for r in rows)
            y_max = max(r["power_high"] for r in rows)
            if show_simulation_overlay:
                for sim_data in sim_values.values():
                    if not isinstance(sim_data, dict):
                        continue
                    sim_min = sim_data.get("min")
                    sim_max = sim_data.get("max")
                    if sim_min is None or sim_max is None:
                        continue
                    y_min = min(y_min, float(sim_min) * sim_unit_scale)
                    y_max = max(y_max, float(sim_max) * sim_unit_scale)
            y_span = y_max - y_min
            y_pad = max(y_span * 0.08, 1e-12)

            first = True
            ring_positions: dict[int, list[int]] = {}
            for i, row in enumerate(rows):
                if row["ring"] is not None:
                    ring_positions.setdefault(int(row["ring"]), [])
                    ring_positions[int(row["ring"])].append(i)
                left = x[i] - rect_width / 2.0
                height = row["power_high"] - row["power_low"]
                rect = Rectangle(
                    (left, row["power_low"]),
                    rect_width,
                    height if height > 0.0 else 1e-12,
                    facecolor=self._c("power_range_fill"),
                    edgecolor=self._c("power_range_rect_edge"),
                    linewidth=1.0,
                    alpha=0.35,
                    label="Power range (ADC 0..4095)" if first else None,
                )
                ax.add_patch(rect)
                ax.hlines(
                    row["power_at_adc_min"],
                    left,
                    left + rect_width,
                    colors=self._c("power_at_adc_min"),
                    linestyles=self._ls("power_at_adc_min"),
                    linewidth=1.5,
                    label="Power @ ADC=0" if first else None,
                )
                ax.hlines(
                    row["power_at_adc_max"],
                    left,
                    left + rect_width,
                    colors=self._c("power_at_adc_max"),
                    linestyles=self._ls("power_at_adc_max"),
                    linewidth=1.5,
                    label="Power @ ADC=4095" if first else None,
                )
                first = False

            if show_simulation_overlay:
                # Overlay simulated expected-power ranges by ring as foreground rectangles.
                first_sim = True
                y_display_span = max((y_max + y_pad) - (y_min - y_pad), 1e-12)
                min_sim_display_height = y_display_span * 0.006
                for ring_idx, idxs in sorted(ring_positions.items()):
                    sim_entry = simulation_entry_for_ring(ring_idx)
                    if not isinstance(sim_entry, dict):
                        continue
                    sim_min = sim_entry.get("min")
                    sim_max = sim_entry.get("max")
                    sim_mean = sim_entry.get("mean")
                    if sim_min is None or sim_max is None:
                        continue
                    sim_min_f = float(sim_min) * sim_unit_scale
                    sim_max_f = float(sim_max) * sim_unit_scale
                    sim_mean_f = float(sim_mean) * sim_unit_scale if sim_mean is not None else None
                    bottom = min(sim_min_f, sim_max_f)
                    top = max(sim_min_f, sim_max_f)
                    display_height = max(top - bottom, min_sim_display_height)
                    display_bottom = ((bottom + top) / 2.0) - (display_height / 2.0)

                    left = min(idxs) - rect_width / 2.0
                    width = (max(idxs) - min(idxs)) + rect_width
                    sim_rect = Rectangle(
                        (left, display_bottom),
                        width,
                        display_height,
                        facecolor=self._c("sim_power_range_fill"),
                        edgecolor=self._c("sim_power_range_edge"),
                        linewidth=1.4,
                        alpha=0.45,
                        zorder=30,
                        label="Expected simulated power" if first_sim else None,
                    )
                    ax.add_patch(sim_rect)
                    if sim_mean_f is not None:
                        ax.hlines(
                            sim_mean_f,
                            left,
                            left + width,
                            colors=self._c("sim_power_range_edge"),
                            linestyles="--",
                            linewidth=1.5,
                            zorder=31,
                            label=f"Sim mean ring {ring_idx}: {sim_mean_f:.3e} {power_unit}",
                        )
                    ax.hlines(
                        [bottom, top],
                        left,
                        left + width,
                        colors=self._c("sim_power_range_edge"),
                        linestyles="--",
                        linewidth=1.0,
                        zorder=31,
                    )
                    first_sim = False

            ax.set_xlim(-0.8, len(rows) - 0.2)
            ax.set_ylim(y_min - y_pad, y_max + y_pad)
            ax.set_xticks(x)
            ax.set_xticklabels([r["label"] for r in rows])
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_ylabel(f"Power ({power_unit})")
            ax.set_xlabel("Sensor")
            ax.set_title(f"ADC-to-power range by sensor - {wavelength_label}")
            ax.grid(True, axis='y', alpha=0.3)
            ax.legend(loc="best")

            plt.tight_layout()
            self.savefig(fig, f"power_range_by_sensor_{wavelength_label}")
            plt.close(fig)
