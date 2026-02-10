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
        df = self.char.df_pedestals
        if df is None or df.empty:
            logger.warning("No pedestal data available at characterization level.")
            return
        self.results['pedestal_stats'] = {
            'ref_pd_mean': {
                'mean': float(df['ref_pd_mean'].mean()),
                'std': float(df['ref_pd_mean'].std()),
                'samples': int(df['ref_pd_mean'].shape[0]),
            }
        }
