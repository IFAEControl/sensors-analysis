"""Calibration analysis across multiple file sets"""

from typing import TYPE_CHECKING

import pandas as pd

from calibration.helpers import get_logger
from calibration.config import config
from .plot_base import BasePlots

if TYPE_CHECKING:
    from ..calibration import Calibration
    from ..calib_file import CalibFile

logger = get_logger()


class CalibrationPlots(BasePlots):
    """
    CalibrationAPlots

    Generate plots at Calibration Level
    """
    def __init__(self, calibration:Calibration):
        super().__init__()
        self._data_holder:Calibration = calibration
        self.outpath = calibration.plots_path
    
    @property
    def output_path(self) -> str:
        """Output path for storing analysis results and plots."""
        return self.outpath

    @property
    def laser_label(self) -> str:
        """Label for the laser parameter."""
        return 'laser_setpoint'

    def generate_plots(self):
        """Generate plots interrelating data from all sets of calibration files."""
        # plot of whole calibration data acquisition temperature and humidity
        if config.generate_plots:
            self._gen_timeseries_plot()
            self._gen_temp_humidity_hists_plot()
            self._gen_pedestals_timeseries_plot()
            self._gen_pm_samples_plot_full()
            self._gen_pm_samples_plot_pedestals()            

