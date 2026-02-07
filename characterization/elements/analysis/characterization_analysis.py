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
        self._build_summary()

    def _build_summary(self):
        self.results['photodiodes'] = list(self.photodiodes.keys())

    def to_dict(self) -> dict:
        return {
            'photodiodes': {pid: pdh.to_dict() for pid, pdh in self.photodiodes.items()},
            'summary': self.results
        }
