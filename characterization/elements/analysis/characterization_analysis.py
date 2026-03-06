"""Characterization analysis across photodiodes"""

from typing import TYPE_CHECKING
import numpy as np
from characterization.helpers import get_logger
from characterization.config import config
from .analysis_base import BaseAnal

if TYPE_CHECKING:
    from ..characterization import Characterization

logger = get_logger()

class CharacterizationAnalysis(BaseAnal):
    def __init__(self, characterization: 'Characterization'):
        super().__init__()
        self._data_holder: Characterization = characterization
        self.char = characterization
        self.photodiodes = characterization.photodiodes
        self.results = {}

    def analyze(self):
        for pdh in self.photodiodes.values():
            pdh.analyze()
        self._calc_refpd_pedestal_stats()
        self._calc_linreg_group_stats()

    def to_dict(self) -> dict:
        def _sensor_sort_key(sensor_id: str):
            try:
                return float(sensor_id)
            except (ValueError, TypeError):
                return str(sensor_id)

        return {
            'photodiodes': {
                pid: pdh.to_dict()
                for pid, pdh in sorted(self.photodiodes.items(), key=lambda item: _sensor_sort_key(item[0]))
            },
            **self.results,
        }

    def _calc_refpd_pedestal_stats(self):
        if self.char.df_pedestals is None or self.char.df_pedestals.empty:
            logger.warning("No pedestal data available at characterization level.")
            return
        refpd_stats = self._calc_single_pedestal_stat("ref_pd_mean", "ref_pd_std")
        if refpd_stats is None:
            logger.warning("Missing ref_pd_mean/ref_pd_std columns in characterization pedestals.")
            return
        self.results['pedestal_stats'] = {
            "ref_pd_mean": refpd_stats
        }

    def _calc_linreg_group_stats(self):
        lr_rows = []
        adc_to_power_rows = []
        for sensor_id, pdh in self.photodiodes.items():
            sensor_gain = str(config.sensor_config.get(sensor_id, {}).get("gain", "UNK"))
            for cfg_key, fs in pdh.filesets.items():
                wavelength = cfg_key.split("_", 1)[0] if cfg_key else "UNK"
                group_key = f"{wavelength}_{sensor_gain}"

                lr = fs.anal.lr_refpd_vs_adc
                if lr is not None and lr.linreg is not None:
                    lr_rows.append(
                        {
                            "sensor_id": sensor_id,
                            "group": group_key,
                            "slope": float(lr.slope),
                            "intercept": float(lr.intercept),
                            "r_value": float(lr.r_value),
                        }
                    )

                adc_to_power = fs.anal.adc_to_power if isinstance(fs.anal.adc_to_power, dict) else {}
                conv_slope = adc_to_power.get("slope")
                conv_intercept = adc_to_power.get("intercept")
                if conv_slope is not None and conv_intercept is not None:
                    adc_to_power_rows.append(
                        {
                            "sensor_id": sensor_id,
                            "group": group_key,
                            "slope": float(conv_slope),
                            "intercept": float(conv_intercept),
                        }
                    )

        lr_grouped: dict[str, list[dict]] = {}
        for row in lr_rows:
            lr_grouped.setdefault(row["group"], [])
            lr_grouped[row["group"]].append(row)

        lr_out = {}
        for group_key, group_rows in lr_grouped.items():
            slopes = np.array([r["slope"] for r in group_rows], dtype=float)
            intercepts = np.array([r["intercept"] for r in group_rows], dtype=float)
            r_values = np.array([r["r_value"] for r in group_rows], dtype=float)

            slope_median = float(np.median(slopes))
            intercept_median = float(np.median(intercepts))
            deviations = []
            for r in group_rows:
                slope_rel_dev_pct = None
                if slope_median != 0:
                    slope_rel_dev_pct = float((r["slope"] - slope_median) / slope_median * 100.0)
                deviations.append(
                    {
                        "sensor_id": r["sensor_id"],
                        "slope_rel_dev_pct": slope_rel_dev_pct,
                    }
                )

            lr_out[group_key] = {
                "lr_refpd_vs_adc_summary": {
                    "num_photodiodes": int(len(group_rows)),
                    "slope_mean": float(np.mean(slopes)),
                    "slope_median": slope_median,
                    "slope_std": float(np.std(slopes)),
                    "intercept_mean": float(np.mean(intercepts)),
                    "intercept_median": intercept_median,
                    "intercept_std": float(np.std(intercepts)),
                    "r_value_median": float(np.median(r_values)),
                },
                "lr_refpd_vs_adc_relative_deviation_by_pd": deviations,
            }

        adc_to_power_grouped: dict[str, list[dict]] = {}
        for row in adc_to_power_rows:
            adc_to_power_grouped.setdefault(row["group"], [])
            adc_to_power_grouped[row["group"]].append(row)

        adc_to_power_out = {}
        for group_key, group_rows in adc_to_power_grouped.items():
            slopes = np.array([r["slope"] for r in group_rows], dtype=float)
            intercepts = np.array([r["intercept"] for r in group_rows], dtype=float)
            adc_to_power_out[group_key] = {
                "adc_to_power_summary": {
                    "num_photodiodes": int(len(group_rows)),
                    "slope_mean": float(np.mean(slopes)),
                    "slope_median": float(np.median(slopes)),
                    "slope_std": float(np.std(slopes)),
                    "intercept_mean": float(np.mean(intercepts)),
                    "intercept_median": float(np.median(intercepts)),
                    "intercept_std": float(np.std(intercepts)),
                }
            }

        self.results["lr_refpd_vs_adc_by_wavelength_gain"] = lr_out
        self.results["adc_to_power_by_wavelength_gain"] = adc_to_power_out
