from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd

class DataHolderLevel(Enum):
    CHARACTERIZATION = 'characterization'
    PHOTODIODE = 'photodiode'
    RUN = 'run'

class BaseElement(ABC):
    def __init__(self, level: DataHolderLevel) -> None:
        self.level = level
        self._df = None
        self._df_pedestals = None
        self._df_full = None
        self.level_header = ""
        self.long_label = ""
        self.dh_parent = None
        self.data_prep_info = {}
        self.time_info = {}

    @property
    @abstractmethod
    def df(self) -> pd.DataFrame:
        """DataFrame containing the data."""

    @property
    @abstractmethod
    def df_pedestals(self) -> pd.DataFrame:
        """DataFrame containing the pedestal data."""

    @property
    @abstractmethod
    def df_full(self) -> pd.DataFrame:
        """DataFrame containing the full data."""

    @abstractmethod
    def analyze(self):
        """Perform the analysis."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert element data to dictionary."""

    def set_time_info(self):
        if self.df is None or self.df.empty:
            self.time_info = {}
            return
        min_time = self.df['timestamp'].min()
        max_time = self.df['timestamp'].max()
        self.time_info = {
            'min_ts': int(min_time),
            'max_ts': int(max_time),
            'elapsed_time_s': int(max_time - min_time),
            'min_dt': pd.to_datetime(min_time, unit='s').strftime('%Y-%m-%d %H:%M:%S'),
            'max_dt': pd.to_datetime(max_time, unit='s').strftime('%Y-%m-%d %H:%M:%S')
        }
