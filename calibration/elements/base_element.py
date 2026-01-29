from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd

from calibration.config import config

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
        self.dh_parent = None
        self.data_prep_info = {}
    
    @property
    def refpd_col(self) -> str:
        """Column name for reference photodiode data."""
        return 'ref_pd_zeroed' if config.subtract_pedestals else 'ref_pd_mean'
    
    @property
    def pm_col(self) -> str:
        """Column name for power meter data."""
        return 'pm_zeroed' if config.subtract_pedestals else 'pm_mean'
    
    @property
    def refpd_std_col(self) -> str:
        """Column name for reference photodiode standard deviation data."""
        return 'ref_pd_std'
    
    @property
    def pm_std_col(self) -> str:
        """Column name for power meter standard deviation data."""
        return 'pm_std'
    
    @property
    def power_units(self) -> str:
        """Return the units used for power measurements."""
        return 'uW' if config.use_uW_as_power_units else 'W'

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
