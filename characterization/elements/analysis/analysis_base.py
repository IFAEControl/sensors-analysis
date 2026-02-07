from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

from characterization.helpers import get_logger
from ..helpers import MeanStats

logger = get_logger()

class BaseAnal(ABC):
    def __init__(self) -> None:
        self._data_holder = None

    @property
    def df(self) -> pd.DataFrame:
        return self._data_holder.df

    @property
    def df_pedestals(self) -> pd.DataFrame:
        return self._data_holder.df_pedestals

    @property
    def df_full(self) -> pd.DataFrame:
        return self._data_holder.df_full

    @abstractmethod
    def analyze(self):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def get_mean(self, values: np.ndarray) -> MeanStats:
        if values.size == 0:
            return MeanStats(mean=float('nan'), std=float('nan'), samples=0)
        return MeanStats(mean=float(np.nanmean(values)), std=float(np.nanstd(values)), samples=int(np.sum(~np.isnan(values))))
