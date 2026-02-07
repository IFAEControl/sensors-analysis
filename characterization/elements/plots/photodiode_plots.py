"""Photodiode plots"""

from typing import TYPE_CHECKING

from characterization.helpers import get_logger
from .plot_base import BasePlots

if TYPE_CHECKING:
    from ..photodiode import Photodiode

logger = get_logger()

class PhotodiodePlots(BasePlots):
    def __init__(self, photodiode: 'Photodiode'):
        super().__init__()
        self._data_holder: Photodiode = photodiode

    @property
    def output_path(self) -> str:
        return self._data_holder.output_path if self._data_holder.output_path else '.'

    def generate_plots(self):
        self._gen_timeseries_plot()
        fileplots = self.plots.setdefault('files', {})
        for cf in self._data_holder.files:
            cf.plotter.generate_plots()
            fileplots[cf.level_header] = cf.plotter.plots

        fileset_plots = self.plots.setdefault('filesets', {})
        for key, fs in self._data_holder.filesets.items():
            fs.generate_plots()
            fileset_plots[key] = fs.plotter.plots
