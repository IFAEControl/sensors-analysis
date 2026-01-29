"""
Docstring for calibration.elements.calib_file_analysis
"""

from typing import TYPE_CHECKING
from scipy.stats import linregress

from calibration.helpers import get_logger
from calibration.config import config

from ..helpers import CalibLinReg
from .analysis_base import BaseAnal

if TYPE_CHECKING:
    from ..calib_file import CalibFile


logger = get_logger()


class CalibFileAnalysis(BaseAnal):
    """
    Docstring for CalibFileAnalysis
    """
    def __init__(self, calib_file:CalibFile):
        super().__init__()
        self._data_holder:CalibFile = calib_file
        self.file_info = {}
        self._analyzed = False
        self._data_info = {}
        self.lr_refpd_vs_pm = CalibLinReg('ref_pd_mean', 'pm_mean', None)
        
        self.lr_pm_mean_vs_laser = CalibLinReg('laser_setpoint', 'pm_mean', None)
        self.lr_refpd_vs_laser = CalibLinReg('laser_setpoint', 'ref_pd_mean', None)


    def analyze(self):
        """
        Docstring for analyze
        """
        self.analyze_pedestals()
        self.calc_lin_regs()
        self._analyzed = True

    def calc_lin_regs(self):
        """Calculate linear regressions for the calibration file data."""
        if self.df is None:
            logger.error("Dataframe is not loaded for file: %s", self._data_holder.file_info['filename'])
            return
        
        if config.subtract_pedestals:
            pm_mean = 'pm_zeroed'
            ref_pd_mean = 'ref_pd_zeroed'
            
        else:
            pm_mean = 'pm_mean'
            ref_pd_mean = 'ref_pd_mean'
        
        self._data_info['used_pm_column'] = pm_mean
        self._data_info['used_refpd_column'] = ref_pd_mean

        # Perform linear regressions
        self.lr_refpd_vs_pm.linreg = linregress(self.df[ref_pd_mean], self.df[pm_mean])
        self.lr_pm_mean_vs_laser.linreg = linregress(self.df['laser_setpoint'], self.df[pm_mean])
        self.lr_refpd_vs_laser.linreg = linregress(self.df['laser_setpoint'], self.df[ref_pd_mean])
    

    def to_dict(self):
        """Return analysis results as a dictionary."""
        if self._analyzed is False:
            logger.warning("Analysis has not been performed yet for file: %s", self._data_holder.file_info['filename'])        
        return {
            'linregs': {
                'used_columns': {
                    'pm': self._data_info.get('used_pm_column'),
                    'refpd': self._data_info.get('used_refpd_column'),
                    'info': 'zeroed columns used if pedestals subtracted'
                },
                'ref_pd_vs_pm': self.lr_refpd_vs_pm.to_dict(),
                'pm_vs_laser_setpoint': self.lr_pm_mean_vs_laser.to_dict(),
                'ref_pd_vs_laser_setpoint': self.lr_refpd_vs_laser.to_dict(),
            },
            'pedestal_stats': self.pedestal_stats.to_dict(),
        }
    