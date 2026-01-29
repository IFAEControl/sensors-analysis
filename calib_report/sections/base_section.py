"""Base class for report sections"""
from abc import ABC, abstractmethod
from base_report.base_report import BaseReport
from ..helpers.data_holders import ReportData

class BaseSection(ABC):
    """Base class for report sections"""

    def __init__(self, report_data: ReportData, report: BaseReport) -> None:
        self.report_data = report_data
        self.report = report
        # depending on the section depth and the build depth requested
        # a section will be added or not
        # to be defined in child classes
        self.section_depth = 4

    def build(self, depth: int = 0):
        """Build the section of the report"""
        if depth == 0 or self.section_depth <= depth:
            self._build(depth)
    
    @abstractmethod
    def _build(self, depth: int):
        """Internal method to build the section of the report"""

    
