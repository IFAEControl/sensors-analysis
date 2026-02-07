"""Characterization plots across photodiodes"""

from typing import TYPE_CHECKING

from characterization.helpers import get_logger
from characterization.config import config
from .plot_base import BasePlots

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
        # No cross-photodiode plots for now.
