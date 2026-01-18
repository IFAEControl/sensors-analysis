"""
Docstring for calibration.elements.calibration
"""
import os
import json
from datetime import datetime, timezone

import pandas as pd
import matplotlib.pyplot as plt

from calibration.helpers import file_manage, get_logger, system_info
from .calib_file import CalibFile
from .calibration_analysis import CalibrationAnalysis
from .sets import FileSet
logger = get_logger()

        

class Calibration:
    """
    Docstring for Calibration
    """
    def __init__(self, call_args):
        cfpath, opath =  file_manage.setup_paths(call_args.calib_files_path, call_args.output_path,
                                               overwrite=call_args.overwrite)
        self.calib_files_path = cfpath
        self.output_path = opath
        self.file_sets = {}
        self.meta = {
            'calling_arguments': vars(call_args),
            'calib_files_path': cfpath,
            'output_path': opath,
            'execution_date': datetime.now(timezone.utc).isoformat(),
            'system': system_info.get_system_info()
        }
        self.anal = CalibrationAnalysis(self)

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
                    self.file_sets.setdefault((calfile.wavelength, calfile.filter_wheel), FileSet(calfile.wavelength, calfile.filter_wheel, calibration=self)).add_calib_file(calfile)
                else:
                    logger.warning("Skipping invalid calibration file: %s", file_name)
                    continue
                logger.info("Loaded calibration file: %s", file_name)
    
    def analyze(self):
        """Analyze the calibration data"""
        os.makedirs(self.output_path, exist_ok=True)
        self.anal.analyze()
    
    def to_dict(self):
        """Convert calibration data to dictionary"""
        return {
            'meta': self.meta,
            'file_sets': {f"{wl}_{fw}": fs.to_dict() for (wl, fw), fs in self.file_sets.items()}
        }

    def export_calib_data_summary(self):
        results_path = os.path.join(self.output_path, "calibration_summary.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info("Calibration results saved to %s", results_path)
    
    
#-------------------------------------

 
    # def get_temperature_data(self):
    #     temp_data = pd.DataFrame()
    #     for calfile in self.calib_files:
    #         temp_data = pd.concat([temp_data, calfile.df[['datetime', 'Temp']].copy()])
    #     return temp_data
    
    # def get_humidity_data(self):
    #     humidity_data = pd.DataFrame()
    #     for calfile in self.calib_files:
    #         humidity_data = pd.concat([humidity_data, calfile.df[['datetime', 'RH']].copy()])
    #     return humidity_data

