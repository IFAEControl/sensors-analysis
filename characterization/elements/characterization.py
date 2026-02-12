"""Characterization top-level element"""
import os
import json
from datetime import datetime, timezone
import pandas as pd
import math

from characterization.helpers import file_manage, get_logger, system_info
from .sweep_file import SweepFile
from .analysis.characterization_analysis import CharacterizationAnalysis
from .plots.characterization_plots import CharacterizationPlots
from .base_element import BaseElement, DataHolderLevel
from .photodiode import Photodiode
from characterization.config import config

logger = get_logger()

class Characterization(BaseElement):
    def __init__(self, call_args):
        super().__init__(DataHolderLevel.CHARACTERIZATION)
        cfpath, output_root, char_folder_path, char_name = file_manage.setup_paths(
            call_args.char_files_path,
            call_args.output_path,
            overwrite=call_args.overwrite
        )
        self.char_files_path = cfpath
        self.reports_path = char_folder_path
        self.output_path = os.path.join(char_folder_path, 'characterization_outputs')
        self.photodiodes: dict[str, Photodiode] = {}
        self.calibration_info: dict = {}
        self.conversion_factors: dict = {}
        self.meta = {
            'calling_arguments': vars(call_args),
            'charact_id': char_name,
            'charact_files_path': cfpath,
            'root_output_path': output_root,
            'characterization_folder_path': char_folder_path,
            'characterization_outputs_path': self.output_path,
            'reports_path': self.reports_path,
            'execution_date': datetime.now(timezone.utc).isoformat(),
            'system': system_info.get_system_info(),
            'config': config.to_dict()
        }
        self.anal = CharacterizationAnalysis(self)
        self.plotter = CharacterizationPlots(self)
        self.level_header = char_name
        self.long_label = char_name
        self.initialize()

    def initialize(self):
        os.makedirs(self.output_path, exist_ok=True)
        self.plot_label = self.level_header

    @property
    def df(self):
        if self._df is None:
            if not self.photodiodes:
                return pd.DataFrame()
            self._df = pd.concat(
                [cf.df for pdh in self.photodiodes.values() for cf in pdh.files if cf.df is not None],
                ignore_index=True
            )
            self._df = self._df.sort_values(by='timestamp').reset_index(drop=True)
            self._df = self._na_adc_columns(self._df)
        return self._df

    @property
    def df_pedestals(self):
        if self._df_pedestals is None:
            if not self.photodiodes:
                return pd.DataFrame()
            self._df_pedestals = pd.concat(
                [cf.df_pedestals for pdh in self.photodiodes.values() for cf in pdh.files if cf.df_pedestals is not None],
                ignore_index=True
            )
            self._df_pedestals = self._df_pedestals.sort_values(by='timestamp').reset_index(drop=True)
            self._df_pedestals = self._na_adc_columns(self._df_pedestals)
        return self._df_pedestals

    @property
    def df_full(self):
        if self._df_full is None:
            if not self.photodiodes:
                return pd.DataFrame()
            self._df_full = pd.concat(
                [cf.df_full for pdh in self.photodiodes.values() for cf in pdh.files if cf.df_full is not None],
                ignore_index=True
            )
            self._df_full = self._df_full.sort_values(by='timestamp').reset_index(drop=True)
            self._df_full = self._na_adc_columns(self._df_full)
        return self._df_full

    @staticmethod
    def _na_adc_columns(df: pd.DataFrame) -> pd.DataFrame:
        adc_cols = ['total_sum', 'total_square_sum', 'total_counts', 'mean_adc', 'std_adc']
        existing = [col for col in adc_cols if col in df.columns]
        if existing:
            df = df.copy()
            df[existing] = pd.NA
        return df

    def load_characterization_files(self):
        for file_name in sorted(os.listdir(self.char_files_path)):
            file_path = os.path.join(self.char_files_path, file_name)
            if os.path.isfile(file_path):
                sweepfile = SweepFile(file_path)
                if sweepfile.valid:
                    self.photodiodes.setdefault(sweepfile.sensor_id, Photodiode(sweepfile.sensor_id, characterization=self)).add_file(sweepfile)
                else:
                    logger.warning("Skipping invalid characterization file: %s", file_name)
                    continue

    def get_output_base_name(self) -> str:
        board_ids = sorted({
            pdh.board_id
            for pdh in self.photodiodes.values()
            if pdh.board_id
        })
        if len(board_ids) == 1:
            return str(board_ids[0])
        if len(board_ids) > 1:
            logger.warning(
                "Multiple board IDs found in characterization (%s). Falling back to charact_id for output names.",
                board_ids
            )
        return self.meta['charact_id']

    def analyze(self):
        os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
        self.set_time_info()

    def generate_plots(self):
        os.makedirs(self.output_path, exist_ok=True)
        pd_plots = self.plotter.plots.setdefault('photodiodes', {})
        for pdh in self.photodiodes.values():
            pdh.generate_plots()
            pd_plots[pdh.level_header] = pdh.plotter.plots
            logger.debug("Generated plots for photodiode %s", pdh.sensor_id)
        self.plotter.generate_plots()

    def to_dict(self):
        out = {
            'meta': self.meta,
            'analysis': self.anal.to_dict(),
            'time_info': self.time_info,
            'plots': self.plotter.plots
        }
        if self.calibration_info:
            out['calibration'] = self.calibration_info
        if self.conversion_factors:
            out['conversion_factors'] = self.conversion_factors
        return out

    def export_data_summary(self, meta: dict | None = None):
        results_path = os.path.join(self.reports_path, config.summary_file_name)
        outdata = self.to_dict()
        if meta:
            outdata.update(meta)
        with open(results_path, 'w', encoding='utf-8') as f:
            try:
                json.dump(outdata, f, indent=2)
            except TypeError as e:
                logger.error("Failed to serialize characterization data to JSON: %s", str(e))
                print(outdata)
        logger.info("Characterization results saved to %s", results_path)

    def export_reduced_summary(self):
        results_path = os.path.join(self.reports_path, f"{self.get_output_base_name()}.json")
        out_photodiodes = {}
        for sensor_id, pdh in self.photodiodes.items():
            out_configs = {}
            for cfg_label, fs in pdh.filesets.items():
                linreg = fs.anal.to_dict().get('linreg_refpd_vs_adc')
                adc_to_power = fs.anal.adc_to_power or {}
                parts = cfg_label.split('_', 1)
                wavelength = parts[0] if parts else cfg_label
                filter_wheel = parts[1] if len(parts) > 1 else ""
                config_key = wavelength
                if config_key in out_configs:
                    logger.warning(
                        "Duplicate wavelength key %s for photodiode %s; using full configuration key %s",
                        config_key,
                        sensor_id,
                        cfg_label
                    )
                    config_key = cfg_label

                adc_to_vref = {'configuration': f"{wavelength} - {filter_wheel}".strip(" -")}
                if isinstance(linreg, dict):
                    adc_to_vref.update(linreg)

                out_configs[config_key] = {
                    'adc_to_power': {
                        'slope': adc_to_power.get('slope'),
                        'intercept': adc_to_power.get('intercept'),
                        'slope_err': adc_to_power.get('slope_err'),
                        'intercept_err': adc_to_power.get('intercept_err'),
                    },
                    'adc_to_vrefV': adc_to_vref,
                }
            out_photodiodes[sensor_id] = out_configs

        reduced_calibration = dict(self.calibration_info)
        reduced_calibration.pop('used_configurations', None)
        reduced_calibration.pop('available_configurations', None)

        outdata = {
            'characterization_id': self.meta['charact_id'],
            'acquisition_time': self.time_info,
            'calibration': reduced_calibration,
            'photodiodes': out_photodiodes
        }
        with open(results_path, 'w', encoding='utf-8') as f:
            try:
                json.dump(outdata, f, indent=2)
            except TypeError as e:
                logger.error("Failed to serialize reduced characterization summary to JSON: %s", str(e))
                print(outdata)
        logger.info("Reduced characterization summary saved to %s", results_path)

    def apply_calibration(self, calibration_json_path: str):
        with open(calibration_json_path, 'r', encoding='utf-8') as f:
            cal_data = json.load(f)

        cal_filesets = self._extract_calibration_filesets(cal_data)
        used_configs = sorted({
            fs.label
            for pdh in self.photodiodes.values()
            for fs in pdh.filesets.values()
        })
        available_configs = sorted(cal_filesets.keys())
        missing = sorted(set(used_configs) - set(available_configs))
        if missing:
            raise ValueError(
                f"Calibration file does not include required characterization configurations: {missing}"
            )

        calibration_meta = cal_data.get('meta', {})
        calibration_execution_date = calibration_meta.get('execution_date')
        if calibration_execution_date is None:
            calibration_execution_date = cal_data.get('time_info', {}).get('min_dt')
        if calibration_execution_date is None:
            calibration_execution_date = cal_data.get('acquisition_time', {}).get('min_dt')
        calibration_power_unit = self._extract_calibration_power_unit(cal_data)
        cal_linreg_by_config = {}
        for cfg in available_configs:
            cal_lr = self._extract_calibration_linreg(cal_filesets.get(cfg))
            if isinstance(cal_lr, dict):
                cal_linreg_by_config[cfg] = cal_lr
        self.calibration_info = {
            'summary_path': calibration_json_path,
            'calibration_id': calibration_meta.get('calib_id', os.path.basename(calibration_json_path)),
            'calibration_execution_date': calibration_execution_date,
            'power_unit': calibration_power_unit,
            'used_configurations': used_configs,
            'available_configurations': available_configs,
            'linreg_by_configuration': cal_linreg_by_config,
        }

        out_conversion = {}
        for sensor_id, pdh in self.photodiodes.items():
            sensor_conv = {}
            for cfg_label, fs in pdh.filesets.items():
                cal_lr = self._extract_calibration_linreg(cal_filesets[cfg_label])
                if cal_lr is None:
                    raise ValueError(f"Missing calibration linear regression for configuration {cfg_label}")
                if fs.anal.lr_refpd_vs_adc.linreg is None:
                    raise ValueError(f"Missing characterization linear regression for sensor {sensor_id}, {cfg_label}")

                conv = self._combine_refpd_adc_with_pm_refpd(fs.anal.lr_refpd_vs_adc.to_dict(), cal_lr)
                conv['configuration'] = cfg_label
                conv['sensor_id'] = sensor_id
                fs.anal.calibration_ref = {
                    'calibration_id': self.calibration_info['calibration_id'],
                    'calibration_execution_date': self.calibration_info['calibration_execution_date'],
                    'power_unit': self.calibration_info['power_unit'],
                    'configuration': cfg_label,
                }
                fs.anal.adc_to_power = conv
                sensor_conv[cfg_label] = conv

            out_conversion[sensor_id] = sensor_conv

        self.conversion_factors = out_conversion
        self.meta['calibration'] = {
            'id': self.calibration_info['calibration_id'],
            'execution_date': self.calibration_info['calibration_execution_date'],
            'power_unit': self.calibration_info['power_unit'],
            'summary_path': self.calibration_info['summary_path'],
            'linreg_by_configuration': self.calibration_info['linreg_by_configuration'],
        }

    @staticmethod
    def _extract_calibration_filesets(cal_data: dict) -> dict:
        if isinstance(cal_data.get('analysis', {}).get('filesets'), dict):
            return cal_data['analysis']['filesets']
        if isinstance(cal_data.get('filesets'), dict):
            return cal_data['filesets']
        raise ValueError("Calibration JSON does not contain filesets information")

    @staticmethod
    def _extract_calibration_linreg(fileset_entry: dict) -> dict | None:
        if not isinstance(fileset_entry, dict):
            return None
        if isinstance(fileset_entry.get('analysis', {}).get('lr_refpd_vs_pm'), dict):
            return fileset_entry['analysis']['lr_refpd_vs_pm']
        if isinstance(fileset_entry.get('full_dataset_linreg'), dict):
            return fileset_entry['full_dataset_linreg']
        if isinstance(fileset_entry.get('lr_refpd_vs_pm'), dict):
            return fileset_entry['lr_refpd_vs_pm']
        return None

    @staticmethod
    def _extract_calibration_power_unit(cal_data: dict) -> str | None:
        # Preferred explicit unit, fallback to config flag.
        unit = cal_data.get('power_unit')
        if isinstance(unit, str) and unit:
            return unit
        use_uW = cal_data.get('meta', {}).get('config', {}).get('use_uW_as_power_units')
        if isinstance(use_uW, bool):
            return 'uW' if use_uW else 'W'
        return None

    @staticmethod
    def _combine_refpd_adc_with_pm_refpd(char_lr: dict, cal_lr: dict) -> dict:
        m_char = float(char_lr['slope'])
        b_char = float(char_lr['intercept'])
        s_m_char = float(char_lr.get('stderr', 0.0))
        s_b_char = float(char_lr.get('intercept_stderr', 0.0))

        m_cal = float(cal_lr['slope'])
        b_cal = float(cal_lr['intercept'])
        s_m_cal = float(cal_lr.get('stderr', 0.0))
        s_b_cal = float(cal_lr.get('intercept_stderr', 0.0))

        slope = m_cal * m_char
        intercept = m_cal * b_char + b_cal

        rel_char = 0.0 if m_char == 0 else s_m_char / abs(m_char)
        rel_cal = 0.0 if m_cal == 0 else s_m_cal / abs(m_cal)
        slope_err = abs(slope) * math.sqrt(rel_char ** 2 + rel_cal ** 2)
        intercept_err = math.sqrt((b_char * s_m_cal) ** 2 + (m_cal * s_b_char) ** 2 + s_b_cal ** 2)

        return {
            # 'model': 'power = slope * adc + intercept',
            'slope': slope,
            'intercept': intercept,
            'slope_err': slope_err,
            'intercept_err': intercept_err,
        }
