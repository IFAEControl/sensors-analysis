from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch
import pandas as pd

from characterization.config import config
from characterization.elements.analysis.analysis_base import BaseAnal
from characterization.elements.analysis.characterization_analysis import CharacterizationAnalysis
from characterization.elements.analysis.fileset_analysis import FilesetAnalysis


class TestSubtractionModeColumns(unittest.TestCase):
    def test_uses_zeroed_columns_when_subtract_enabled(self):
        with patch.object(config, "subtract_pedestals", True):
            anal = FilesetAnalysis(SimpleNamespace(label="1064_FW5"))
        self.assertEqual(anal.lr_refpd_vs_adc.x_var, "mean_adc_zeroed")
        self.assertEqual(anal.lr_refpd_vs_adc.y_var, "ref_pd_zeroed")

    def test_uses_raw_columns_when_subtract_disabled(self):
        with patch.object(config, "subtract_pedestals", False):
            anal = FilesetAnalysis(SimpleNamespace(label="1064_FW5"))
        self.assertEqual(anal.lr_refpd_vs_adc.x_var, "mean_adc")
        self.assertEqual(anal.lr_refpd_vs_adc.y_var, "ref_pd_mean")

    def test_pedestal_stats_use_raw_columns_and_include_weighted_mean(self):
        class _DummyAnal(BaseAnal):
            def analyze(self):
                return None

            def to_dict(self):
                return {}

        df_ped = pd.DataFrame(
            {
                "mean_adc": [10.0, 20.0],
                "std_adc": [1.0, 2.0],
                "ref_pd_mean": [1.0, 3.0],
                "ref_pd_std": [0.5, 1.0],
                "mean_adc_zeroed": [0.0, 0.0],
                "ref_pd_zeroed": [0.0, 0.0],
            }
        )
        holder = SimpleNamespace(
            df_pedestals=df_ped,
            df=df_ped,
            df_full=df_ped,
            df_sat=df_ped.iloc[0:0],
            adc_col="mean_adc_zeroed",
            ref_pd_col="ref_pd_zeroed",
        )
        anal = _DummyAnal()
        anal._data_holder = holder
        stats = anal._calc_pedestal_stats()
        self.assertIn("mean_adc", stats)
        self.assertIn("ref_pd_mean", stats)
        self.assertIn("w_mean", stats["mean_adc"])
        self.assertIn("w_mean", stats["ref_pd_mean"])
        self.assertTrue(stats["mean_adc"]["weighted"])
        self.assertFalse(stats["mean_adc"]["exec_error"])
        self.assertTrue(stats["ref_pd_mean"]["weighted"])
        self.assertFalse(stats["ref_pd_mean"]["exec_error"])
        self.assertNotEqual(stats["mean_adc"]["w_mean"], 0.0)
        self.assertNotEqual(stats["ref_pd_mean"]["w_mean"], 0.0)

    def test_pedestal_weighted_flags_mark_failure_when_not_enough_valid_std(self):
        class _DummyAnal(BaseAnal):
            def analyze(self):
                return None

            def to_dict(self):
                return {}

        df_ped = pd.DataFrame(
            {
                "mean_adc": [10.0],
                "std_adc": [0.0],
                "ref_pd_mean": [1.0],
                "ref_pd_std": [0.0],
            }
        )
        holder = SimpleNamespace(
            df_pedestals=df_ped,
            df=df_ped,
            df_full=df_ped,
            df_sat=df_ped.iloc[0:0],
            adc_col="mean_adc",
            ref_pd_col="ref_pd_mean",
        )
        anal = _DummyAnal()
        anal._data_holder = holder
        stats = anal._calc_pedestal_stats()
        self.assertFalse(stats["mean_adc"]["weighted"])
        self.assertTrue(stats["mean_adc"]["exec_error"])
        self.assertFalse(stats["ref_pd_mean"]["weighted"])
        self.assertTrue(stats["ref_pd_mean"]["exec_error"])

    def test_characterization_pedestal_stats_use_base_method_structure(self):
        ped = pd.DataFrame(
            {
                "ref_pd_mean": [1.0, 3.0],
                "ref_pd_std": [0.5, 1.0],
            }
        )
        char = SimpleNamespace(df_pedestals=ped, photodiodes={})
        anal = CharacterizationAnalysis(char)
        anal._calc_refpd_pedestal_stats()
        stats = anal.results["pedestal_stats"]["ref_pd_mean"]
        self.assertIn("weighted", stats)
        self.assertIn("w_mean", stats)
        self.assertIn("exec_error", stats)
        self.assertTrue(stats["weighted"])


if __name__ == "__main__":
    unittest.main()
