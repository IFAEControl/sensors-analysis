from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd

from characterization.config import config

class DataHolderLevel(Enum):
    CHARACTERIZATION = 'characterization'
    PHOTODIODE = 'photodiode'
    RUN = 'run'

class BaseElement(ABC):
    VALID_ISSUE_LEVELS = {"warning", "error"}

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
        self.issues: list[dict] = []

    @property
    def ref_pd_col(self) -> str:
        return "ref_pd_zeroed" if config.subtract_pedestals else "ref_pd_mean"

    @property
    def adc_col(self) -> str:
        return "mean_adc_zeroed" if config.subtract_pedestals else "mean_adc"

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

    def add_issue(self, description: str, level: str = "warning", meta: dict | None = None):
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Issue description must be a non-empty string")
        if not isinstance(level, str) or level not in self.VALID_ISSUE_LEVELS:
            raise ValueError(
                f"Invalid issue level '{level}'. Allowed: {sorted(self.VALID_ISSUE_LEVELS)}"
            )
        if meta is None:
            meta = {}
        if not isinstance(meta, dict):
            raise ValueError("Issue meta must be a dict")

        self.issues.append(
            {
                "description": description,
                "level": level,
                "meta": meta,
            }
        )

    def add_issue_error(self, description: str, meta: dict | None = None):
        self.add_issue(description=description, level="error", meta=meta)

    def add_issue_warning(self, description: str, meta: dict | None = None):
        self.add_issue(description=description, level="warning", meta=meta)

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
