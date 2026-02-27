"""Characterization analysis across photodiodes"""

from typing import TYPE_CHECKING
import numpy as np
from characterization.helpers import get_logger
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
        return {
            'photodiodes': {pid: pdh.to_dict() for pid, pdh in self.photodiodes.items()},
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
        rows = []
        for sensor_id, pdh in self.photodiodes.items():
            for cfg_key, fs in pdh.filesets.items():
                lr = fs.anal.lr_refpd_vs_adc
                if lr is None or lr.linreg is None:
                    continue
                rows.append(
                    {
                        "sensor_id": sensor_id,
                        "group": cfg_key,  # wavelength_filter, e.g. 1064_FW5
                        "slope": float(lr.slope),
                        "intercept": float(lr.intercept),
                        "r_value": float(lr.r_value),
                    }
                )

        grouped: dict[str, dict] = {}
        for row in rows:
            grouped.setdefault(row["group"], {"rows": []})
            grouped[row["group"]]["rows"].append(row)

        out = {}
        for group_key, payload in grouped.items():
            group_rows = payload["rows"]
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

            out[group_key] = {
                "summary": {
                    "num_photodiodes": int(len(group_rows)),
                    "slope_mean": float(np.mean(slopes)),
                    "slope_median": slope_median,
                    "slope_std": float(np.std(slopes)),
                    "intercept_mean": float(np.mean(intercepts)),
                    "intercept_median": intercept_median,
                    "intercept_std": float(np.std(intercepts)),
                    "r_value_median": float(np.median(r_values)),
                },
                "relative_deviation_by_pd": deviations,
            }

        self.results["linreg_by_wavelength_filter"] = out
