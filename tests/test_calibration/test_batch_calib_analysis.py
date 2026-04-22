from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from calibration.batch_calib_analysis import _build_calibration_command, _collect_dated_files, _publish_reduced_summary


class _Args:
    def __init__(self) -> None:
        self.output_folder = Path("calib-reports")
        self.plot_format = "png"
        self.log_file = True
        self.no_plots = True
        self.no_gen_report = True
        self.zip_it = True
        self.do_not_sub_pedestals = True
        self.do_not_replace_zero_pm_stds = True
        self.use_first_ped_in_linreag = True
        self.use_W_as_power_units = True


class TestBatchCalibrationAnalysis(unittest.TestCase):
    def test_collect_dated_files_sorts_by_date_and_skips_invalid_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "calibration_21012026.zip").write_text("", encoding="utf-8")
            (root / "calibration_01012026.zip").write_text("", encoding="utf-8")
            (root / "invalid_name.zip").write_text("", encoding="utf-8")

            collected = _collect_dated_files(root, "*.zip")

        self.assertEqual(
            [item.path.name for item in collected],
            ["calibration_01012026.zip", "calibration_21012026.zip"],
        )

    def test_build_calibration_command_maps_batch_flags(self) -> None:
        args = _Args()

        command = _build_calibration_command(args, Path("calibration_21012026.zip"))

        self.assertEqual(command[:5], [command[0], "-m", "calibration.main", "calibration_21012026.zip", "-o"])
        self.assertIn("calib-reports", command)
        self.assertIn("-w", command)
        self.assertIn("-f", command)
        self.assertIn("png", command)
        self.assertIn("-n", command)
        self.assertIn("--no-gen-report", command)
        self.assertIn("-z", command)
        self.assertIn("-l", command)
        self.assertIn("-d", command)
        self.assertIn("-s", command)
        self.assertIn("-p", command)
        self.assertIn("-u", command)

    def test_publish_reduced_summary_copies_json_to_output_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_root = Path(tmp_dir)
            reports_dir = output_root / "calibration_21012026"
            reports_dir.mkdir()
            source = reports_dir / "calibration_21012026.json"
            source.write_text('{"ok": true}', encoding="utf-8")

            destination = _publish_reduced_summary(output_root, Path("calibration_21012026.zip"))

            self.assertEqual(destination, output_root / "calibration_21012026.json")
            self.assertTrue(destination.exists())
            self.assertEqual(destination.read_text(encoding="utf-8"), '{"ok": true}')


if __name__ == "__main__":
    unittest.main()
