"""Photodiode-level analysis"""

from typing import TYPE_CHECKING
from characterization.helpers import get_logger
from .analysis_base import BaseAnal

if TYPE_CHECKING:
    from ..photodiode import Photodiode

logger = get_logger()

class PhotodiodeAnalysis(BaseAnal):
    def __init__(self, photodiode: 'Photodiode'):
        super().__init__()
        self._data_holder: Photodiode = photodiode
        self.results = {}
        self._analyzed = False

    def analyze(self):
        for fs in self._data_holder.filesets.values():
            fs.analyze()
        self._analyzed = True

    def to_dict(self) -> dict:
        if not self._analyzed:
            logger.warning("Analysis has not been performed yet for photodiode: %s", self._data_holder.sensor_id)
        return self.results
