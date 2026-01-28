import os
from dataclasses import dataclass

@dataclass
class ReportPaths:
    """Class to hold paths of report"""
    input_file: str
    calib_anal_files_path: str
    report_path: str
    logo_path: str

this_path = os.path.dirname(os.path.abspath(__file__))
default_logo_path = os.path.join(this_path, "logo", "IFAE_logo_SO.png")

def calc_paths(input_path: str, output_path: str|None):
    """Calculate and create necessary paths for reports and outputs."""
    if input_path is None or input_path.strip() == "":
        raise ValueError("Input path must be provided and cannot be empty.")
    if os.path.isdir(input_path):
        calib_anal_files_path = os.path.join(input_path, 'calibration_outputs')
        input_file = os.path.join(input_path, 'calibration_summary.json')
        report_path = input_path
    elif input_path.endswith('.json'):
        input_file = input_path
        calib_anal_files_path = os.path.join(os.path.dirname(input_path), 'calibration_outputs')
        report_path = os.path.dirname(input_path)
    else:
        raise ValueError("Input path must be a directory or a .json file.")
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    if not os.path.exists(calib_anal_files_path):
        raise FileNotFoundError(f"Calibration analysis files path does not exist: {calib_anal_files_path}")
    
    if output_path is None:
        output_path = report_path
    else:
        os.makedirs(output_path, exist_ok=True)        
    report_path = os.path.join(output_path, 'calibration-report.pdf')

    return ReportPaths(
        input_file=input_file,
        calib_anal_files_path=calib_anal_files_path,
        report_path=report_path,
        logo_path=default_logo_path
    )
