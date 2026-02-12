"""
Docstring for calibration.elements.calibration
"""
import os
import json
import re
from datetime import datetime, timezone
import pandas as pd

from calibration.helpers import file_manage, get_logger, system_info
from .calib_file import CalibFile
from .analysis import CalibrationAnalysis
from .plots.calibration_plots import CalibrationPlots
from .calib_fileset import FileSet
from .base_element import BaseElement, DataHolderLevel
from calibration.config import config

logger = get_logger()
        

class Calibration(BaseElement):
    """
    Docstring for Calibration
    """
    def __init__(self, call_args):
        super().__init__(DataHolderLevel.CALIBRATION)
        cfpath, opath, calib_name =  file_manage.setup_paths(call_args.calib_files_path, call_args.output_path,
                                               overwrite=call_args.overwrite)
        self.root_output_path = call_args.output_path if call_args.output_path else './output/'
        self.calib_files_path = cfpath
        self.reports_path = opath
        self.plots_path = os.path.join(opath, 'plots')
        self.filesets = {}
        self.meta = {
            'calling_arguments': vars(call_args),
            'calib_id': calib_name,
            'calib_files_path': cfpath,
            'root_output_path': self.root_output_path,
            'calibration_output_path': opath,
            'calibration_plots_path': self.plots_path,
            'reports_path': self.reports_path,
            'execution_date': datetime.now(timezone.utc).isoformat(),
            'system': system_info.get_system_info(),
            'config': config.to_dict()
        }
        self.anal = CalibrationAnalysis(self)
        self.plotter = CalibrationPlots(self)
        self.level_header = calib_name
        self.long_label = calib_name
        self.past_calibrations: dict[str, dict] = {}
        self.initialize()
    
    def initialize(self):
        os.makedirs(self.plots_path, exist_ok=True)
        self._load_past_calibrations()

    def _load_past_calibrations(self):
        """Load previously exported reduced calibration json files from output root."""
        output_root = self.root_output_path
        file_pattern = re.compile(r"^calibration_\d{8}\.json$")
        past_calibrations: dict[str, dict] = {}
        try:
            for fname in sorted(os.listdir(output_root)):
                if not file_pattern.match(fname):
                    continue
                fpath = os.path.join(output_root, fname)
                if not os.path.isfile(fpath):
                    continue
                key = os.path.splitext(fname)[0]
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        past_calibrations[key] = json.load(f)
                except Exception as e:
                    logger.warning("Skipping past calibration file %s: %s", fpath, str(e))
        except Exception as e:
            logger.warning("Failed to scan output root for past calibrations at %s: %s", output_root, str(e))
        self.past_calibrations = past_calibrations
   
    @property
    def df(self):
        """Concatenated DataFrame of all calibration files."""
        if self._df is None:
            self._df = pd.concat(
                [calfile.df for fileset in self.filesets.values() for calfile in fileset.files if calfile.df is not None], ignore_index=True)
            self._df = self._df.sort_values(by='timestamp').reset_index(drop=True)
        return self._df
    
    @property
    def df_pedestals(self):
        """Concatenated DataFrame of all pedestal data."""
        if self._df_pedestals is None:
            self._df_pedestals = pd.concat(
                [fileset.df_pedestals for fileset in self.filesets.values() if fileset.df_pedestals is not None], ignore_index=True)
            self._df_pedestals = self._df_pedestals.sort_values(by='timestamp').reset_index(drop=True)
        return self._df_pedestals
    
    @property
    def df_full(self):
        """Concatenated DataFrame of all full data."""
        if self._df_full is None:
            self._df_full = pd.concat(
                [fileset.df_full for fileset in self.filesets.values() if fileset.df_full is not None], ignore_index=True)
            self._df_full = self._df_full.sort_values(by='timestamp').reset_index(drop=True)
        return self._df_full


    def load_calibration_files(self):
        """
        Load calibration files from the specified directory or zip file

        Files are grouped into sets based on their wavelength and filter wheel settings
        
        """
        # sorted makes sure that the files are loaded in a consistent order (run1, run2, run3)
        for file_name in sorted(os.listdir(self.calib_files_path)):
            file_path = os.path.join(self.calib_files_path, file_name)
            if os.path.isfile(file_path):
                # File set itself is the responsible to set the fileset in the calib file
                # On creation of the CalibFile object the file is loaded to a DataFrame (if valid)
                calfile = CalibFile(file_path)
                if calfile.valid:
                    self.filesets.setdefault((calfile.wavelength, calfile.filter_wheel), FileSet(calfile.wavelength, calfile.filter_wheel, calibration=self)).add_calib_file(calfile)
                else:
                    logger.warning("Skipping invalid calibration file: %s", file_name)
                    continue
                # logger.info("Loaded calibration file: %s", file_name)
    
    def analyze(self):
        """Analyze the calibration data"""
        os.makedirs(self.plots_path, exist_ok=True)
        self.anal.analyze()
        self.set_time_info()
    
    def generate_plots(self):
        """Generate calibration plots"""
        os.makedirs(self.plots_path, exist_ok=True)
        fs_plots = self.plotter.plots.setdefault('filesets', {})
        for fileset in self.filesets.values():
            fileset.generate_plots()
            fs_plots[fileset.level_header] = fileset.plotter.plots
        self.plotter.generate_plots()
    
    def to_dict(self):
        """Convert calibration data to dictionary"""

        return {
            'meta': self.meta,
            'analysis': self.anal.to_dict(),
            'time_info': self.time_info,
            'plots': self.plotter.plots
        }

    def export_calib_data_summary(self, meta={}):
        results_path = os.path.join(self.reports_path, config.summary_file_name)
        outdata = self.to_dict()
        if meta:
            outdata.update(meta)
        with open(results_path, 'w', encoding='utf-8') as f:
            try:
                json.dump(outdata, f, indent=2)
            except TypeError as e:
                logger.error("Failed to serialize calibration data to JSON: %s", str(e))
                print(outdata)
        logger.info("Calibration results saved to %s", results_path)

    def export_reduced_summary(self):
        results_path = os.path.join(self.reports_path, f"{self.meta['calib_id']}.json")
        filesets = {}
        for fileset in self.filesets.values():
            linreg = fileset.anal.results.get('lr_refpd_vs_pm')
            pedestals = fileset.anal.results.get('pedestals')
            filesets[fileset.level_header] = {
                'full_dataset_linreg': linreg,
                'pedestals': pedestals
            }
        outdata = {
            'acquisition_time': self.time_info,
            'power_unit': self.power_units,
            'filesets': filesets
        }
        with open(results_path, 'w', encoding='utf-8') as f:
            try:
                json.dump(outdata, f, indent=2)
            except TypeError as e:
                logger.error("Failed to serialize reduced calibration summary to JSON: %s", str(e))
                print(outdata)
        logger.info("Reduced calibration summary saved to %s", results_path)
    

#-------------------------------------

 
    # def get_temperature_data(self):
    #     temp_data = pd.DataFrame()
    #     for calfile in self.calib_files:
    #         temp_data = pd.concat([temp_data, calfile.df[['datetime', 'temperature']].copy()])
    #     return temp_data
    
    # def get_humidity_data(self):
    #     humidity_data = pd.DataFrame()
    #     for calfile in self.calib_files:
    #         humidity_data = pd.concat([humidity_data, calfile.df[['datetime', 'RH']].copy()])
    #     return humidity_data
