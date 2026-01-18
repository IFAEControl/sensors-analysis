
from calibration.elements.calibration import Calibration
from calibration.elements.file_set import FileSet
from calibration.elements.calib_file import CalibFile



class SanityBase:
    def __init__(self, level_instance: Calibration | FileSet | CalibFile):
        self.dh = level_instance
        