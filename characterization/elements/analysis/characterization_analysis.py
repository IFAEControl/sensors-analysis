"""Characterization analysis across photodiodes"""

from typing import TYPE_CHECKING
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
