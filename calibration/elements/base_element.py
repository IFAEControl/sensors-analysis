from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd

class DataHolderLevel(Enum):
    """Enum for sanity check levels."""
    CALIBRATION = 'calibration'
    FILESET = 'fileset'
    FILE = 'file'



class BaseElement(ABC):
    """Base class for calibration elements."""
    def __init__(self, level: DataHolderLevel) -> None:
        self.level = level
        self._df = None
        self._df_pedestals = None
        self._df_full = None
        self.level_header = ""

    @property
    def level_name(self) -> str:
        """Return the label of the element based on its level"""
        return self.level.value
    
    @property
    @abstractmethod
    def df(self)-> pd.DataFrame:
        """DataFrame containing the data of the calibration"""
    
    @property
    @abstractmethod
    def df_pedestals(self) -> pd.DataFrame:
        """DataFrame containing the pedestals data"""
    
    @property
    @abstractmethod
    def df_full(self) -> pd.DataFrame:
        """DataFrame containing the Full data to be analyzed full = df + pedestals"""
    
    @abstractmethod
    def analyze(self):
        """Perform the analysis."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert element data to dictionary."""
