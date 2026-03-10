"""Fileset-level analysis"""
from typing import TYPE_CHECKING
from scipy.stats import linregress

from characterization.helpers import get_logger
from ..helpers import CharLinReg
from .analysis_base import BaseAnal

if TYPE_CHECKING:
    from ..fileset import Fileset

logger = get_logger()

class FilesetAnalysis(BaseAnal):
    def __init__(self, fileset: 'Fileset'):
        super().__init__()
        self._data_holder = fileset
        self.adc_to_power = None
        self.adc_to_power_range = None
        self.calibration_ref = None

    @staticmethod
    def _compute_power_range(adc_to_power: dict | None, adc_min: int = 0, adc_max: int = 4095) -> dict | None:
        if not isinstance(adc_to_power, dict):
            return None
        slope = adc_to_power.get("slope")
        intercept = adc_to_power.get("intercept")
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

    def set_adc_to_power(self, adc_to_power: dict | None):
        if not isinstance(adc_to_power, dict):
            self.adc_to_power = adc_to_power
            self.adc_to_power_range = None
            return

        range_info = self._compute_power_range(adc_to_power=adc_to_power)
        self.adc_to_power_range = range_info
        conv = dict(adc_to_power)
        if range_info is not None:
            conv["power_range"] = range_info
        self.adc_to_power = conv

    def analyze(self):
        if self.df is None or self.df.empty:
            logger.error("Dataframe is not loaded for fileset: %s", self._data_holder.label)
            return
        self._calc_pedestal_stats()
        self._calc_saturation_stats(threshold=4095)
        
        x_col = self._data_holder.adc_col
        y_col = self._data_holder.ref_pd_col
        self.lr_refpd_vs_adc.x_var = x_col
        self.lr_refpd_vs_adc.y_var = y_col
        if x_col not in self.df.columns or y_col not in self.df.columns:
            logger.error(
                "Missing required regression columns (%s, %s) in fileset: %s",
                x_col,
                y_col,
                self._data_holder.label,
            )
            return
        if len(self.df) >= 2:
            self.lr_refpd_vs_adc.linreg = linregress(self.df[x_col], self.df[y_col])
        else:
            logger.warning("Not enough points for linreg in fileset: %s", self._data_holder.label)
        self._analyzed = True

    def to_dict(self) -> dict:
        if not self._analyzed:
            logger.warning("Analysis has not been performed yet for fileset: %s", self._data_holder.label)
        out = {
            'linreg_refpd_vs_adc': self.lr_refpd_vs_adc.to_dict() if self.lr_refpd_vs_adc.linreg else None,
            'pedestal_stats': self._pedestal_stats,
            'saturation_stats': self._saturation_stats,
        }
        # if self.calibration_ref is not None:
        #     out['calibration_ref'] = self.calibration_ref
        if self.adc_to_power is not None:
            out['adc_to_power'] = self.adc_to_power
        if self.adc_to_power_range is not None:
            out['adc_to_power_range'] = self.adc_to_power_range
        return out
