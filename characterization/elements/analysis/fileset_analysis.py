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
        self.calibration_ref = None


    def analyze(self):
        if self.df is None or self.df.empty:
            logger.error("Dataframe is not loaded for fileset: %s", self._data_holder.label)
            return
        self._calc_pedestal_stats()
        self._calc_saturation_stats(threshold=4095)
        
        if len(self.df) >= 2:
            self.lr_refpd_vs_adc.linreg = linregress(self.df['mean_adc'], self.df['ref_pd_mean'])
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
        return out
